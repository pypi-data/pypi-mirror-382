# CreateAccountResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**account_id** | **str** | Auto-generated account ID.  | [optional] 
**account_number** | **str** | Account number.  | [optional] 
**bill_to_contact_id** | **str** | The ID of the bill-to contact.  | [optional] 
**contracted_mrr** | **decimal.Decimal** | Contracted monthly recurring revenue of the subscription.  | [optional] 
**credit_memo_id** | **str** | The credit memo ID, if a credit memo is generated during the subscription process.   **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. | [optional] 
**invoice_id** | **str** | ID of the invoice generated at account creation, if applicable.  | [optional] 
**paid_amount** | **decimal.Decimal** | Amount collected on the invoice generated at account creation, if applicable. | [optional] 
**payment_id** | **str** | ID of the payment collected on the invoice generated at account creation, if applicable. | [optional] 
**payment_method_id** | **str** | ID of the payment method that was set up at account creation, which automatically becomes the default payment method for this account. | [optional] 
**ship_to_contact_id** | **str** | The ID of the ship-to contact.  | [optional] 
**sold_to_contact_id** | **str** | The ID of the sold-to contact.  | [optional] 
**subscription_id** | **str** | ID of the subscription that was set up at account creation, if applicable.  | [optional] 
**subscription_number** | **str** | Number of the subscription that was set up at account creation, if applicable. | [optional] 
**total_contracted_value** | **decimal.Decimal** | Total contracted value of the subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.create_account_response import CreateAccountResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAccountResponse from a JSON string
create_account_response_instance = CreateAccountResponse.from_json(json)
# print the JSON string representation of the object
print(CreateAccountResponse.to_json())

# convert the object into a dict
create_account_response_dict = create_account_response_instance.to_dict()
# create an instance of CreateAccountResponse from a dict
create_account_response_from_dict = CreateAccountResponse.from_dict(create_account_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


