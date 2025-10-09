# AccountSummaryDefaultPaymentMethod



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_card_expiration_month** | **str** | Two-digit numeric card expiration month as &#x60;mm&#x60;.  | [optional] 
**credit_card_expiration_year** | **str** | Four-digit card expiration year as &#x60;yyyy&#x60;.  | [optional] 
**credit_card_number** | **str** | Credit card number, 16 characters or less, displayed in masked format (e.g., ************1234). | [optional] 
**credit_card_type** | **str** | The type of the credit card.   Possible values  include &#x60;Visa&#x60;, &#x60;MasterCard&#x60;, &#x60;AmericanExpress&#x60;, &#x60;Discover&#x60;, &#x60;JCB&#x60;, and &#x60;Diners&#x60;. For more information about credit card types supported by different payment gateways, see [Supported Payment Methods](https://knowledgecenter.zuora.com/Zuora_Central/Billing_and_Payments/L_Payment_Methods/Supported_Payment_Methods). | [optional] 
**id** | **str** | ID of the default payment method associated with this account.  | [optional] 
**payment_method_type** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.account_summary_default_payment_method import AccountSummaryDefaultPaymentMethod

# TODO update the JSON string below
json = "{}"
# create an instance of AccountSummaryDefaultPaymentMethod from a JSON string
account_summary_default_payment_method_instance = AccountSummaryDefaultPaymentMethod.from_json(json)
# print the JSON string representation of the object
print(AccountSummaryDefaultPaymentMethod.to_json())

# convert the object into a dict
account_summary_default_payment_method_dict = account_summary_default_payment_method_instance.to_dict()
# create an instance of AccountSummaryDefaultPaymentMethod from a dict
account_summary_default_payment_method_from_dict = AccountSummaryDefaultPaymentMethod.from_dict(account_summary_default_payment_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


