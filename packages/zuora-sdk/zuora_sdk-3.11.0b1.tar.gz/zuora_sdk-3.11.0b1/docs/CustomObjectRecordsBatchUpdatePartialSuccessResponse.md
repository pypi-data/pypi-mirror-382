# CustomObjectRecordsBatchUpdatePartialSuccessResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | [**CustomObjectRecordsErrorResponse**](CustomObjectRecordsErrorResponse.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_records_batch_update_partial_success_response import CustomObjectRecordsBatchUpdatePartialSuccessResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectRecordsBatchUpdatePartialSuccessResponse from a JSON string
custom_object_records_batch_update_partial_success_response_instance = CustomObjectRecordsBatchUpdatePartialSuccessResponse.from_json(json)
# print the JSON string representation of the object
print(CustomObjectRecordsBatchUpdatePartialSuccessResponse.to_json())

# convert the object into a dict
custom_object_records_batch_update_partial_success_response_dict = custom_object_records_batch_update_partial_success_response_instance.to_dict()
# create an instance of CustomObjectRecordsBatchUpdatePartialSuccessResponse from a dict
custom_object_records_batch_update_partial_success_response_from_dict = CustomObjectRecordsBatchUpdatePartialSuccessResponse.from_dict(custom_object_records_batch_update_partial_success_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


