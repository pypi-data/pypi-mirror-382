import datetime
from enum import Enum
import warnings
import certifi
import threading
import time

import zuora_sdk
from zuora_sdk import *

# Suppress all warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


class ZuoraEnvironment(Enum):
    SBX = "https://rest.apisandbox.zuora.com"
    SBX_NA = "https://rest.sandbox.na.zuora.com"
    SBX_EU = "https://rest.sandbox.eu.zuora.com"
    CSBX = "https://rest.test.zuora.com"
    CSBX_EU = "https://rest.test.eu.zuora.com"
    CSBX_AP = "https://rest.test.ap.zuora.com"
    PROD = "https://rest.zuora.com"
    PROD_NA = "https://rest.na.zuora.com"
    PROD_EU = "https://rest.eu.zuora.com"
    PROD_AP = "https://rest.ap.zuora.com"


class ZuoraClient:
    def __init__(self, client_id: str, client_secret: str, env: ZuoraEnvironment, config: Configuration = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.env = env

        if config is None:
            self.configuration = zuora_sdk.Configuration()
            self.configuration.ssl_ca_cert = certifi.where()
        else:
            self.configuration: Configuration = config
        if self.env is not None:
            self.configuration.host = self.env.value
        self.api_client = ApiClient(self.configuration)
        self.token = {'access_token': None, 'expires_at': datetime.datetime.now()}
        
        # Auto-auth related attributes
        self._refresh_timer = None
        self._refresh_interval = 10 * 60  # 10 minutes in seconds
        self._stop_refresh = threading.Event()
        self._refresh_lock = threading.Lock()
        self._token_lock = threading.RLock()  # Reentrant lock for token operations
        self._config_lock = threading.Lock()  # Lock for configuration changes
        
        # Retry configuration
        self._max_retries = 3
        self._retry_base_delay = 1  # 1 second base delay

    def initialize(self):
        """
        Initialize the client with auto-auth functionality.
        This method performs initial authentication and sets up automatic token refresh.
        """
        with self._refresh_lock:
            if self._refresh_timer is not None:
                return  # Already initialized
        
        # Perform initial authentication
        self._auth()
        
        # Start the refresh timer
        self._start_refresh_timer()
    
    def _auth(self):
        """
        Internal method to fetch a new bearer token and update the API client.
        Thread-safe implementation using a single lock for the entire operation.
        
        Locking Strategy:
        - The entire method is wrapped in _token_lock to ensure atomicity
        - This prevents race conditions between API calls and token updates
        - While this blocks other token operations during refresh, it's necessary
          to maintain consistency and prevent partial token states
        - The lock duration is minimal (just the API call + token update)
        """
        with self._token_lock:
            # Retry logic with exponential backoff
            for attempt in range(1, self._max_retries + 1):
                try:
                    # Fetch new token from Zuora OAuth API
                    ret: TokenResponse = OAuthApi(self.api_client).create_token(
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                        grant_type='client_credentials'
                    )
                    
                    # Atomic token update - all token-related changes happen together
                    self.token['access_token'] = ret.access_token
                    self.token['expires_at'] = datetime.datetime.now() + datetime.timedelta(seconds=ret.expires_in)
                    # Update API client headers atomically with token
                    self.api_client.default_headers['Authorization'] = 'Bearer ' + ret.access_token
                    
                    # Success - break out of retry loop
                    break
                    
                except Exception as e:
                    print(f"Authentication attempt {attempt} failed: {e}")
                    
                    # If this is the last attempt, log final failure
                    if attempt == self._max_retries:
                        print(f"All {self._max_retries} authentication attempts failed. Last error: {e}")
                        # Don't re-raise - let the application continue with expired token
                    else:
                        # Calculate delay with exponential backoff: 1s, 2s, 4s
                        delay = self._retry_base_delay * (2 ** (attempt - 1))
                        print(f"Retrying authentication in {delay} seconds...")
                        time.sleep(delay)
    
    def _start_refresh_timer(self):
        """
        Start the background thread for automatic token refresh.
        Thread-safe implementation.
        """
        def refresh_worker():
            while not self._stop_refresh.is_set():
                try:
                    # Get current refresh interval thread-safely
                    with self._config_lock:
                        current_interval = self._refresh_interval
                    
                    time.sleep(current_interval)
                    if not self._stop_refresh.is_set():
                        self._auth()
                except Exception as e:
                    print(f"Error in refresh worker: {e}")
                    # Continue trying even if there's an error
        
        self._refresh_timer = threading.Thread(target=refresh_worker, daemon=True)
        self._refresh_timer.start()
    
    def stop_auto_auth(self):
        """
        Stop the automatic token refresh.
        """
        with self._refresh_lock:
            if self._refresh_timer is not None:
                self._stop_refresh.set()
                self._refresh_timer.join(timeout=5)  # Wait up to 5 seconds
                self._refresh_timer = None
    
    def set_refresh_interval(self, interval_seconds: int):
        """
        Set the token refresh interval in seconds.
        Thread-safe implementation.
        
        :param interval_seconds: Refresh interval in seconds (minimum 60 seconds recommended)
        """
        if interval_seconds < 60:
            raise ValueError("Refresh interval must be at least 60 seconds")
        
        with self._config_lock:
            self._refresh_interval = interval_seconds
    
    def get_refresh_interval(self) -> int:
        """
        Get the current token refresh interval in seconds.
        Thread-safe implementation.
        
        :return: Current refresh interval in seconds
        """
        with self._config_lock:
            return self._refresh_interval
    
    def set_retry_config(self, max_retries: int, retry_base_delay: int):
        """
        Set the retry configuration for authentication failures.
        Thread-safe implementation.
        
        :param max_retries: Maximum number of retry attempts (1-10)
        :param retry_base_delay: Base delay in seconds for exponential backoff (1-30)
        """
        if max_retries < 1 or max_retries > 10:
            raise ValueError("max_retries must be between 1 and 10")
        if retry_base_delay < 1 or retry_base_delay > 30:
            raise ValueError("retry_base_delay must be between 1 and 30 seconds")
        
        with self._config_lock:
            self._max_retries = max_retries
            self._retry_base_delay = retry_base_delay
    
    def get_retry_config(self) -> dict:
        """
        Get the current retry configuration.
        Thread-safe implementation.
        
        :return: Dictionary containing retry configuration
        """
        with self._config_lock:
            return {
                'max_retries': self._max_retries,
                'retry_base_delay': self._retry_base_delay
            }
    
    def is_token_expired(self) -> bool:
        """
        Check if the current token is expired.
        Thread-safe implementation.
        
        :return: True if token is expired, False otherwise
        """
        with self._token_lock:
            return datetime.datetime.now() >= self.token['expires_at']
    
    def refresh_token(self):
        """
        Manually refresh the bearer token.
        Thread-safe implementation - delegates to _auth() which handles locking.
        """
        self._auth()  # _auth() handles its own locking
    
    def get_token_info(self) -> dict:
        """
        Get information about the current token.
        Thread-safe implementation.
        
        :return: Dictionary containing token information
        """
        with self._token_lock:
            with self._config_lock:
                return {
                    'access_token': self.token['access_token'][:10] + '...' if self.token['access_token'] else None,
                    'expires_at': self.token['expires_at'],
                    'is_expired': datetime.datetime.now() >= self.token['expires_at'],
                    'refresh_interval': self._refresh_interval,
                    'auto_auth_active': self._refresh_timer is not None,
                    'retry_config': {
                        'max_retries': self._max_retries,
                        'retry_base_delay': self._retry_base_delay
                    }
                }
    
    def is_thread_safe(self) -> bool:
        """
        Check if the client is configured for thread safety.
        
        :return: True if thread safety measures are in place
        """
        return (hasattr(self, '_token_lock') and 
                hasattr(self, '_config_lock') and 
                hasattr(self, '_refresh_lock'))
    
    def get_thread_info(self) -> dict:
        """
        Get information about the current threading state.
        Useful for debugging multi-threaded issues.
        
        :return: Dictionary containing threading information
        """
        import threading as th
        return {
            'current_thread': th.current_thread().name,
            'active_threads': th.active_count(),
            'token_lock_locked': self._token_lock._locked if hasattr(self._token_lock, '_locked') else 'Unknown',
            'config_lock_locked': self._config_lock._locked if hasattr(self._config_lock, '_locked') else 'Unknown',
            'refresh_lock_locked': self._refresh_lock._locked if hasattr(self._refresh_lock, '_locked') else 'Unknown',
            'refresh_thread_alive': self._refresh_timer.is_alive() if self._refresh_timer else False,
            'stop_refresh_set': self._stop_refresh.is_set()
        }
    
    def __del__(self):
        """
        Destructor to ensure auto-auth thread is properly cleaned up.
        """
        self.stop_auto_auth()

    def set_base_url(self, base_url: str):
        self.api_client.configuration.host = base_url

    def set_zuora_version(self, version: str):
        self.api_client.set_default_header('Zuora-Version', version)

    def get_zuora_version(self, default_version):
        return self.api_client.default_headers.get('Zuora-Version', default_version)

    def add_default_header(self, key: str, value: str):
        self.api_client.set_default_header(key, value)

    def get_default_headers(self) -> dict:
        return self.api_client.default_headers

    def set_entity_id(self, entity_id: str):
        self.api_client.set_default_header('Zuora-Entity-Ids', entity_id)

    def get_entity_id(self) -> str:
        return self.api_client.default_headers.get('Zuora-Entity-Ids')

    def set_debug(self, debug: bool):
        self.configuration.debug = debug

    def set_accept_encoding(self, accept_encoding: str):
        self.api_client.set_default_header('Accept-Encoding', accept_encoding)

    def get_accept_encoding(self):
        return self.api_client.default_headers.get('Accept-Encoding')

    def set_request_timeout(self, request_timeout):
        """
        :param request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        """
        self.api_client.request_timeout = request_timeout

    def get_request_timeout(self):
        return self.api_client.request_timeout

    def api_health_api(self) -> APIHealthApi:
        return APIHealthApi(self.api_client)

    def accounting_codes_api(self) -> AccountingCodesApi:
        return AccountingCodesApi(self.api_client)

    def accounting_periods_api(self) -> AccountingPeriodsApi:
        return AccountingPeriodsApi(self.api_client)

    def accounts_api(self) -> AccountsApi:
        return AccountsApi(self.api_client)

    def actions_api(self) -> ActionsApi:
        return ActionsApi(self.api_client)

    def adjustments_api(self) -> AdjustmentsApi:
        return AdjustmentsApi(self.api_client)

    def aggregate_queries_api(self) -> AggregateQueriesApi:
        return AggregateQueriesApi(self.api_client)

    def attachments_api(self) -> AttachmentsApi:
        return AttachmentsApi(self.api_client)

    def bill_run_api(self) -> BillRunApi:
        return BillRunApi(self.api_client)

    def bill_run_health_api(self) -> BillRunHealthApi:
        return BillRunHealthApi(self.api_client)

    def billing_documents_api(self) -> BillingDocumentsApi:
        return BillingDocumentsApi(self.api_client)

    def billing_preview_run_api(self) -> BillingPreviewRunApi:
        return BillingPreviewRunApi(self.api_client)

    def booking_date_backfill_job_api(self) -> BookingDateBackfillJobApi:
        return BookingDateBackfillJobApi(self.api_client)

    def catalog_groups_api(self) -> CatalogGroupsApi:
        return CatalogGroupsApi(self.api_client)

    def contact_snapshots_api(self) -> ContactSnapshotsApi:
        return ContactSnapshotsApi(self.api_client)

    def contacts_api(self) -> ContactsApi:
        return ContactsApi(self.api_client)

    def credit_memos_api(self) -> CreditMemosApi:
        return CreditMemosApi(self.api_client)

    def custom_event_triggers_api(self) -> CustomEventTriggersApi:
        return CustomEventTriggersApi(self.api_client)

    def custom_exchange_rates_api(self) -> CustomExchangeRatesApi:
        return CustomExchangeRatesApi(self.api_client)

    def custom_object_definitions_api(self) -> CustomObjectDefinitionsApi:
        return CustomObjectDefinitionsApi(self.api_client)

    def custom_object_jobs_api(self) -> CustomObjectJobsApi:
        return CustomObjectJobsApi(self.api_client)

    def custom_object_records_api(self) -> CustomObjectRecordsApi:
        return CustomObjectRecordsApi(self.api_client)

    def custom_payment_method_types_api(self) -> CustomPaymentMethodTypesApi:
        return CustomPaymentMethodTypesApi(self.api_client)

    def custom_scheduled_events_api(self) -> CustomScheduledEventsApi:
        return CustomScheduledEventsApi(self.api_client)

    def data_backfill_job_api(self) -> DataBackfillJobApi:
        return DataBackfillJobApi(self.api_client)

    def data_labeling_api(self) -> DataLabelingApi:
        return DataLabelingApi(self.api_client)

    def data_queries_api(self) -> DataQueriesApi:
        return DataQueriesApi(self.api_client)

    def debit_memos_api(self) -> DebitMemosApi:
        return DebitMemosApi(self.api_client)

    def deployment_api(self) -> DeploymentApi:
        return DeploymentApi(self.api_client)

    def deployment_configuration_templates_api(self) -> DeploymentConfigurationTemplatesApi:
        return DeploymentConfigurationTemplatesApi(self.api_client)

    def describe_api(self) -> DescribeApi:
        return DescribeApi(self.api_client)

    def e_invoicing_api(self) -> EInvoicingApi:
        return EInvoicingApi(self.api_client)

    def electronic_payments_health_api(self) -> ElectronicPaymentsHealthApi:
        return ElectronicPaymentsHealthApi(self.api_client)

    def files_api(self) -> FilesApi:
        return FilesApi(self.api_client)

    def fulfillments_api(self) -> FulfillmentsApi:
        return FulfillmentsApi(self.api_client)

    def hosted_pages_api(self) -> HostedPagesApi:
        return HostedPagesApi(self.api_client)

    def imports_api(self) -> ImportsApi:
        return ImportsApi(self.api_client)

    def invoice_schedules_api(self) -> InvoiceSchedulesApi:
        return InvoiceSchedulesApi(self.api_client)

    def invoices_api(self) -> InvoicesApi:
        return InvoicesApi(self.api_client)

    def journal_runs_api(self) -> JournalRunsApi:
        return JournalRunsApi(self.api_client)

    def mass_updater_api(self) -> MassUpdaterApi:
        return MassUpdaterApi(self.api_client)

    def notifications_api(self) -> NotificationsApi:
        return NotificationsApi(self.api_client)

    def o_auth_api(self) -> OAuthApi:
        return OAuthApi(self.api_client)

    def object_queries_api(self) -> ObjectQueriesApi:
        return ObjectQueriesApi(self.api_client)

    def omni_channel_subscriptions_api(self) -> OmniChannelSubscriptionsApi:
        return OmniChannelSubscriptionsApi(self.api_client)

    def omni_channel_subscriptions_api(self) -> OmniChannelSubscriptionsApi:
        return OmniChannelSubscriptionsApi(self.api_client)

    def operations_api(self) -> OperationsApi:
        return OperationsApi(self.api_client)

    def order_actions_api(self) -> OrderActionsApi:
        return OrderActionsApi(self.api_client)

    def order_line_items_api(self) -> OrderLineItemsApi:
        return OrderLineItemsApi(self.api_client)

    def orders_api(self) -> OrdersApi:
        return OrdersApi(self.api_client)

    def payment_authorization_api(self) -> PaymentAuthorizationApi:
        return PaymentAuthorizationApi(self.api_client)

    def payment_gateway_reconciliation_api(self) -> PaymentGatewayReconciliationApi:
        return PaymentGatewayReconciliationApi(self.api_client)

    def payment_gateways_api(self) -> PaymentGatewaysApi:
        return PaymentGatewaysApi(self.api_client)

    def payment_method_snapshots_api(self) -> PaymentMethodSnapshotsApi:
        return PaymentMethodSnapshotsApi(self.api_client)

    def payment_method_transaction_logs_api(self) -> PaymentMethodTransactionLogsApi:
        return PaymentMethodTransactionLogsApi(self.api_client)

    def payment_method_updater_api(self) -> PaymentMethodUpdaterApi:
        return PaymentMethodUpdaterApi(self.api_client)

    def payment_methods_api(self) -> PaymentMethodsApi:
        return PaymentMethodsApi(self.api_client)

    def payment_runs_api(self) -> PaymentRunsApi:
        return PaymentRunsApi(self.api_client)

    def payment_schedules_api(self) -> PaymentSchedulesApi:
        return PaymentSchedulesApi(self.api_client)

    def payment_transaction_logs_api(self) -> PaymentTransactionLogsApi:
        return PaymentTransactionLogsApi(self.api_client)

    def payments_api(self) -> PaymentsApi:
        return PaymentsApi(self.api_client)

    def product_rate_plan_charge_tiers_api(self) -> ProductRatePlanChargeTiersApi:
        return ProductRatePlanChargeTiersApi(self.api_client)

    def product_rate_plan_charges_api(self) -> ProductRatePlanChargesApi:
        return ProductRatePlanChargesApi(self.api_client)

    def product_rate_plans_api(self) -> ProductRatePlansApi:
        return ProductRatePlansApi(self.api_client)

    def products_api(self) -> ProductsApi:
        return ProductsApi(self.api_client)

    def rsa_signatures_api(self) -> RSASignaturesApi:
        return RSASignaturesApi(self.api_client)

    def ramps_api(self) -> RampsApi:
        return RampsApi(self.api_client)

    def rate_plans_api(self) -> RatePlansApi:
        return RatePlansApi(self.api_client)

    def refunds_api(self) -> RefundsApi:
        return RefundsApi(self.api_client)

    def regenerate_api(self) -> RegenerateApi:
        return RegenerateApi(self.api_client)

    def revenue_integration_api(self) -> RevenueIntegrationApi:
        return RevenueIntegrationApi(self.api_client)

    def revenue_accounting_codes_api(self) -> RevenueAccountingCodesApi:
        return RevenueAccountingCodesApi(self.api_client)

    def sequence_sets_api(self) -> SequenceSetsApi:
        return SequenceSetsApi(self.api_client)

    def settings_api(self) -> SettingsApi:
        return SettingsApi(self.api_client)

    def sign_up_api(self) -> SignUpApi:
        return SignUpApi(self.api_client)

    def subscription_change_logs_api(self) -> SubscriptionChangeLogsApi:
        return SubscriptionChangeLogsApi(self.api_client)

    def subscriptions_api(self) -> SubscriptionsApi:
        return SubscriptionsApi(self.api_client)

    def summary_journal_entries_api(self) -> SummaryJournalEntriesApi:
        return SummaryJournalEntriesApi(self.api_client)

    def taxation_items_api(self) -> TaxationItemsApi:
        return TaxationItemsApi(self.api_client)

    def usage_api(self) -> UsageApi:
        return UsageApi(self.api_client)

    def workflows_api(self) -> WorkflowsApi:
        return WorkflowsApi(self.api_client)

