# GetSubscriptionChangeLogResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**subscription** | [**SubscriptionChangeLog**](SubscriptionChangeLog.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_subscription_change_log_response import GetSubscriptionChangeLogResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetSubscriptionChangeLogResponse from a JSON string
get_subscription_change_log_response_instance = GetSubscriptionChangeLogResponse.from_json(json)
# print the JSON string representation of the object
print(GetSubscriptionChangeLogResponse.to_json())

# convert the object into a dict
get_subscription_change_log_response_dict = get_subscription_change_log_response_instance.to_dict()
# create an instance of GetSubscriptionChangeLogResponse from a dict
get_subscription_change_log_response_from_dict = GetSubscriptionChangeLogResponse.from_dict(get_subscription_change_log_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


