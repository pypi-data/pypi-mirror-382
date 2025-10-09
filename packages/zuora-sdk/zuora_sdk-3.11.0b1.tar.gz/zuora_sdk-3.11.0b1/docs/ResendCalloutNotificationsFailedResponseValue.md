# ResendCalloutNotificationsFailedResponseValue

The ID of a fail-to-resend callout notification history object, containing an object with the error code and message.   **Note:** Multiple records of this field are allowed in the response. Each of them represents a fail-to-resend callout notification history.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The error code of response.  | [optional] 
**message** | **str** | The detail information of the error response | [optional] 

## Example

```python
from zuora_sdk.models.resend_callout_notifications_failed_response_value import ResendCalloutNotificationsFailedResponseValue

# TODO update the JSON string below
json = "{}"
# create an instance of ResendCalloutNotificationsFailedResponseValue from a JSON string
resend_callout_notifications_failed_response_value_instance = ResendCalloutNotificationsFailedResponseValue.from_json(json)
# print the JSON string representation of the object
print(ResendCalloutNotificationsFailedResponseValue.to_json())

# convert the object into a dict
resend_callout_notifications_failed_response_value_dict = resend_callout_notifications_failed_response_value_instance.to_dict()
# create an instance of ResendCalloutNotificationsFailedResponseValue from a dict
resend_callout_notifications_failed_response_value_from_dict = ResendCalloutNotificationsFailedResponseValue.from_dict(resend_callout_notifications_failed_response_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


