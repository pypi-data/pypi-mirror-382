# UnapplyCreditMemoItemToDebitMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount that is unapplied from the specific item.   | 
**credit_memo_item_id** | **str** | The ID of the credit memo item.  | [optional] 
**credit_tax_item_id** | **str** | The ID of the credit memo taxation item.  | [optional] 
**debit_memo_item_id** | **str** | The ID of the debit memo item that the credit memo item is unapplied from.  | [optional] 
**tax_item_id** | **str** | The ID of the debit memo taxation item that the credit memo taxation item is unapplied from. | [optional] 

## Example

```python
from zuora_sdk.models.unapply_credit_memo_item_to_debit_memo_item import UnapplyCreditMemoItemToDebitMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyCreditMemoItemToDebitMemoItem from a JSON string
unapply_credit_memo_item_to_debit_memo_item_instance = UnapplyCreditMemoItemToDebitMemoItem.from_json(json)
# print the JSON string representation of the object
print(UnapplyCreditMemoItemToDebitMemoItem.to_json())

# convert the object into a dict
unapply_credit_memo_item_to_debit_memo_item_dict = unapply_credit_memo_item_to_debit_memo_item_instance.to_dict()
# create an instance of UnapplyCreditMemoItemToDebitMemoItem from a dict
unapply_credit_memo_item_to_debit_memo_item_from_dict = UnapplyCreditMemoItemToDebitMemoItem.from_dict(unapply_credit_memo_item_to_debit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


