# Bi3ViewsTaskStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task_state** | **str** | The current state of the task. | [optional] 

## Example

```python
from zuora_sdk.models.bi3_views_task_status_response import Bi3ViewsTaskStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of Bi3ViewsTaskStatusResponse from a JSON string
bi3_views_task_status_response_instance = Bi3ViewsTaskStatusResponse.from_json(json)
# print the JSON string representation of the object
print(Bi3ViewsTaskStatusResponse.to_json())

# convert the object into a dict
bi3_views_task_status_response_dict = bi3_views_task_status_response_instance.to_dict()
# create an instance of Bi3ViewsTaskStatusResponse from a dict
bi3_views_task_status_response_from_dict = Bi3ViewsTaskStatusResponse.from_dict(bi3_views_task_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


