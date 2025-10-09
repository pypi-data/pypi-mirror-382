# DebitMemoItemTaxationItems

Container for the taxation items of the debit memo item.   **Note**: This field is only available if you set the `zuora-version` request header to `239.0` or later.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[GetDebitMemoTaxItemNew]**](GetDebitMemoTaxItemNew.md) | List of taxation items.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_item_taxation_items import DebitMemoItemTaxationItems

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoItemTaxationItems from a JSON string
debit_memo_item_taxation_items_instance = DebitMemoItemTaxationItems.from_json(json)
# print the JSON string representation of the object
print(DebitMemoItemTaxationItems.to_json())

# convert the object into a dict
debit_memo_item_taxation_items_dict = debit_memo_item_taxation_items_instance.to_dict()
# create an instance of DebitMemoItemTaxationItems from a dict
debit_memo_item_taxation_items_from_dict = DebitMemoItemTaxationItems.from_dict(debit_memo_item_taxation_items_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


