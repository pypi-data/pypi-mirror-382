# CustomObjectAllFieldsDefinitionAllOfId

The `Id` field definition

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | [**CustomObjectAllFieldsDefinitionAllOfIdFormat**](CustomObjectAllFieldsDefinitionAllOfIdFormat.md) |  | [optional] 
**label** | **str** | The UI name of the field | [optional] 
**origin** | [**CustomObjectAllFieldsDefinitionAllOfIdOrigin**](CustomObjectAllFieldsDefinitionAllOfIdOrigin.md) |  | [optional] 
**type** | [**CustomObjectAllFieldsDefinitionAllOfIdType**](CustomObjectAllFieldsDefinitionAllOfIdType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_all_fields_definition_all_of_id import CustomObjectAllFieldsDefinitionAllOfId

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectAllFieldsDefinitionAllOfId from a JSON string
custom_object_all_fields_definition_all_of_id_instance = CustomObjectAllFieldsDefinitionAllOfId.from_json(json)
# print the JSON string representation of the object
print(CustomObjectAllFieldsDefinitionAllOfId.to_json())

# convert the object into a dict
custom_object_all_fields_definition_all_of_id_dict = custom_object_all_fields_definition_all_of_id_instance.to_dict()
# create an instance of CustomObjectAllFieldsDefinitionAllOfId from a dict
custom_object_all_fields_definition_all_of_id_from_dict = CustomObjectAllFieldsDefinitionAllOfId.from_dict(custom_object_all_fields_definition_all_of_id_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


