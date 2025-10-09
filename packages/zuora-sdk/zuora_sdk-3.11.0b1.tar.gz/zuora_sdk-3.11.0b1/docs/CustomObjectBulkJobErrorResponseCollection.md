# CustomObjectBulkJobErrorResponseCollection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | [**List[CustomObjectBulkJobErrorResponse]**](CustomObjectBulkJobErrorResponse.md) | All errors for a custom object bulk job. | 

## Example

```python
from zuora_sdk.models.custom_object_bulk_job_error_response_collection import CustomObjectBulkJobErrorResponseCollection

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectBulkJobErrorResponseCollection from a JSON string
custom_object_bulk_job_error_response_collection_instance = CustomObjectBulkJobErrorResponseCollection.from_json(json)
# print the JSON string representation of the object
print(CustomObjectBulkJobErrorResponseCollection.to_json())

# convert the object into a dict
custom_object_bulk_job_error_response_collection_dict = custom_object_bulk_job_error_response_collection_instance.to_dict()
# create an instance of CustomObjectBulkJobErrorResponseCollection from a dict
custom_object_bulk_job_error_response_collection_from_dict = CustomObjectBulkJobErrorResponseCollection.from_dict(custom_object_bulk_job_error_response_collection_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


