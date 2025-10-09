# TasksResponsePagination

An object containing pagination information for the list of tasks returned by the API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | A string containing the URL where the next page of data can be retrieved.  | [optional] 
**page** | **int** | An integer denoting the current page number.  | [optional] 
**page_length** | **int** | An integer denoting the number of tasks in this response. The maximum value is 100. | [optional] 

## Example

```python
from zuora_sdk.models.tasks_response_pagination import TasksResponsePagination

# TODO update the JSON string below
json = "{}"
# create an instance of TasksResponsePagination from a JSON string
tasks_response_pagination_instance = TasksResponsePagination.from_json(json)
# print the JSON string representation of the object
print(TasksResponsePagination.to_json())

# convert the object into a dict
tasks_response_pagination_dict = tasks_response_pagination_instance.to_dict()
# create an instance of TasksResponsePagination from a dict
tasks_response_pagination_from_dict = TasksResponsePagination.from_dict(tasks_response_pagination_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


