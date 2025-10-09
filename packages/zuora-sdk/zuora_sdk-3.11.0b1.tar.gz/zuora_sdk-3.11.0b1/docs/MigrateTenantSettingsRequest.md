# MigrateTenantSettingsRequest

Request to add a new Template migration. TemplateMigrationClientRequest object contains request details of target tenant, source tenant, and template information needed for migration. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comments** | **str** |  | [optional] 
**description** | **str** | Description of the migration. | 
**email_ids** | **str** | List of Emails with comma separator. | [optional] 
**entity_uuid** | **str** | Entity UUID | 
**meta_data** | **object** | Json node object contains metadata. | [optional] 
**name** | **str** | Name of the migration. | 
**request** | [**List[MigrationComponentContent]**](MigrationComponentContent.md) | List of settings need to be migrated. | [optional] 
**send_email** | **bool** | Flag determines whether or not to send an email. | 

## Example

```python
from zuora_sdk.models.migrate_tenant_settings_request import MigrateTenantSettingsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MigrateTenantSettingsRequest from a JSON string
migrate_tenant_settings_request_instance = MigrateTenantSettingsRequest.from_json(json)
# print the JSON string representation of the object
print(MigrateTenantSettingsRequest.to_json())

# convert the object into a dict
migrate_tenant_settings_request_dict = migrate_tenant_settings_request_instance.to_dict()
# create an instance of MigrateTenantSettingsRequest from a dict
migrate_tenant_settings_request_from_dict = MigrateTenantSettingsRequest.from_dict(migrate_tenant_settings_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


