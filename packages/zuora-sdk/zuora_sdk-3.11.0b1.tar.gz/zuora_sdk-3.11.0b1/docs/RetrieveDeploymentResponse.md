# RetrieveDeploymentResponse

Response when deployment is retrieved.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the Deployment Manager migration process. | [optional] 
**status** | **str** | Status of the Deployment Manager migration. | [optional] 
**name** | **str** | Name of the migration. | [optional] 
**description** | **str** | Description of the migration. | [optional] 
**run_by** | **str** | Name of the user who executed the migration. | [optional] 
**start_time** | **str** | Deployment timestamp. | [optional] 
**target_tenant** | [**RetrieveDeploymentResponseTargetTenant**](RetrieveDeploymentResponseTargetTenant.md) |  | [optional] 
**succeeded** | [**List[RetrieveDeploymentResponseSucceededInner]**](RetrieveDeploymentResponseSucceededInner.md) | List of succeeded components. | [optional] 
**failed** | [**List[RetrieveDeploymentResponseFailedInner]**](RetrieveDeploymentResponseFailedInner.md) | List of failed components. | [optional] 
**skipped** | [**List[RetrieveDeploymentResponseSkippedInner]**](RetrieveDeploymentResponseSkippedInner.md) | List of skipped components. | [optional] 

## Example

```python
from zuora_sdk.models.retrieve_deployment_response import RetrieveDeploymentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RetrieveDeploymentResponse from a JSON string
retrieve_deployment_response_instance = RetrieveDeploymentResponse.from_json(json)
# print the JSON string representation of the object
print(RetrieveDeploymentResponse.to_json())

# convert the object into a dict
retrieve_deployment_response_dict = retrieve_deployment_response_instance.to_dict()
# create an instance of RetrieveDeploymentResponse from a dict
retrieve_deployment_response_from_dict = RetrieveDeploymentResponse.from_dict(retrieve_deployment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


