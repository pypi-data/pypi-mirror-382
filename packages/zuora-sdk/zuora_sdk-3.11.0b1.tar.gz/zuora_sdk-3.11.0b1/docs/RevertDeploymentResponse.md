# RevertDeploymentResponse

Response when deployment is reverted.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the Deployment Manager migration process.. | [optional] 
**status** | **str** | Status of the Deployment Manager migration. | [optional] 
**environment** | **str** | Environment of the Deployment Manager migration process. | [optional] 
**email_ids** | **str** | emailIds notified of the Deployment Manager migration process. | [optional] 
**product_catalog** | **bool** | Boolean flag specifies if the migration process includes product catalog module. | [optional] 
**name** | **str** | Name of the Deployment Manager migration process. | [optional] 
**description** | **str** | Description of the Deployment Manager migration process. | [optional] 
**source_tenant_description** | **str** | Source Tenant Description. | [optional] 
**source_tenant_name** | **str** | Source Tenant Name. | [optional] 
**type** | **str** | Type of the Deployment Manager migration process. | [optional] 
**migrated_by** | **str** | User who initiated the Deployment Manager migration process. | [optional] 
**end_time** | **str** | end timestamp of the Deployment Manager migration process. | [optional] 
**start_time** | **str** | start timestamp of the Deployment Manager migration process. | [optional] 

## Example

```python
from zuora_sdk.models.revert_deployment_response import RevertDeploymentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RevertDeploymentResponse from a JSON string
revert_deployment_response_instance = RevertDeploymentResponse.from_json(json)
# print the JSON string representation of the object
print(RevertDeploymentResponse.to_json())

# convert the object into a dict
revert_deployment_response_dict = revert_deployment_response_instance.to_dict()
# create an instance of RevertDeploymentResponse from a dict
revert_deployment_response_from_dict = RevertDeploymentResponse.from_dict(revert_deployment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


