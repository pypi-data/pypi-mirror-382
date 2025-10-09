# CustomObjectDefinitionRelationship

The schema of the custom object definition relationship

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cardinality** | [**CustomObjectDefinitionSchemaRelationshipCardinality**](CustomObjectDefinitionSchemaRelationshipCardinality.md) |  | [optional] 
**fields** | **Dict[str, str]** | Field mappings between the custom object and the related object. | 
**namespace** | **str** | The namespace where the related object is located. | 
**object** | **str** | The API name of the related object | 
**record_constraints** | [**CustomObjectDefinitionRelationshipRecordConstraints**](CustomObjectDefinitionRelationshipRecordConstraints.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_definition_relationship import CustomObjectDefinitionRelationship

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectDefinitionRelationship from a JSON string
custom_object_definition_relationship_instance = CustomObjectDefinitionRelationship.from_json(json)
# print the JSON string representation of the object
print(CustomObjectDefinitionRelationship.to_json())

# convert the object into a dict
custom_object_definition_relationship_dict = custom_object_definition_relationship_instance.to_dict()
# create an instance of CustomObjectDefinitionRelationship from a dict
custom_object_definition_relationship_from_dict = CustomObjectDefinitionRelationship.from_dict(custom_object_definition_relationship_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


