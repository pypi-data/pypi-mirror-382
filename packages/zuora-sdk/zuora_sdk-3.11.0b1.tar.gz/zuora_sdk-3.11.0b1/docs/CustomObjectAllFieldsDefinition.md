# CustomObjectAllFieldsDefinition

The definitions of all the fields in the custom object definition

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by_id** | [**CustomObjectAllFieldsDefinitionAllOfCreatedById**](CustomObjectAllFieldsDefinitionAllOfCreatedById.md) |  | [optional] 
**created_date** | [**CustomObjectAllFieldsDefinitionAllOfCreatedDate**](CustomObjectAllFieldsDefinitionAllOfCreatedDate.md) |  | [optional] 
**id** | [**CustomObjectAllFieldsDefinitionAllOfId**](CustomObjectAllFieldsDefinitionAllOfId.md) |  | [optional] 
**updated_by_id** | [**CustomObjectAllFieldsDefinitionAllOfUpdatedById**](CustomObjectAllFieldsDefinitionAllOfUpdatedById.md) |  | [optional] 
**updated_date** | [**CustomObjectAllFieldsDefinitionAllOfUpdatedDate**](CustomObjectAllFieldsDefinitionAllOfUpdatedDate.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_all_fields_definition import CustomObjectAllFieldsDefinition

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectAllFieldsDefinition from a JSON string
custom_object_all_fields_definition_instance = CustomObjectAllFieldsDefinition.from_json(json)
# print the JSON string representation of the object
print(CustomObjectAllFieldsDefinition.to_json())

# convert the object into a dict
custom_object_all_fields_definition_dict = custom_object_all_fields_definition_instance.to_dict()
# create an instance of CustomObjectAllFieldsDefinition from a dict
custom_object_all_fields_definition_from_dict = CustomObjectAllFieldsDefinition.from_dict(custom_object_all_fields_definition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


