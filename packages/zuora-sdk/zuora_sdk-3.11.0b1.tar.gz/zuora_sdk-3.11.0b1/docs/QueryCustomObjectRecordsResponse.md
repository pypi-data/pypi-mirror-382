# QueryCustomObjectRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** | The record count of the given custom object type | 
**records** | [**List[CustomObjectRecordWithAllFields]**](CustomObjectRecordWithAllFields.md) |  | 

## Example

```python
from zuora_sdk.models.query_custom_object_records_response import QueryCustomObjectRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCustomObjectRecordsResponse from a JSON string
query_custom_object_records_response_instance = QueryCustomObjectRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryCustomObjectRecordsResponse.to_json())

# convert the object into a dict
query_custom_object_records_response_dict = query_custom_object_records_response_instance.to_dict()
# create an instance of QueryCustomObjectRecordsResponse from a dict
query_custom_object_records_response_from_dict = QueryCustomObjectRecordsResponse.from_dict(query_custom_object_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


