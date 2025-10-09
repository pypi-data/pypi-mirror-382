# PutTasksRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[UpdateTask]**](UpdateTask.md) | The list of tasks to update.  | [optional] 

## Example

```python
from zuora_sdk.models.put_tasks_request import PutTasksRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PutTasksRequest from a JSON string
put_tasks_request_instance = PutTasksRequest.from_json(json)
# print the JSON string representation of the object
print(PutTasksRequest.to_json())

# convert the object into a dict
put_tasks_request_dict = put_tasks_request_instance.to_dict()
# create an instance of PutTasksRequest from a dict
put_tasks_request_from_dict = PutTasksRequest.from_dict(put_tasks_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


