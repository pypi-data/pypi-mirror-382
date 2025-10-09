# CustomObjectBulkJobErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** | The error code. | [optional] 
**message** | **str** | The error message. | [optional] 
**record** | [**CustomObjectRecordWithAllFields**](CustomObjectRecordWithAllFields.md) |  | [optional] 
**row** | **int** | The CSV record row number. The custom object record data starts at the second row because the first row is the CSV header. | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_bulk_job_error_response import CustomObjectBulkJobErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectBulkJobErrorResponse from a JSON string
custom_object_bulk_job_error_response_instance = CustomObjectBulkJobErrorResponse.from_json(json)
# print the JSON string representation of the object
print(CustomObjectBulkJobErrorResponse.to_json())

# convert the object into a dict
custom_object_bulk_job_error_response_dict = custom_object_bulk_job_error_response_instance.to_dict()
# create an instance of CustomObjectBulkJobErrorResponse from a dict
custom_object_bulk_job_error_response_from_dict = CustomObjectBulkJobErrorResponse.from_dict(custom_object_bulk_job_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


