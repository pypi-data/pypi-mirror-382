# RetrieveDeploymentResponseSkippedInner

When a deployment is retrieved it shows failed components.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**component** | **str** | Component name. | [optional] 
**sub_component** | **str** | Subcomponent name. | [optional] 
**key** | **str** | Key to identify a particular migration data. | [optional] 
**reason** | **str** | The rationale behind the non-migration of specific data. | [optional] 

## Example

```python
from zuora_sdk.models.retrieve_deployment_response_skipped_inner import RetrieveDeploymentResponseSkippedInner

# TODO update the JSON string below
json = "{}"
# create an instance of RetrieveDeploymentResponseSkippedInner from a JSON string
retrieve_deployment_response_skipped_inner_instance = RetrieveDeploymentResponseSkippedInner.from_json(json)
# print the JSON string representation of the object
print(RetrieveDeploymentResponseSkippedInner.to_json())

# convert the object into a dict
retrieve_deployment_response_skipped_inner_dict = retrieve_deployment_response_skipped_inner_instance.to_dict()
# create an instance of RetrieveDeploymentResponseSkippedInner from a dict
retrieve_deployment_response_skipped_inner_from_dict = RetrieveDeploymentResponseSkippedInner.from_dict(retrieve_deployment_response_skipped_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


