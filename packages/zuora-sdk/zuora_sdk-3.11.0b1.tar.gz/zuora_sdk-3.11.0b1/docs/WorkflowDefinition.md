# WorkflowDefinition

A workflow. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active_version** | [**WorkflowDefinitionActiveVersion**](WorkflowDefinitionActiveVersion.md) |  | [optional] 
**callout_trigger** | **bool** | Indicates whether the callout trigger is enabled for the retrieved workflow. | [optional] 
**created_at** | **str** | The date and time when the workflow is created, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format. | [optional] 
**description** | **str** | The description of the workflow definition.  | [optional] 
**id** | **int** | The unique ID of the workflow definition.  | [optional] 
**interval** | **str** | The schedule of the workflow, in a CRON expression. Returns null if the schedued trigger is disabled. | [optional] 
**name** | **str** | The name of the workflow definition.  | [optional] 
**ondemand_trigger** | **bool** | Indicates whether the ondemand trigger is enabled for the workflow.  | [optional] 
**scheduled_trigger** | **bool** | Indicates whether the scheduled trigger is enabled for the workflow.  | [optional] 
**status** | **str** | The status of the workflow definition.  | [optional] 
**timezone** | **str** | The timezone that is configured for the scheduler of the workflow. Returns null if the scheduled trigger is disabled. | [optional] 
**updated_at** | **str** | The date and time when the workflow is updated the last time, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format. | [optional] 

## Example

```python
from zuora_sdk.models.workflow_definition import WorkflowDefinition

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDefinition from a JSON string
workflow_definition_instance = WorkflowDefinition.from_json(json)
# print the JSON string representation of the object
print(WorkflowDefinition.to_json())

# convert the object into a dict
workflow_definition_dict = workflow_definition_instance.to_dict()
# create an instance of WorkflowDefinition from a dict
workflow_definition_from_dict = WorkflowDefinition.from_dict(workflow_definition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


