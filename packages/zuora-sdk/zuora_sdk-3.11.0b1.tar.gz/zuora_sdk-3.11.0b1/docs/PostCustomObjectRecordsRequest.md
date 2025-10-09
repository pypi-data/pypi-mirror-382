# PostCustomObjectRecordsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_partial_success** | **bool** | Indicates whether the records that pass the schema validation should be created when not all records in the request pass the schema validation. | [optional] [default to False]
**records** | **List[Dict[str, object]]** | A list of custom object records to be created | 

## Example

```python
from zuora_sdk.models.post_custom_object_records_request import PostCustomObjectRecordsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostCustomObjectRecordsRequest from a JSON string
post_custom_object_records_request_instance = PostCustomObjectRecordsRequest.from_json(json)
# print the JSON string representation of the object
print(PostCustomObjectRecordsRequest.to_json())

# convert the object into a dict
post_custom_object_records_request_dict = post_custom_object_records_request_instance.to_dict()
# create an instance of PostCustomObjectRecordsRequest from a dict
post_custom_object_records_request_from_dict = PostCustomObjectRecordsRequest.from_dict(post_custom_object_records_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


