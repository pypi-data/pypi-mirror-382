# MigrationUpdateCustomObjectDefinitionsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actions** | [**List[CustomObjectDefinitionUpdateActionResponse]**](CustomObjectDefinitionUpdateActionResponse.md) | The actions of updating custom object definitions, to be performed as parts of the migration.  Currently only one action per migration is supported. | [optional] 

## Example

```python
from zuora_sdk.models.migration_update_custom_object_definitions_response import MigrationUpdateCustomObjectDefinitionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MigrationUpdateCustomObjectDefinitionsResponse from a JSON string
migration_update_custom_object_definitions_response_instance = MigrationUpdateCustomObjectDefinitionsResponse.from_json(json)
# print the JSON string representation of the object
print(MigrationUpdateCustomObjectDefinitionsResponse.to_json())

# convert the object into a dict
migration_update_custom_object_definitions_response_dict = migration_update_custom_object_definitions_response_instance.to_dict()
# create an instance of MigrationUpdateCustomObjectDefinitionsResponse from a dict
migration_update_custom_object_definitions_response_from_dict = MigrationUpdateCustomObjectDefinitionsResponse.from_dict(migration_update_custom_object_definitions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


