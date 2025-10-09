# CreatePaymentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account that the payment is created for.  | [optional] 
**account_number** | **str** | The number of the customer account that the payment is created for, such as &#x60;A00000001&#x60;.   You can specify either &#x60;accountNumber&#x60; or &#x60;accountId&#x60; for a customer account. If both of them are specified, they must refer to the same customer account. | [optional] 
**amount** | **float** | The total amount of the payment.  | 
**auth_transaction_id** | **str** | The authorization transaction ID from the payment gateway. Use this field for electronic payments, such as credit cards.   When you create a payment for capturing the authorized funds, it is highly recommended to pass in the gatewayOrderId that you used when authorizing the funds by using the [Create authorization](https://www.zuora.com/developer/api-references/api/operation/Post_CreateAuthorization) operation, together with the &#x60;authTransactionId&#x60; field.   The following payment gateways support this field:   - Adyen Integration v2.0   - CyberSource 1.28   - CyberSource 1.97   - CyberSource 2.0   - Chase Paymentech Orbital   - Ingenico ePayments   - SlimPay   - Stripe v2   - Verifi Global Payment Gateway   - WePay Payment Gateway Integration | [optional] 
**comment** | **str** | Additional information related to the payment.  | [optional] 
**cryptogram** | **str** | Cryptogram value supplied by the token provider if DPAN or network scheme token is present  To ensure PCI compliance, this value is not stored and cannot be queried.  | [optional] 
**currency** | **str** | When Standalone Payment is not enabled, the &#x60;currency&#x60; of the payment must be the same as the payment currency defined in the customer account settings through Zuora UI.   When Standalone Payment is enabled and &#x60;standalone&#x60; is &#x60;true&#x60;, the &#x60;currency&#x60; of the standalone payment can be different from the payment currency defined in the customer account settings. The amount will not be summed up to the account balance or key metrics regardless of currency. | 
**custom_rates** | [**List[PaymentWithCustomRates]**](PaymentWithCustomRates.md) | It contains Home currency and Reporting currency custom rates currencies. The maximum number of items is 2 (you can pass the Home currency item or Reporting currency item or both).   **Note**: The API custom rate feature is permission controlled. | [optional] 
**debit_memos** | [**List[CreatePaymentDebitMemoApplication]**](CreatePaymentDebitMemoApplication.md) | Container for debit memos. The maximum number of debit memos is 1,000.  | [optional] 
**effective_date** | **str** | The date when the payment takes effect, in &#x60;yyyy-mm-dd&#x60; format.  **Note:**   - This field is required for only electronic payments. It&#39;s an optional field for external payments.   - When specified, this field must be set to the date of today.  | [optional] 
**finance_information** | [**PaymentRequestFinanceInformation**](PaymentRequestFinanceInformation.md) |  | [optional] 
**gateway_id** | **str** | The ID of the gateway instance that processes the payment. The ID must be a valid gateway instance ID and this gateway must support the specific payment method.    - When creating electronic payments, this field is required.   - When creating external payments, this field is optional. | [optional] 
**payment_gateway_number** | **str** | The natural key for the payment gateway. | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**gateway_order_id** | **str** | A merchant-specified natural key value that can be passed to the electronic payment gateway when a payment is created. If not specified, the payment number will be passed in instead.   Gateways check duplicates on the gateway order ID to ensure that the merchant do not accidentally enter the same transaction twice. This ID can also be used to do reconciliation and tie the payment to a natural key in external systems. The source of this ID varies by merchant. Some merchants use their shopping cart order IDs, and others use something different. Merchants use this ID to track transactions in their eCommerce systems.   When you create a payment for capturing the authorized funds, it is highly recommended to pass in the gatewayOrderId that you used when authorizing the funds by using the [Create authorization](https://www.zuora.com/developer/api-references/api/operation/Post_CreateAuthorization) operation, together with the &#x60;authTransactionId&#x60; field. | [optional] 
**invoices** | [**List[CreatePaymentInvoiceApplication]**](CreatePaymentInvoiceApplication.md) | Container for invoices. The maximum number of invoices is 1,000.  | [optional] 
**mit_transaction_source** | [**MitTransactionSource**](MitTransactionSource.md) |  | [optional] 
**payment_method_id** | **str** | The unique ID of the payment method that the customer used to make the payment.    If no payment method ID is specified in the request body, the default payment method for the customer account is used automatically. If the default payment method is different from the type of payments that you want to create, an error occurs. | [optional] 
**payment_method_type** | **str** | The type of the payment method that the customer used to make the payment.    Specify this value when you are creating an external payment method. If both &#x60;paymentMethodType&#x60; and &#x60;paymentMethodId&#x60; are specified, only the &#x60;paymentMethodId&#x60; value is used to create the payment. | [optional] 
**payment_option** | [**List[PaymentSchedulePaymentOptionFields]**](PaymentSchedulePaymentOptionFields.md) | Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.   Here is an example:  &#x60;&#x60;&#x60;  \&quot;paymentOption\&quot;: [   {     \&quot;type\&quot;: \&quot;GatewayOptions\&quot;,     \&quot;detail\&quot;: {       \&quot;SecCode\&quot;:\&quot;WEB\&quot;     }   } ]  &#x60;&#x60;&#x60;   &#x60;paymentOption&#x60; of the payment schedule takes precedence over &#x60;paymentOption&#x60; of the payment schedule item.   You can use this field or the &#x60;gatewayOptions&#x60; field to pass the Gateway Options fields supported by a payment gateway. However, the Gateway Options fields passed through the &#x60;paymentOption&#x60; field will be stored in the Payment Option object and can be easily retrieved.   To enable this field, submit a request at [Zuora Global Support](https://support.zuora.com/). This field is only available if &#x60;zuora-version&#x60; is set to 337.0 or later. | [optional] 
**payment_schedule_key** | **str** | The unique ID or the number of the payment schedule to be linked with the payment. See [Link payments to payment schedules](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Payment_Schedules/Link_payments_with_payment_schedules) for more information. | [optional] 
**prepayment** | **bool** | Indicates whether the payment will be used as a reserved payment. See [Prepaid Cash with Drawdown](https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Invoicing/JA_Advanced_Consumption_Billing/Prepaid_Cash_with_Drawdown) for more information. | [optional] 
**reference_id** | **str** | The transaction ID returned by the payment gateway. Use this field to reconcile payments between your gateway and Zuora Payments. | [optional] 
**soft_descriptor** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi. | [optional] 
**soft_descriptor_phone** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi. | [optional] 
**standalone** | **bool** | This field is only available if support for standalone payments is enabled.   Specify &#x60;true&#x60; to create a standalone payment that will be processed in Zuora through Zuora gateway integration but will be settled outside of Zuora.   When &#x60;standalone&#x60; is set to &#x60;true&#x60;:   - &#x60;accountId&#x60;, &#x60;amount&#x60;, &#x60;currency&#x60;, and &#x60;type&#x60; are required.    - &#x60;type&#x60; must be &#x60;Electronic&#x60;.   - &#x60;currency&#x60; of the payment can be different from the payment currency in the customer account settings.   - The amount will not be summed up into the account balance and key metrics regardless of the payment currency.   - No settlement data will be created.   - Either the applied amount or the unapplied amount of the payment is zero.   - The standalone payment cannot be applied, unapplied, or transferred.  Specify &#x60;false&#x60; to create an ordinary payment that will be created, processed, and settled in Zuora. The &#x60;currency&#x60; of an ordinary payment must be the same as the currency in the customer account settings. | [optional] 
**type** | [**PaymentType**](PaymentType.md) |  | 

## Example

```python
from zuora_sdk.models.create_payment_request import CreatePaymentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentRequest from a JSON string
create_payment_request_instance = CreatePaymentRequest.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentRequest.to_json())

# convert the object into a dict
create_payment_request_dict = create_payment_request_instance.to_dict()
# create an instance of CreatePaymentRequest from a dict
create_payment_request_from_dict = CreatePaymentRequest.from_dict(create_payment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


