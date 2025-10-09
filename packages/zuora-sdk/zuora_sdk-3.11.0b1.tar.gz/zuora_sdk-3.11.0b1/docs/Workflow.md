# Workflow

A workflow. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**callout_trigger** | **bool** | Indicates whether the callout trigger is enabled for the retrieved workflow.  | [optional] 
**created_at** | **str** | The date and time when the workflow is created, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format.  | [optional] 
**description** | **str** | The description of the workflow.  | [optional] 
**id** | **int** | The unique ID of the workflow.  | [optional] 
**interval** | **str** | The schedule of the workflow, in a CRON expression. Returns null if the schedued trigger is disabled.  | [optional] 
**name** | **str** | The name of the workflow.  | [optional] 
**ondemand_trigger** | **bool** | Indicates whether the ondemand trigger is enabled for the workflow.  | [optional] 
**scheduled_trigger** | **bool** | Indicates whether the scheduled trigger is enabled for the workflow.  | [optional] 
**timezone** | **str** | The timezone that is configured for the scheduler of the workflow. Returns null if the scheduled trigger is disabled.  | [optional] 
**type** | [**WorkflowType**](WorkflowType.md) |  | [optional] 
**updated_at** | **str** | The date and time when the workflow is updated the last time, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format.  | [optional] 
**version** | **str** | The version number of the workflow.   | [optional] 

## Example

```python
from zuora_sdk.models.workflow import Workflow

# TODO update the JSON string below
json = "{}"
# create an instance of Workflow from a JSON string
workflow_instance = Workflow.from_json(json)
# print the JSON string representation of the object
print(Workflow.to_json())

# convert the object into a dict
workflow_dict = workflow_instance.to_dict()
# create an instance of Workflow from a dict
workflow_from_dict = Workflow.from_dict(workflow_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


