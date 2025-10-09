# CreateTaxationItemsForDebitMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**taxation_items** | [**List[CreateTaxationItemForDebitMemo]**](CreateTaxationItemForDebitMemo.md) | Container for taxation items.  | 

## Example

```python
from zuora_sdk.models.create_taxation_items_for_debit_memo_request import CreateTaxationItemsForDebitMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTaxationItemsForDebitMemoRequest from a JSON string
create_taxation_items_for_debit_memo_request_instance = CreateTaxationItemsForDebitMemoRequest.from_json(json)
# print the JSON string representation of the object
print(CreateTaxationItemsForDebitMemoRequest.to_json())

# convert the object into a dict
create_taxation_items_for_debit_memo_request_dict = create_taxation_items_for_debit_memo_request_instance.to_dict()
# create an instance of CreateTaxationItemsForDebitMemoRequest from a dict
create_taxation_items_for_debit_memo_request_from_dict = CreateTaxationItemsForDebitMemoRequest.from_dict(create_taxation_items_for_debit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


