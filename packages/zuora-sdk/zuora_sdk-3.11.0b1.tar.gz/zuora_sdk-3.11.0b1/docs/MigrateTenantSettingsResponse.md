# MigrateTenantSettingsResponse

Response after migration is added.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email_ids** | **str** | List of Emails with comma separator  | [optional] 
**environment** | **str** | Environment information | [optional] 
**id** | **str** | Variable to hold the job ID. | 
**migrated_by** | **str** | User responsible for migration. | 
**migration_description** | **str** | Description of the migration. | 
**migration_end** | **str** | Timestamp when migration ended. | 
**migration_name** | **str** | Name of the migration. | 
**migration_start** | **str** | Timestamp when migration started. | 
**response** | [**List[MigrationComponentContent]**](MigrationComponentContent.md) |  | [optional] 
**source_tenant_description** | **str** | Source Tenant Description. | 
**source_tenant_name** | **str** | Source Tenant Name. | 
**status** | **str** | Status of the Migration Job. | 
**type** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.migrate_tenant_settings_response import MigrateTenantSettingsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MigrateTenantSettingsResponse from a JSON string
migrate_tenant_settings_response_instance = MigrateTenantSettingsResponse.from_json(json)
# print the JSON string representation of the object
print(MigrateTenantSettingsResponse.to_json())

# convert the object into a dict
migrate_tenant_settings_response_dict = migrate_tenant_settings_response_instance.to_dict()
# create an instance of MigrateTenantSettingsResponse from a dict
migrate_tenant_settings_response_from_dict = MigrateTenantSettingsResponse.from_dict(migrate_tenant_settings_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


