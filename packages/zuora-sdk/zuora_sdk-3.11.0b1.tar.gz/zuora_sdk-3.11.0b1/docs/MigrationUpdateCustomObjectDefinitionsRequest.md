# MigrationUpdateCustomObjectDefinitionsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actions** | [**List[CustomObjectDefinitionUpdateActionRequest]**](CustomObjectDefinitionUpdateActionRequest.md) | The actions of updating custom object definitions, to be performed as parts of the migration.  Currently only one action per migration is supported. | 

## Example

```python
from zuora_sdk.models.migration_update_custom_object_definitions_request import MigrationUpdateCustomObjectDefinitionsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MigrationUpdateCustomObjectDefinitionsRequest from a JSON string
migration_update_custom_object_definitions_request_instance = MigrationUpdateCustomObjectDefinitionsRequest.from_json(json)
# print the JSON string representation of the object
print(MigrationUpdateCustomObjectDefinitionsRequest.to_json())

# convert the object into a dict
migration_update_custom_object_definitions_request_dict = migration_update_custom_object_definitions_request_instance.to_dict()
# create an instance of MigrationUpdateCustomObjectDefinitionsRequest from a dict
migration_update_custom_object_definitions_request_from_dict = MigrationUpdateCustomObjectDefinitionsRequest.from_dict(migration_update_custom_object_definitions_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


