# RetrieveDeploymentResponseSucceededInner

When a deployment is retrieved it shows succeeded components.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**component** | **str** | Component name. | [optional] 
**sub_component** | **str** | Subcomponent name. | [optional] 
**key** | **str** | Key to identify a particular migration data. | [optional] 

## Example

```python
from zuora_sdk.models.retrieve_deployment_response_succeeded_inner import RetrieveDeploymentResponseSucceededInner

# TODO update the JSON string below
json = "{}"
# create an instance of RetrieveDeploymentResponseSucceededInner from a JSON string
retrieve_deployment_response_succeeded_inner_instance = RetrieveDeploymentResponseSucceededInner.from_json(json)
# print the JSON string representation of the object
print(RetrieveDeploymentResponseSucceededInner.to_json())

# convert the object into a dict
retrieve_deployment_response_succeeded_inner_dict = retrieve_deployment_response_succeeded_inner_instance.to_dict()
# create an instance of RetrieveDeploymentResponseSucceededInner from a dict
retrieve_deployment_response_succeeded_inner_from_dict = RetrieveDeploymentResponseSucceededInner.from_dict(retrieve_deployment_response_succeeded_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


