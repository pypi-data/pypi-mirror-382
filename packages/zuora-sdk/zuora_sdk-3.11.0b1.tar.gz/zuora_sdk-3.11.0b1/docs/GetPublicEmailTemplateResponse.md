# GetPublicEmailTemplateResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the email template. | [optional] 
**bcc_email_address** | **str** | Email BCC address. | [optional] 
**cc_email_address** | **str** | Email CC address. | [optional] 
**cc_email_type** | [**GetPublicEmailTemplateResponseCcEmailType**](GetPublicEmailTemplateResponseCcEmailType.md) |  | [optional] [default to GetPublicEmailTemplateResponseCcEmailType.SPECIFICEMAILS]
**created_by** | **str** | The ID of the user who created the email template. | [optional] 
**created_on** | **datetime** | The time when the email template was created. Specified in the UTC timezone in the ISO860 format (YYYY-MM-DDThh:mm:ss.sTZD). E.g. 1997-07-16T19:20:30.45+00:00 | [optional] 
**description** | **str** | The description of the email template. | [optional] 
**email_body** | **str** | The email body. You can add merge fields in the email object using angle brackets.  User can also embed html tags if &#x60;isHtml&#x60; is &#x60;true&#x60;. | [optional] 
**email_subject** | **str** | The email subject. You can add merge fields in the email subject using angle brackets. | [optional] 
**encoding_type** | [**GetPublicEmailTemplateResponseEncodingType**](GetPublicEmailTemplateResponseEncodingType.md) |  | [optional] 
**event_category** | **float** | The event category code for a standard event. See [Standard Event Categories](https://knowledgecenter.zuora.com/Central_Platform/Notifications/A_Standard_Events/Standard_Event_Category_Code_for_Notification_Histories_API) for all event category codes. | [optional] 
**event_type_name** | **str** | The name of the custom event or custom scheduled event. | [optional] 
**event_type_namespace** | **str** | The namespace of the &#x60;eventTypeName&#x60; field for custom events and custom scheduled events.   | [optional] 
**from_email_address** | **str** | If formEmailType is SpecificEmail, this field is required. | [optional] 
**from_email_type** | [**GetPublicEmailTemplateResponseFromEmailType**](GetPublicEmailTemplateResponseFromEmailType.md) |  | [optional] 
**from_name** | **str** | The name of email sender. | [optional] 
**id** | **str** | The email template ID. | [optional] 
**is_html** | **bool** | Indicates whether the style of email body is HTML. | [optional] 
**name** | **str** | The name of the email template. | [optional] 
**reply_to_email_address** | **str** | If replyToEmailType is SpecificEmail, this field is required | [optional] 
**reply_to_email_type** | [**GetPublicEmailTemplateResponseReplyToEmailType**](GetPublicEmailTemplateResponseReplyToEmailType.md) |  | [optional] 
**to_email_address** | **str** | If &#x60;toEmailType&#x60; is &#x60;SpecificEmail&#x60;, this field is required. | [optional] 
**to_email_type** | [**GetPublicEmailTemplateResponseToEmailType**](GetPublicEmailTemplateResponseToEmailType.md) |  | [optional] 
**updated_by** | **str** | The ID of the user who updated the email template. | [optional] 
**updated_on** | **datetime** | The time when the email template was updated. Specified in the UTC timezone in the ISO860 format (YYYY-MM-DDThh:mm:ss.sTZD). E.g. 1997-07-16T19:20:30.45+00:00 | [optional] 

## Example

```python
from zuora_sdk.models.get_public_email_template_response import GetPublicEmailTemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPublicEmailTemplateResponse from a JSON string
get_public_email_template_response_instance = GetPublicEmailTemplateResponse.from_json(json)
# print the JSON string representation of the object
print(GetPublicEmailTemplateResponse.to_json())

# convert the object into a dict
get_public_email_template_response_dict = get_public_email_template_response_instance.to_dict()
# create an instance of GetPublicEmailTemplateResponse from a dict
get_public_email_template_response_from_dict = GetPublicEmailTemplateResponse.from_dict(get_public_email_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


