# QueryCustomObjectsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | **List[Dict[str, object]]** |  | [optional] 

## Example

```python
from zuora_sdk.models.query_custom_objects_response import QueryCustomObjectsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCustomObjectsResponse from a JSON string
query_custom_objects_response_instance = QueryCustomObjectsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryCustomObjectsResponse.to_json())

# convert the object into a dict
query_custom_objects_response_dict = query_custom_objects_response_instance.to_dict()
# create an instance of QueryCustomObjectsResponse from a dict
query_custom_objects_response_from_dict = QueryCustomObjectsResponse.from_dict(query_custom_objects_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


