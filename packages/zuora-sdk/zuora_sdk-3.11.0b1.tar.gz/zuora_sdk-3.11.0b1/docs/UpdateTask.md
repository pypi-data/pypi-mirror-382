# UpdateTask

A task. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action_type** | **str** | The type of task.  | [optional] 
**call_type** | **str** | The type of the API used.  | [optional] 
**concurrent_limit** | **int** | The maximum number of this task that can run concurrently.  | [optional] 
**id** | **int** | The unique ID of the task.  | 
**name** | **str** | The name of the task.  | [optional] 
**object** | **str** | The selected object for the task.  | [optional] 
**object_id** | **str** | The ID of the selected object of the task.  | [optional] 
**status** | [**UpdateTaskStatus**](UpdateTaskStatus.md) |  | [optional] 
**tags** | **List[str]** | The array of filter tags.  | [optional] 
**workflow_id** | **int** | The ID of the workflow the task belongs to.  | [optional] 

## Example

```python
from zuora_sdk.models.update_task import UpdateTask

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateTask from a JSON string
update_task_instance = UpdateTask.from_json(json)
# print the JSON string representation of the object
print(UpdateTask.to_json())

# convert the object into a dict
update_task_dict = update_task_instance.to_dict()
# create an instance of UpdateTask from a dict
update_task_from_dict = UpdateTask.from_dict(update_task_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


