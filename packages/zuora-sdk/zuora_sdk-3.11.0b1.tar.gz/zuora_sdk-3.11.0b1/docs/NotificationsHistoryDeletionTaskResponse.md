# NotificationsHistoryDeletionTaskResponse

The notification history deletion task information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the account whose notification histories are deleted by the current deletion task. | [optional] 
**created_by** | **str** | The ID of the user who submits the notification history deletion task. | [optional] 
**created_on** | **int** | The timestamp when the notification history deletion task is created. | [optional] 
**id** | **str** | The ID of the notification history deletion task. | [optional] 
**status** | [**NotificationsHistoryDeletionTaskResponseStatus**](NotificationsHistoryDeletionTaskResponseStatus.md) |  | [optional] 
**tenant_id** | **str** | The ID of the tenant where the notification history deletion task runs. | [optional] 

## Example

```python
from zuora_sdk.models.notifications_history_deletion_task_response import NotificationsHistoryDeletionTaskResponse

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationsHistoryDeletionTaskResponse from a JSON string
notifications_history_deletion_task_response_instance = NotificationsHistoryDeletionTaskResponse.from_json(json)
# print the JSON string representation of the object
print(NotificationsHistoryDeletionTaskResponse.to_json())

# convert the object into a dict
notifications_history_deletion_task_response_dict = notifications_history_deletion_task_response_instance.to_dict()
# create an instance of NotificationsHistoryDeletionTaskResponse from a dict
notifications_history_deletion_task_response_from_dict = NotificationsHistoryDeletionTaskResponse.from_dict(notifications_history_deletion_task_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


