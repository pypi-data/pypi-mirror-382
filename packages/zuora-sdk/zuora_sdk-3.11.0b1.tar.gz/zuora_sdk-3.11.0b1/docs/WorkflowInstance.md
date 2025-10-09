# WorkflowInstance

A instance workflow object.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **str** | The date and time when the workflow is created, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format.  | [optional] 
**id** | **int** | The unique ID of the workflow.  | [optional] 
**name** | **str** | The run number of this workflow instance  | [optional] 
**original_workflow_id** | **int** | The identifier of the workflow template that is used to create this instance.  | [optional] 
**status** | [**WorkflowInstanceStatus**](WorkflowInstanceStatus.md) |  | [optional] 
**updated_at** | **str** | The date and time the last time when the workflow is updated, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format.  | [optional] 

## Example

```python
from zuora_sdk.models.workflow_instance import WorkflowInstance

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowInstance from a JSON string
workflow_instance_instance = WorkflowInstance.from_json(json)
# print the JSON string representation of the object
print(WorkflowInstance.to_json())

# convert the object into a dict
workflow_instance_dict = workflow_instance_instance.to_dict()
# create an instance of WorkflowInstance from a dict
workflow_instance_from_dict = WorkflowInstance.from_dict(workflow_instance_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


