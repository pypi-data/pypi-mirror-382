# SubscriptionCreditMemo

 Container for credit memos.   **Note:** This container is only available if you set the Zuora REST API minor version to 207.0 or later in the request header, and you have  [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | Credit memo amount. | [optional] 
**amount_without_tax** | **float** | Credit memo amount minus tax. | [optional] 
**credit_memo_items** | [**List[SubscriptionCreditMemoItem]**](SubscriptionCreditMemoItem.md) |  | [optional] 
**tax_amount** | **float** | Tax amount on the credit memo. | [optional] 

## Example

```python
from zuora_sdk.models.subscription_credit_memo import SubscriptionCreditMemo

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionCreditMemo from a JSON string
subscription_credit_memo_instance = SubscriptionCreditMemo.from_json(json)
# print the JSON string representation of the object
print(SubscriptionCreditMemo.to_json())

# convert the object into a dict
subscription_credit_memo_dict = subscription_credit_memo_instance.to_dict()
# create an instance of SubscriptionCreditMemo from a dict
subscription_credit_memo_from_dict = SubscriptionCreditMemo.from_dict(subscription_credit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


