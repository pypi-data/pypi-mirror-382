# AccountBillingAndPayment

Container for billing and payment information for the account.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**additional_email_addresses** | **List[str]** | A list of additional email addresses to receive email notifications.  | [optional] 
**auto_pay** | **bool** | Whether future payments are automatically collected when they are due during a payment run.   | [optional] 
**bill_cycle_day** | **int** | Billing cycle day (BCD), the day of the month when a bill run generates invoices for the account. | [optional] 
**currency** | **str** | A currency defined in the web-based UI administrative settings.  | [optional] 
**default_payment_method_id** | **str** | ID of the default payment method for the account.  | [optional] 
**invoice_delivery_prefs_email** | **bool** | Whether the customer wants to receive invoices through email.   | [optional] 
**invoice_delivery_prefs_print** | **bool** | Whether the customer wants to receive printed invoices, such as through postal mail. | [optional] 
**payment_gateway** | **str** | The name of the payment gateway instance. If null or left unassigned, the Account will use the Default Gateway. | [optional] 
**payment_term** | **str** | A payment-terms indicator defined in the web-based UI administrative settings, e.g., \&quot;Net 30\&quot;. | [optional] 
**payment_gateway_number** | **str** | paymentGatewayNumber\&quot;. | [optional] 
**payment_method_cascading_consent** | **bool** | payment method cascading consent  | [optional] 
**roll_up_usage** | **bool** | whether roll up usage of the account to its parent account | [optional] 
**gateway_routing_eligible** | **bool** | Whether gateway routing is eligible for the account | [optional] 

## Example

```python
from zuora_sdk.models.account_billing_and_payment import AccountBillingAndPayment

# TODO update the JSON string below
json = "{}"
# create an instance of AccountBillingAndPayment from a JSON string
account_billing_and_payment_instance = AccountBillingAndPayment.from_json(json)
# print the JSON string representation of the object
print(AccountBillingAndPayment.to_json())

# convert the object into a dict
account_billing_and_payment_dict = account_billing_and_payment_instance.to_dict()
# create an instance of AccountBillingAndPayment from a dict
account_billing_and_payment_from_dict = AccountBillingAndPayment.from_dict(account_billing_and_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


