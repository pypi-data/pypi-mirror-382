# GetSubscriptionChangeLogsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**subscriptions** | [**List[SubscriptionChangeLog]**](SubscriptionChangeLog.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_subscription_change_logs_response import GetSubscriptionChangeLogsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetSubscriptionChangeLogsResponse from a JSON string
get_subscription_change_logs_response_instance = GetSubscriptionChangeLogsResponse.from_json(json)
# print the JSON string representation of the object
print(GetSubscriptionChangeLogsResponse.to_json())

# convert the object into a dict
get_subscription_change_logs_response_dict = get_subscription_change_logs_response_instance.to_dict()
# create an instance of GetSubscriptionChangeLogsResponse from a dict
get_subscription_change_logs_response_from_dict = GetSubscriptionChangeLogsResponse.from_dict(get_subscription_change_logs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


