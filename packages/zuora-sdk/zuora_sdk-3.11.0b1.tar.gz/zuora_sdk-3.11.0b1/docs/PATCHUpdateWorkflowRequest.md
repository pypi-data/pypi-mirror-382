# PATCHUpdateWorkflowRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the workflow definition  | [optional] 
**description** | **str** | The description of the workflow defintion  | [optional] 
**active_workflow_version_id** | **int** | The id of a version. This version will then be set to the active version of the workflow definition. | [optional] 
**status** | **str** | Can be &#x60;Active&#x60; or &#x60;Inactive&#x60;. Active workfow definitions run like normal. Inactive workflow definitions cannot be run. | [optional] 

## Example

```python
from zuora_sdk.models.patch_update_workflow_request import PATCHUpdateWorkflowRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PATCHUpdateWorkflowRequest from a JSON string
patch_update_workflow_request_instance = PATCHUpdateWorkflowRequest.from_json(json)
# print the JSON string representation of the object
print(PATCHUpdateWorkflowRequest.to_json())

# convert the object into a dict
patch_update_workflow_request_dict = patch_update_workflow_request_instance.to_dict()
# create an instance of PATCHUpdateWorkflowRequest from a dict
patch_update_workflow_request_from_dict = PATCHUpdateWorkflowRequest.from_dict(patch_update_workflow_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


