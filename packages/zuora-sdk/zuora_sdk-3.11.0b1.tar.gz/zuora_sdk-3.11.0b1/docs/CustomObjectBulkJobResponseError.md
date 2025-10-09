# CustomObjectBulkJobResponseError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** | The error code. | [optional] 
**message** | **str** | The error message. | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_bulk_job_response_error import CustomObjectBulkJobResponseError

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectBulkJobResponseError from a JSON string
custom_object_bulk_job_response_error_instance = CustomObjectBulkJobResponseError.from_json(json)
# print the JSON string representation of the object
print(CustomObjectBulkJobResponseError.to_json())

# convert the object into a dict
custom_object_bulk_job_response_error_dict = custom_object_bulk_job_response_error_instance.to_dict()
# create an instance of CustomObjectBulkJobResponseError from a dict
custom_object_bulk_job_response_error_from_dict = CustomObjectBulkJobResponseError.from_dict(custom_object_bulk_job_response_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


