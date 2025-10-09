# PostCustomObjectDefinitionsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**definitions** | [**Dict[str, PostCustomObjectDefinitionsRequestDefinition]**](PostCustomObjectDefinitionsRequestDefinition.md) | The custom object definitions. This object maps types to custom object definitions. | [optional] 

## Example

```python
from zuora_sdk.models.post_custom_object_definitions_request import PostCustomObjectDefinitionsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostCustomObjectDefinitionsRequest from a JSON string
post_custom_object_definitions_request_instance = PostCustomObjectDefinitionsRequest.from_json(json)
# print the JSON string representation of the object
print(PostCustomObjectDefinitionsRequest.to_json())

# convert the object into a dict
post_custom_object_definitions_request_dict = post_custom_object_definitions_request_instance.to_dict()
# create an instance of PostCustomObjectDefinitionsRequest from a dict
post_custom_object_definitions_request_from_dict = PostCustomObjectDefinitionsRequest.from_dict(post_custom_object_definitions_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


