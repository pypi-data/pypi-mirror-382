# CustomObjectBulkJobResponseCollection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** | The number of custom object bulk jobs returned in the result page set. | [optional] 
**cursor** | **str** | The &#x60;cursor&#x60; points to the last job record of the current page. | [optional] 
**jobs** | [**List[CustomObjectBulkJobResponse]**](CustomObjectBulkJobResponse.md) | All custom object bulk jobs returned in the result page set. | 

## Example

```python
from zuora_sdk.models.custom_object_bulk_job_response_collection import CustomObjectBulkJobResponseCollection

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectBulkJobResponseCollection from a JSON string
custom_object_bulk_job_response_collection_instance = CustomObjectBulkJobResponseCollection.from_json(json)
# print the JSON string representation of the object
print(CustomObjectBulkJobResponseCollection.to_json())

# convert the object into a dict
custom_object_bulk_job_response_collection_dict = custom_object_bulk_job_response_collection_instance.to_dict()
# create an instance of CustomObjectBulkJobResponseCollection from a dict
custom_object_bulk_job_response_collection_from_dict = CustomObjectBulkJobResponseCollection.from_dict(custom_object_bulk_job_response_collection_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


