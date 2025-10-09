# CreateSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contracted_mrr** | **float** | Monthly recurring revenue of the subscription.  | [optional] 
**credit_memo_id** | **str** | The credit memo ID, if a credit memo is generated during the subscription process.   **Note:** This container is only available if you set the Zuora REST API minor version to 207.0 or later in the request header, and you have  [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. | [optional] 
**invoice_id** | **str** | Invoice ID, if an invoice is generated during the subscription process.  | [optional] 
**paid_amount** | **float** | Payment amount, if a payment is collected.  | [optional] 
**payment_id** | **str** | Payment ID, if a payment is collected.  | [optional] 
**subscription_id** | **str** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**total_contracted_value** | **float** | Total contracted value of the subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.create_subscription_response import CreateSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateSubscriptionResponse from a JSON string
create_subscription_response_instance = CreateSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(CreateSubscriptionResponse.to_json())

# convert the object into a dict
create_subscription_response_dict = create_subscription_response_instance.to_dict()
# create an instance of CreateSubscriptionResponse from a dict
create_subscription_response_from_dict = CreateSubscriptionResponse.from_dict(create_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


