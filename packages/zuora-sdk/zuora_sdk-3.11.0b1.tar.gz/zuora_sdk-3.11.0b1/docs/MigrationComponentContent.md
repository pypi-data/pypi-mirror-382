# MigrationComponentContent

When a comparison is made between a source and target tenant, it sends a response to the user interface.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attribute** | **str** |  | [optional] 
**component_type** | **str** | Type of selected components to be migrated. | [optional] 
**current_target_response** | **object** | Json node object contains metadata. | [optional] 
**description** | **str** |  | [optional] 
**disabled** | **str** |  | [optional] 
**error_message** | **str** | Error information. | [optional] 
**http_methods** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**key** | **str** |  | [optional] 
**migrated_on** | **datetime** | It is the time when migration is triggered. | [optional] 
**migration_id** | **str** | Migration ID. It is generated at the time of triggering deployment. | [optional] 
**path_pattern** | **str** | PathPattern of component. | [optional] 
**previous_target_response** | **object** | Json node object contains metadata. | [optional] 
**result** | **str** | Returns the result details of Components. | [optional] 
**segregation_key** | **str** | Displays the differences between components. | [optional] 
**source_response** | **object** | Json node object contains metadata. | [optional] 
**status** | **str** | Returns the status of each component. | [optional] 
**update_status** | **str** | Updated Status. | [optional] 

## Example

```python
from zuora_sdk.models.migration_component_content import MigrationComponentContent

# TODO update the JSON string below
json = "{}"
# create an instance of MigrationComponentContent from a JSON string
migration_component_content_instance = MigrationComponentContent.from_json(json)
# print the JSON string representation of the object
print(MigrationComponentContent.to_json())

# convert the object into a dict
migration_component_content_dict = migration_component_content_instance.to_dict()
# create an instance of MigrationComponentContent from a dict
migration_component_content_from_dict = MigrationComponentContent.from_dict(migration_component_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


