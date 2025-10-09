# PostCreateOrUpdateEmailTemplateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_partial_success** | **bool** | When set to &#x60;false&#x60;, the call will fail if one or multiple instances fail to import, and a &#x60;200&#x60; response is returned if all email templates have been successfully updated.  When set to &#x60;true&#x60;, a success (&#x60;200&#x60;) response is returned if one or more instances have imported successfully. All failed instances are also returned in the response. | [optional] 
**email_templates** | [**List[PostCreateOrUpdateEmailTemplateRequestFormat]**](PostCreateOrUpdateEmailTemplateRequestFormat.md) | A container for email templates.  | [optional] 

## Example

```python
from zuora_sdk.models.post_create_or_update_email_template_request import PostCreateOrUpdateEmailTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostCreateOrUpdateEmailTemplateRequest from a JSON string
post_create_or_update_email_template_request_instance = PostCreateOrUpdateEmailTemplateRequest.from_json(json)
# print the JSON string representation of the object
print(PostCreateOrUpdateEmailTemplateRequest.to_json())

# convert the object into a dict
post_create_or_update_email_template_request_dict = post_create_or_update_email_template_request_instance.to_dict()
# create an instance of PostCreateOrUpdateEmailTemplateRequest from a dict
post_create_or_update_email_template_request_from_dict = PostCreateOrUpdateEmailTemplateRequest.from_dict(post_create_or_update_email_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


