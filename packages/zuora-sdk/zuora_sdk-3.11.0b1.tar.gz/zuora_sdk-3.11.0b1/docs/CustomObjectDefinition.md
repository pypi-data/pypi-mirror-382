# CustomObjectDefinition


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by_id** | **str** | The creator&#39;s Id | [optional] 
**created_date** | **datetime** | The creation time of the custom object definition in date-time format. | [optional] 
**id** | **str** | The unique Id of the custom object definition | [optional] 
**updated_by_id** | **str** | The modifier&#39;s Id | [optional] 
**updated_date** | **datetime** | The update time of the custom object definition in date-time format. | [optional] 
**var_schema** | [**CustomObjectDefinitionSchema**](CustomObjectDefinitionSchema.md) |  | [optional] 
**type** | **str** | The API name of the custom object | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_definition import CustomObjectDefinition

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectDefinition from a JSON string
custom_object_definition_instance = CustomObjectDefinition.from_json(json)
# print the JSON string representation of the object
print(CustomObjectDefinition.to_json())

# convert the object into a dict
custom_object_definition_dict = custom_object_definition_instance.to_dict()
# create an instance of CustomObjectDefinition from a dict
custom_object_definition_from_dict = CustomObjectDefinition.from_dict(custom_object_definition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


