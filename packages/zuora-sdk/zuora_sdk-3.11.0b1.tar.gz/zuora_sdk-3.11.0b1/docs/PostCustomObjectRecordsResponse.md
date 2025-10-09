# PostCustomObjectRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | [**CustomObjectRecordsErrorResponse**](CustomObjectRecordsErrorResponse.md) |  | [optional] 
**records** | [**List[CustomObjectRecordWithAllFields]**](CustomObjectRecordWithAllFields.md) | The custom object records that are succesfully created and stored | [optional] 

## Example

```python
from zuora_sdk.models.post_custom_object_records_response import PostCustomObjectRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PostCustomObjectRecordsResponse from a JSON string
post_custom_object_records_response_instance = PostCustomObjectRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(PostCustomObjectRecordsResponse.to_json())

# convert the object into a dict
post_custom_object_records_response_dict = post_custom_object_records_response_instance.to_dict()
# create an instance of PostCustomObjectRecordsResponse from a dict
post_custom_object_records_response_from_dict = PostCustomObjectRecordsResponse.from_dict(post_custom_object_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


