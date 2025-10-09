# GetWorkflowResponseTasks

An object containing task counts. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **int** | The number of tasks in **Error** state.  | [optional] 
**pending** | **int** | The number of tasks in **Pending** state.  | [optional] 
**processing** | **int** | The number of tasks in **Processing** state.  | [optional] 
**queued** | **int** | The number of tasks in **Queued** state.  | [optional] 
**stopped** | **int** | The number of tasks in **Stopped** state.  | [optional] 
**success** | **int** | The number of tasks in **Success** state.  | [optional] 
**total** | **int** | The total number of tasks.  | [optional] 

## Example

```python
from zuora_sdk.models.get_workflow_response_tasks import GetWorkflowResponseTasks

# TODO update the JSON string below
json = "{}"
# create an instance of GetWorkflowResponseTasks from a JSON string
get_workflow_response_tasks_instance = GetWorkflowResponseTasks.from_json(json)
# print the JSON string representation of the object
print(GetWorkflowResponseTasks.to_json())

# convert the object into a dict
get_workflow_response_tasks_dict = get_workflow_response_tasks_instance.to_dict()
# create an instance of GetWorkflowResponseTasks from a dict
get_workflow_response_tasks_from_dict = GetWorkflowResponseTasks.from_dict(get_workflow_response_tasks_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


