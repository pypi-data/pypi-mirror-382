# CustomObjectDefinitionUpdateActionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Optional property for &#x60;updateObject&#x60; action | [optional] 
**enable_create_record_auditing** | **bool** | Indicates whether to audit the creation of custom object records of this custom object definition. | [optional] 
**enable_delete_record_auditing** | **bool** | Indicates whether to audit the deletion of custom object records of this custom object definition. | [optional] 
**var_field** | [**UpdateCustomObjectCusotmField**](UpdateCustomObjectCusotmField.md) |  | [optional] 
**label** | **str** | Optional property for &#x60;updateObject&#x60; action | [optional] 
**namespace** | **str** | The namespace of the custom object definition to be updated | [optional] 
**object** | **str** | The API name of the custom object definition to be updated | [optional] 
**relationship** | **object** |  | [optional] 
**type** | [**CustomObjectDefinitionUpdateActionResponseType**](CustomObjectDefinitionUpdateActionResponseType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_definition_update_action_response import CustomObjectDefinitionUpdateActionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectDefinitionUpdateActionResponse from a JSON string
custom_object_definition_update_action_response_instance = CustomObjectDefinitionUpdateActionResponse.from_json(json)
# print the JSON string representation of the object
print(CustomObjectDefinitionUpdateActionResponse.to_json())

# convert the object into a dict
custom_object_definition_update_action_response_dict = custom_object_definition_update_action_response_instance.to_dict()
# create an instance of CustomObjectDefinitionUpdateActionResponse from a dict
custom_object_definition_update_action_response_from_dict = CustomObjectDefinitionUpdateActionResponse.from_dict(custom_object_definition_update_action_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


