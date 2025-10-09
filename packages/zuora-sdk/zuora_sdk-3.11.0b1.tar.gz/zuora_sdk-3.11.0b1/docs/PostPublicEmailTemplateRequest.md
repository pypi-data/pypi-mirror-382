# PostPublicEmailTemplateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the email template. The default value is &#x60;true&#x60;. | [optional] [default to True]
**bcc_email_address** | **str** | The email bcc address. | [optional] 
**cc_email_address** | **str** | The email CC address. | [optional] 
**cc_email_type** | [**PostPublicEmailTemplateRequestCcEmailType**](PostPublicEmailTemplateRequestCcEmailType.md) |  | [optional] [default to PostPublicEmailTemplateRequestCcEmailType.SPECIFICEMAILS]
**description** | **str** | The description of the email template. | [optional] 
**email_body** | **str** | The email body. You can add merge fields in the email object using angle brackets.  You can also embed HTML tags if &#x60;isHtml&#x60; is &#x60;true&#x60;. | 
**email_subject** | **str** | The email subject. Users can add merge fields in the email subject using angle brackets. | 
**encoding_type** | [**PostPublicEmailTemplateRequestEncodingType**](PostPublicEmailTemplateRequestEncodingType.md) |  | [optional] [default to PostPublicEmailTemplateRequestEncodingType.UTF8]
**event_category** | **float** | If you specify this field, the email template is created based on a standard event. See [Standard Event Categories](https://knowledgecenter.zuora.com/Central_Platform/Notifications/A_Standard_Events/Standard_Event_Category_Code_for_Notification_Histories_API) for all standard event category codes.   | [optional] 
**event_type_name** | **str** | The name of the custom event or custom scheduled event. If you specify this field, the email template is created based on the corresponding custom event or custom scheduled event.  | [optional] 
**event_type_namespace** | **str** | The namespace of the &#x60;eventTypeName&#x60; field. The &#x60;eventTypeName&#x60; has the &#x60;user.notification&#x60; namespace by default.   Note that if the &#x60;eventTypeName&#x60; is a standard event type, you must specify the &#x60;com.zuora.notification&#x60; namespace; otherwise, you will get an error.  For example, if you want to create an email template on the &#x60;OrderActionProcessed&#x60; event, you must specify &#x60;com.zuora.notification&#x60; for this field.           | [optional] 
**from_email_address** | **str** | If fromEmailType is SpecificEmail, this field is required. | [optional] 
**from_email_type** | [**PostPublicEmailTemplateRequestFromEmailType**](PostPublicEmailTemplateRequestFromEmailType.md) |  | 
**from_name** | **str** | The name of the email sender. | [optional] 
**is_html** | **bool** | Indicates whether the style of email body is HTML. The default value is &#x60;false&#x60;. | [optional] [default to False]
**name** | **str** | The name of the email template, a unique name in a tenant. | 
**reply_to_email_address** | **str** | If replyToEmailType is SpecificEmail, this field is required. | [optional] 
**reply_to_email_type** | [**PostPublicEmailTemplateRequestReplyToEmailType**](PostPublicEmailTemplateRequestReplyToEmailType.md) |  | [optional] 
**to_email_address** | **str** | If toEmailType is SpecificEmail, this field is required. | [optional] 
**to_email_type** | [**PostPublicEmailTemplateRequestToEmailType**](PostPublicEmailTemplateRequestToEmailType.md) |  | 

## Example

```python
from zuora_sdk.models.post_public_email_template_request import PostPublicEmailTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostPublicEmailTemplateRequest from a JSON string
post_public_email_template_request_instance = PostPublicEmailTemplateRequest.from_json(json)
# print the JSON string representation of the object
print(PostPublicEmailTemplateRequest.to_json())

# convert the object into a dict
post_public_email_template_request_dict = post_public_email_template_request_instance.to_dict()
# create an instance of PostPublicEmailTemplateRequest from a dict
post_public_email_template_request_from_dict = PostPublicEmailTemplateRequest.from_dict(post_public_email_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


