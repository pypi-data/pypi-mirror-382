# CustomObjectAllFieldsDefinitionAllOfUpdatedById

The `UpdatedById` field definition

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | [**CustomObjectAllFieldsDefinitionAllOfUpdatedByIdFormat**](CustomObjectAllFieldsDefinitionAllOfUpdatedByIdFormat.md) |  | [optional] 
**label** | **str** | The UI name of the field | [optional] 
**origin** | [**CustomObjectAllFieldsDefinitionAllOfUpdatedByIdOrigin**](CustomObjectAllFieldsDefinitionAllOfUpdatedByIdOrigin.md) |  | [optional] 
**type** | [**CustomObjectAllFieldsDefinitionAllOfUpdatedByIdType**](CustomObjectAllFieldsDefinitionAllOfUpdatedByIdType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_all_fields_definition_all_of_updated_by_id import CustomObjectAllFieldsDefinitionAllOfUpdatedById

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectAllFieldsDefinitionAllOfUpdatedById from a JSON string
custom_object_all_fields_definition_all_of_updated_by_id_instance = CustomObjectAllFieldsDefinitionAllOfUpdatedById.from_json(json)
# print the JSON string representation of the object
print(CustomObjectAllFieldsDefinitionAllOfUpdatedById.to_json())

# convert the object into a dict
custom_object_all_fields_definition_all_of_updated_by_id_dict = custom_object_all_fields_definition_all_of_updated_by_id_instance.to_dict()
# create an instance of CustomObjectAllFieldsDefinitionAllOfUpdatedById from a dict
custom_object_all_fields_definition_all_of_updated_by_id_from_dict = CustomObjectAllFieldsDefinitionAllOfUpdatedById.from_dict(custom_object_all_fields_definition_all_of_updated_by_id_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


