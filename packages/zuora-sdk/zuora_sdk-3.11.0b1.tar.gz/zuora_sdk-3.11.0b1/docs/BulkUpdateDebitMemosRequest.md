# BulkUpdateDebitMemosRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**memos** | [**List[UpdateDebitMemoWithId]**](UpdateDebitMemoWithId.md) | The container for a list of debit memos. The maximum number of debit memos is 50. | [optional] 

## Example

```python
from zuora_sdk.models.bulk_update_debit_memos_request import BulkUpdateDebitMemosRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkUpdateDebitMemosRequest from a JSON string
bulk_update_debit_memos_request_instance = BulkUpdateDebitMemosRequest.from_json(json)
# print the JSON string representation of the object
print(BulkUpdateDebitMemosRequest.to_json())

# convert the object into a dict
bulk_update_debit_memos_request_dict = bulk_update_debit_memos_request_instance.to_dict()
# create an instance of BulkUpdateDebitMemosRequest from a dict
bulk_update_debit_memos_request_from_dict = BulkUpdateDebitMemosRequest.from_dict(bulk_update_debit_memos_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


