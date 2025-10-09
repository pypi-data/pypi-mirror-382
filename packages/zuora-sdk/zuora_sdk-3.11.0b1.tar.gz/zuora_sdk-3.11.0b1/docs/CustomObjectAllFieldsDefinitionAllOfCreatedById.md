# CustomObjectAllFieldsDefinitionAllOfCreatedById

The `CreatedById` field definition

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | [**CustomObjectAllFieldsDefinitionAllOfCreatedByIdFormat**](CustomObjectAllFieldsDefinitionAllOfCreatedByIdFormat.md) |  | [optional] 
**label** | **str** | The UI name of the field | [optional] 
**origin** | [**CustomObjectAllFieldsDefinitionAllOfCreatedByIdOrigin**](CustomObjectAllFieldsDefinitionAllOfCreatedByIdOrigin.md) |  | [optional] 
**type** | [**CustomObjectAllFieldsDefinitionAllOfCreatedByIdType**](CustomObjectAllFieldsDefinitionAllOfCreatedByIdType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_all_fields_definition_all_of_created_by_id import CustomObjectAllFieldsDefinitionAllOfCreatedById

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectAllFieldsDefinitionAllOfCreatedById from a JSON string
custom_object_all_fields_definition_all_of_created_by_id_instance = CustomObjectAllFieldsDefinitionAllOfCreatedById.from_json(json)
# print the JSON string representation of the object
print(CustomObjectAllFieldsDefinitionAllOfCreatedById.to_json())

# convert the object into a dict
custom_object_all_fields_definition_all_of_created_by_id_dict = custom_object_all_fields_definition_all_of_created_by_id_instance.to_dict()
# create an instance of CustomObjectAllFieldsDefinitionAllOfCreatedById from a dict
custom_object_all_fields_definition_all_of_created_by_id_from_dict = CustomObjectAllFieldsDefinitionAllOfCreatedById.from_dict(custom_object_all_fields_definition_all_of_created_by_id_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


