# CreateOmniChannelSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**subscription_id** | **str** | The system generated Id in Billing, the subscriptionId.  | [optional] 
**subscription_number** | **str** | The system generated subscription number.  | [optional] 
**account_id** | **str** | The ID of the account associated with this subscription.  | [optional] 
**account_number** | **str** | The number of the account associated with this subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.create_omni_channel_subscription_response import CreateOmniChannelSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOmniChannelSubscriptionResponse from a JSON string
create_omni_channel_subscription_response_instance = CreateOmniChannelSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(CreateOmniChannelSubscriptionResponse.to_json())

# convert the object into a dict
create_omni_channel_subscription_response_dict = create_omni_channel_subscription_response_instance.to_dict()
# create an instance of CreateOmniChannelSubscriptionResponse from a dict
create_omni_channel_subscription_response_from_dict = CreateOmniChannelSubscriptionResponse.from_dict(create_omni_channel_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


