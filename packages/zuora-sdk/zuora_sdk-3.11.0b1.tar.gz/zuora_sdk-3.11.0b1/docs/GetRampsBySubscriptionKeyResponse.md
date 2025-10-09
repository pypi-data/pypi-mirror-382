# GetRampsBySubscriptionKeyResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**ramps** | [**List[RampResponse]**](RampResponse.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_ramps_by_subscription_key_response import GetRampsBySubscriptionKeyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetRampsBySubscriptionKeyResponse from a JSON string
get_ramps_by_subscription_key_response_instance = GetRampsBySubscriptionKeyResponse.from_json(json)
# print the JSON string representation of the object
print(GetRampsBySubscriptionKeyResponse.to_json())

# convert the object into a dict
get_ramps_by_subscription_key_response_dict = get_ramps_by_subscription_key_response_instance.to_dict()
# create an instance of GetRampsBySubscriptionKeyResponse from a dict
get_ramps_by_subscription_key_response_from_dict = GetRampsBySubscriptionKeyResponse.from_dict(get_ramps_by_subscription_key_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


