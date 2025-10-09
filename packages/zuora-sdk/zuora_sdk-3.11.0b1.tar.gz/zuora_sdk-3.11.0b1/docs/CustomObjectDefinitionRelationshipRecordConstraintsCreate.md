# CustomObjectDefinitionRelationshipRecordConstraintsCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enforce_valid_mapping** | **bool** | Specifies whether Zuora validates the values of mapped fields in custom object records. | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_definition_relationship_record_constraints_create import CustomObjectDefinitionRelationshipRecordConstraintsCreate

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectDefinitionRelationshipRecordConstraintsCreate from a JSON string
custom_object_definition_relationship_record_constraints_create_instance = CustomObjectDefinitionRelationshipRecordConstraintsCreate.from_json(json)
# print the JSON string representation of the object
print(CustomObjectDefinitionRelationshipRecordConstraintsCreate.to_json())

# convert the object into a dict
custom_object_definition_relationship_record_constraints_create_dict = custom_object_definition_relationship_record_constraints_create_instance.to_dict()
# create an instance of CustomObjectDefinitionRelationshipRecordConstraintsCreate from a dict
custom_object_definition_relationship_record_constraints_create_from_dict = CustomObjectDefinitionRelationshipRecordConstraintsCreate.from_dict(custom_object_definition_relationship_record_constraints_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


