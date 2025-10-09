# BulkDebitMemosResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**memos** | [**List[DebitMemoResponse]**](DebitMemoResponse.md) | The container for a list of debit memos.  | [optional] 

## Example

```python
from zuora_sdk.models.bulk_debit_memos_response import BulkDebitMemosResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkDebitMemosResponse from a JSON string
bulk_debit_memos_response_instance = BulkDebitMemosResponse.from_json(json)
# print the JSON string representation of the object
print(BulkDebitMemosResponse.to_json())

# convert the object into a dict
bulk_debit_memos_response_dict = bulk_debit_memos_response_instance.to_dict()
# create an instance of BulkDebitMemosResponse from a dict
bulk_debit_memos_response_from_dict = BulkDebitMemosResponse.from_dict(bulk_debit_memos_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


