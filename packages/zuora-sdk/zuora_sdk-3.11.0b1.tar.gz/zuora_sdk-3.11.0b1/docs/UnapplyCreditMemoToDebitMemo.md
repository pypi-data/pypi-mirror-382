# UnapplyCreditMemoToDebitMemo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The credit memo amount to be unapplied from the debit memo.  | 
**debit_memo_id** | **str** | The unique ID of the debit memo that the credit memo is unapplied from.  | 
**items** | [**List[UnapplyCreditMemoItemToDebitMemoItem]**](UnapplyCreditMemoItemToDebitMemoItem.md) | Container for items. The maximum number of items is 1,000.  | [optional] 

## Example

```python
from zuora_sdk.models.unapply_credit_memo_to_debit_memo import UnapplyCreditMemoToDebitMemo

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyCreditMemoToDebitMemo from a JSON string
unapply_credit_memo_to_debit_memo_instance = UnapplyCreditMemoToDebitMemo.from_json(json)
# print the JSON string representation of the object
print(UnapplyCreditMemoToDebitMemo.to_json())

# convert the object into a dict
unapply_credit_memo_to_debit_memo_dict = unapply_credit_memo_to_debit_memo_instance.to_dict()
# create an instance of UnapplyCreditMemoToDebitMemo from a dict
unapply_credit_memo_to_debit_memo_from_dict = UnapplyCreditMemoToDebitMemo.from_dict(unapply_credit_memo_to_debit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


