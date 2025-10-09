# GetWorkflowResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cpu_time** | **str** | The overall CPU time for the execution of the workflow.  | [optional] 
**created_at** | **str** | The date and time when the workflow is created, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format..  | [optional] 
**finished_at** | **str** | The date and time when the execution of the workflow completes, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format.  | [optional] 
**id** | **int** | The unique ID of the workflow.  | [optional] 
**messages** | **object** | Messages from tasks.   **Note:** This field is only returned in Production.  | [optional] 
**name** | **str** | The unique run number of the workflow.  | [optional] 
**original_workflow_id** | **str** | The ID of the workflow setup.  | [optional] 
**run_time** | **float** | The execution time of the workflow including the waiting time, in seconds.  | [optional] 
**status** | [**GetWorkflowResponseStatus**](GetWorkflowResponseStatus.md) |  | [optional] 
**tasks** | [**GetWorkflowResponseTasks**](GetWorkflowResponseTasks.md) |  | [optional] 
**type** | **str** | The type of the current workflow. Possible values:   - &#x60;Workflow::Setup&#x60;: The workflow is a setup and is used for creating workflow instances.   - &#x60;Workflow::Instance&#x60;: The workflow is an execution that has data.  | [optional] 
**updated_at** | **str** | The date and time when the workflow is updated the last time, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format.  | [optional] 

## Example

```python
from zuora_sdk.models.get_workflow_response import GetWorkflowResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetWorkflowResponse from a JSON string
get_workflow_response_instance = GetWorkflowResponse.from_json(json)
# print the JSON string representation of the object
print(GetWorkflowResponse.to_json())

# convert the object into a dict
get_workflow_response_dict = get_workflow_response_instance.to_dict()
# create an instance of GetWorkflowResponse from a dict
get_workflow_response_from_dict = GetWorkflowResponse.from_dict(get_workflow_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


