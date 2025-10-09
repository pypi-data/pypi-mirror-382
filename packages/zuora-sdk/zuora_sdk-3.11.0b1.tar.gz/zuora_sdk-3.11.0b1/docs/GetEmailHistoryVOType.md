# GetEmailHistoryVOType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | ID of an account.  | [optional] 
**bcc** | **str** | Blind carbon copy recipients of the email.  | [optional] 
**cc** | **str** | Carbon Copy recipients of the email.  | [optional] 
**error_message** | **str** | null if the content of result is \&quot;OK\&quot;. A description of the error if the content of result is not \&quot;OK\&quot;. | [optional] 
**event_category** | **str** | The event category of the email.  | [optional] 
**from_email** | **str** | The sender of the email.  | [optional] 
**notification** | **str** | The name of the notification.  | [optional] 
**reply_to** | **str** | The reply-to address as configured in the email template.  | [optional] 
**result** | **str** | The result from the mail server of sending the email.  | [optional] 
**send_time** | **str** | The date and time the email was sent.  | [optional] 
**subject** | **str** | The subject of the email.  | [optional] 
**to_email** | **str** | The intended recipient of the email.  | [optional] 

## Example

```python
from zuora_sdk.models.get_email_history_vo_type import GetEmailHistoryVOType

# TODO update the JSON string below
json = "{}"
# create an instance of GetEmailHistoryVOType from a JSON string
get_email_history_vo_type_instance = GetEmailHistoryVOType.from_json(json)
# print the JSON string representation of the object
print(GetEmailHistoryVOType.to_json())

# convert the object into a dict
get_email_history_vo_type_dict = get_email_history_vo_type_instance.to_dict()
# create an instance of GetEmailHistoryVOType from a dict
get_email_history_vo_type_from_dict = GetEmailHistoryVOType.from_dict(get_email_history_vo_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


