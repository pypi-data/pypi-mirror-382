# CustomObjectBulkJobRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filter** | [**CustomObjectBulkDeleteFilter**](CustomObjectBulkDeleteFilter.md) |  | [optional] 
**namespace** | [**CustomObjectBulkJobRequestNamespace**](CustomObjectBulkJobRequestNamespace.md) |  | 
**object** | **str** | The object that the bulk operation performs on. | 
**operation** | [**CustomObjectBulkJobRequestOperation**](CustomObjectBulkJobRequestOperation.md) |  | 

## Example

```python
from zuora_sdk.models.custom_object_bulk_job_request import CustomObjectBulkJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectBulkJobRequest from a JSON string
custom_object_bulk_job_request_instance = CustomObjectBulkJobRequest.from_json(json)
# print the JSON string representation of the object
print(CustomObjectBulkJobRequest.to_json())

# convert the object into a dict
custom_object_bulk_job_request_dict = custom_object_bulk_job_request_instance.to_dict()
# create an instance of CustomObjectBulkJobRequest from a dict
custom_object_bulk_job_request_from_dict = CustomObjectBulkJobRequest.from_dict(custom_object_bulk_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


