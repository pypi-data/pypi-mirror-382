# DetailedWorkflow

A workflow. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**call_type** | **str** | The call type of the active workflow version.  | [optional] 
**callout_trigger** | **bool** | Indicates whether the callout trigger is enabled for the retrieved workflow.  | [optional] 
**created_at** | **str** | The date and time when the workflow is created, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format.  | [optional] 
**description** | **str** | The description of the workflow.  | [optional] 
**finished_at** | **str** | The date and time when the instance of the workflow version finished at.  | [optional] 
**id** | **int** | The unique ID of the workflow.  | [optional] 
**interval** | **str** | The schedule of the workflow, in a CRON expression. Returns null if the schedued trigger is disabled.  | [optional] 
**name** | **str** | The name of the workflow.  | [optional] 
**ondemand_trigger** | **bool** | Indicates whether the ondemand trigger is enabled for the workflow.  | [optional] 
**original_workflow_id** | **int** | The unique ID of the original workflow version.  | [optional] 
**priority** | **str** | The priority of the active workflow version.   | [optional] 
**scheduled_trigger** | **bool** | Indicates whether the scheduled trigger is enabled for the workflow.  | [optional] 
**started_at** | **str** | The date and time when the instance of the workflow version started at.  | [optional] 
**status** | **int** | The status of the active workflow version.  | [optional] 
**sync_trigger** | **bool** | Indicates whether the workflow version is enabled for the sync mode.  | [optional] 
**timezone** | **str** | The timezone that is configured for the scheduler of the workflow. Returns null if the scheduled trigger is disabled.  | [optional] 
**type** | [**DetailedWorkflowType**](DetailedWorkflowType.md) |  | [optional] 
**updated_at** | **str** | The date and time when the workflow is updated the last time, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format.  | [optional] 
**version** | **str** | The version number of the active workflow version.              | [optional] 

## Example

```python
from zuora_sdk.models.detailed_workflow import DetailedWorkflow

# TODO update the JSON string below
json = "{}"
# create an instance of DetailedWorkflow from a JSON string
detailed_workflow_instance = DetailedWorkflow.from_json(json)
# print the JSON string representation of the object
print(DetailedWorkflow.to_json())

# convert the object into a dict
detailed_workflow_dict = detailed_workflow_instance.to_dict()
# create an instance of DetailedWorkflow from a dict
detailed_workflow_from_dict = DetailedWorkflow.from_dict(detailed_workflow_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


