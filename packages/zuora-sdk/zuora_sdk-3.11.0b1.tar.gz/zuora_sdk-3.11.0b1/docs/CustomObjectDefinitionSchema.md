# CustomObjectDefinitionSchema

The schema of the custom object definition

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auditable** | **List[str]** | The set of fields which Audit Trail tracks and records changes of. | [optional] 
**enable_create_record_auditing** | **bool** | Indicates whether to audit the creation of custom object records of this custom object definition. | [optional] 
**enable_delete_record_auditing** | **bool** | Indicates whether to audit the deletion of custom object records of this custom object definition. | [optional] 
**filterable** | **List[str]** | The set of fields that are allowed to be queried on. Queries on non-filterable fields will be rejected. You can not change a non-filterable field to filterable. | [optional] 
**label** | **str** | A label for the custom object | [optional] 
**object** | **str** | The API name of the custom object | [optional] 
**properties** | [**CustomObjectAllFieldsDefinition**](CustomObjectAllFieldsDefinition.md) |  | [optional] 
**relationships** | [**List[CustomObjectDefinitionRelationship]**](CustomObjectDefinitionRelationship.md) | An array of relationships with Zuora objects or other custom objects | [optional] 
**required** | **List[str]** | The required fields of the custom object definition. You can change required fields to optional. However, you can only change optional fields to required on the custom objects with no records. | [optional] 
**type** | [**CustomObjectDefinitionSchemaType**](CustomObjectDefinitionSchemaType.md) |  | [optional] 
**unique** | **List[str]** | The fields with unique constraints. | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_definition_schema import CustomObjectDefinitionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectDefinitionSchema from a JSON string
custom_object_definition_schema_instance = CustomObjectDefinitionSchema.from_json(json)
# print the JSON string representation of the object
print(CustomObjectDefinitionSchema.to_json())

# convert the object into a dict
custom_object_definition_schema_dict = custom_object_definition_schema_instance.to_dict()
# create an instance of CustomObjectDefinitionSchema from a dict
custom_object_definition_schema_from_dict = CustomObjectDefinitionSchema.from_dict(custom_object_definition_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


