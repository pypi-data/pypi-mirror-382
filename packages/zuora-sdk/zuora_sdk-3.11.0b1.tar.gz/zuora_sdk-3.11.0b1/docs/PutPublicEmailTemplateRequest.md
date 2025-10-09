# PutPublicEmailTemplateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the email template. | [optional] 
**bcc_email_address** | **str** | Email bcc address. | [optional] 
**cc_email_address** | **str** | Email cc address. | [optional] 
**cc_email_type** | [**PutPublicEmailTemplateRequestCcEmailType**](PutPublicEmailTemplateRequestCcEmailType.md) |  | [optional] [default to PutPublicEmailTemplateRequestCcEmailType.SPECIFICEMAILS]
**description** | **str** | The description of the email template. | [optional] 
**email_body** | **str** | The email body. You can add merge fields in the email object using angle brackets.  User can also embed html tags if &#x60;isHtml&#x60; is &#x60;true&#x60;. | [optional] 
**email_subject** | **str** | The email subject. You can add merge fields in the email subject using angle brackets. | [optional] 
**encoding_type** | [**PutPublicEmailTemplateRequestEncodingType**](PutPublicEmailTemplateRequestEncodingType.md) |  | [optional] 
**from_email_address** | **str** | If fromEmailType is SpecificEmail, this field is required | [optional] 
**from_email_type** | [**PutPublicEmailTemplateRequestFromEmailType**](PutPublicEmailTemplateRequestFromEmailType.md) |  | [optional] 
**from_name** | **str** | The name of email sender. | [optional] 
**is_html** | **bool** | Indicates whether the style of email body is HTML. | [optional] 
**name** | **str** | The name of the email template. | [optional] 
**reply_to_email_address** | **str** | If replyToEmailType is SpecificEmail, this field is required. | [optional] 
**reply_to_email_type** | [**PutPublicEmailTemplateRequestReplyToEmailType**](PutPublicEmailTemplateRequestReplyToEmailType.md) |  | [optional] 
**to_email_address** | **str** | If toEmailType is SpecificEmail, this field is required. | [optional] 
**to_email_type** | [**PutPublicEmailTemplateRequestToEmailType**](PutPublicEmailTemplateRequestToEmailType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.put_public_email_template_request import PutPublicEmailTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PutPublicEmailTemplateRequest from a JSON string
put_public_email_template_request_instance = PutPublicEmailTemplateRequest.from_json(json)
# print the JSON string representation of the object
print(PutPublicEmailTemplateRequest.to_json())

# convert the object into a dict
put_public_email_template_request_dict = put_public_email_template_request_instance.to_dict()
# create an instance of PutPublicEmailTemplateRequest from a dict
put_public_email_template_request_from_dict = PutPublicEmailTemplateRequest.from_dict(put_public_email_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


