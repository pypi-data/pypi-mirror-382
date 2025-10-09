# CreateOrUpdateEmailTemplatesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reasons** | **List[str]** | Returns an empty array if the request succeeds.  | [optional] 

## Example

```python
from zuora_sdk.models.create_or_update_email_templates_response import CreateOrUpdateEmailTemplatesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrUpdateEmailTemplatesResponse from a JSON string
create_or_update_email_templates_response_instance = CreateOrUpdateEmailTemplatesResponse.from_json(json)
# print the JSON string representation of the object
print(CreateOrUpdateEmailTemplatesResponse.to_json())

# convert the object into a dict
create_or_update_email_templates_response_dict = create_or_update_email_templates_response_instance.to_dict()
# create an instance of CreateOrUpdateEmailTemplatesResponse from a dict
create_or_update_email_templates_response_from_dict = CreateOrUpdateEmailTemplatesResponse.from_dict(create_or_update_email_templates_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


