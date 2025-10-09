# PreviewExistingSubscriptionResultCreditMemos


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_memo_number** | **str** | The credit memo number. | [optional] 
**amount** | **float** | Credit memo amount. | [optional] 
**amount_without_tax** | **float** | Credit memo amount minus tax. | [optional] 
**tax_amount** | **float** | The tax amount of the credit memo. | [optional] 
**target_date** | **date** | Date through which to calculate charges if a credit memo is generated, as yyyy-mm-dd. | [optional] 
**credit_memo_items** | [**List[PreviewExistingSubscriptionCreditMemoItemResult]**](PreviewExistingSubscriptionCreditMemoItemResult.md) | Container for credit memo items. | [optional] 
**status** | **str** | The status of the credit memo. | [optional] 
**is_from_existing_credit_memo** | **bool** | Indicates whether the credit memo information is from an existing credit memo. | [optional] 

## Example

```python
from zuora_sdk.models.preview_existing_subscription_result_credit_memos import PreviewExistingSubscriptionResultCreditMemos

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewExistingSubscriptionResultCreditMemos from a JSON string
preview_existing_subscription_result_credit_memos_instance = PreviewExistingSubscriptionResultCreditMemos.from_json(json)
# print the JSON string representation of the object
print(PreviewExistingSubscriptionResultCreditMemos.to_json())

# convert the object into a dict
preview_existing_subscription_result_credit_memos_dict = preview_existing_subscription_result_credit_memos_instance.to_dict()
# create an instance of PreviewExistingSubscriptionResultCreditMemos from a dict
preview_existing_subscription_result_credit_memos_from_dict = PreviewExistingSubscriptionResultCreditMemos.from_dict(preview_existing_subscription_result_credit_memos_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


