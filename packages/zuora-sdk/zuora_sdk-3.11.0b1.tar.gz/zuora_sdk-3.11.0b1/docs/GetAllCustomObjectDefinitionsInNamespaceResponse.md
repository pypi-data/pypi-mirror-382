# GetAllCustomObjectDefinitionsInNamespaceResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** | The number of objects in the &#x60;definitions&#x60; object. The value of this field is the number of custom object definitions in the namespace. | [optional] 
**definitions** | [**Dict[str, CustomObjectDefinition]**](CustomObjectDefinition.md) | The custom object definitions. This object maps types to custom object definitions. | [optional] 

## Example

```python
from zuora_sdk.models.get_all_custom_object_definitions_in_namespace_response import GetAllCustomObjectDefinitionsInNamespaceResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAllCustomObjectDefinitionsInNamespaceResponse from a JSON string
get_all_custom_object_definitions_in_namespace_response_instance = GetAllCustomObjectDefinitionsInNamespaceResponse.from_json(json)
# print the JSON string representation of the object
print(GetAllCustomObjectDefinitionsInNamespaceResponse.to_json())

# convert the object into a dict
get_all_custom_object_definitions_in_namespace_response_dict = get_all_custom_object_definitions_in_namespace_response_instance.to_dict()
# create an instance of GetAllCustomObjectDefinitionsInNamespaceResponse from a dict
get_all_custom_object_definitions_in_namespace_response_from_dict = GetAllCustomObjectDefinitionsInNamespaceResponse.from_dict(get_all_custom_object_definitions_in_namespace_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


