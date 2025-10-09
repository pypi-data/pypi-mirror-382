# ApplyCreditMemoItemToDebitMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount that is applied to the specific item.   | 
**credit_memo_item_id** | **str** | The ID of the credit memo item.  | [optional] 
**credit_tax_item_id** | **str** | The ID of the credit memo taxation item.  | [optional] 
**debit_memo_item_id** | **str** | The ID of the debit memo item that the credit memo item is applied to.  | [optional] 
**tax_item_id** | **str** | The ID of the debit memo taxation item that the credit memo taxation item is applied to. | [optional] 

## Example

```python
from zuora_sdk.models.apply_credit_memo_item_to_debit_memo_item import ApplyCreditMemoItemToDebitMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of ApplyCreditMemoItemToDebitMemoItem from a JSON string
apply_credit_memo_item_to_debit_memo_item_instance = ApplyCreditMemoItemToDebitMemoItem.from_json(json)
# print the JSON string representation of the object
print(ApplyCreditMemoItemToDebitMemoItem.to_json())

# convert the object into a dict
apply_credit_memo_item_to_debit_memo_item_dict = apply_credit_memo_item_to_debit_memo_item_instance.to_dict()
# create an instance of ApplyCreditMemoItemToDebitMemoItem from a dict
apply_credit_memo_item_to_debit_memo_item_from_dict = ApplyCreditMemoItemToDebitMemoItem.from_dict(apply_credit_memo_item_to_debit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


