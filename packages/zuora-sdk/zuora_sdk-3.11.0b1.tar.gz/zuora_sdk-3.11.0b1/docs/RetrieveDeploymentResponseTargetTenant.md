# RetrieveDeploymentResponseTargetTenant

When a deployment is retrieved it shows target tenant details.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Target tenant id. | [optional] 
**name** | **str** | Target tenant name. | [optional] 
**environment** | **str** | Target tenant environment. | [optional] 

## Example

```python
from zuora_sdk.models.retrieve_deployment_response_target_tenant import RetrieveDeploymentResponseTargetTenant

# TODO update the JSON string below
json = "{}"
# create an instance of RetrieveDeploymentResponseTargetTenant from a JSON string
retrieve_deployment_response_target_tenant_instance = RetrieveDeploymentResponseTargetTenant.from_json(json)
# print the JSON string representation of the object
print(RetrieveDeploymentResponseTargetTenant.to_json())

# convert the object into a dict
retrieve_deployment_response_target_tenant_dict = retrieve_deployment_response_target_tenant_instance.to_dict()
# create an instance of RetrieveDeploymentResponseTargetTenant from a dict
retrieve_deployment_response_target_tenant_from_dict = RetrieveDeploymentResponseTargetTenant.from_dict(retrieve_deployment_response_target_tenant_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


