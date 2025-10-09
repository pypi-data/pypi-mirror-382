# GetQueryEmailTemplates200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | **str** | The URI to query the next page of data, e.g. &#39;/notification-definitions?start&#x3D;1&amp;limit&#x3D;10&#39;. The start equals request&#39;s start+limit, and the limit equals the request&#39;s limit. If the current page is the last page, this value is null. | [optional] 
**data** | [**List[GetPublicEmailTemplateResponse]**](GetPublicEmailTemplateResponse.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_query_email_templates200_response import GetQueryEmailTemplates200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetQueryEmailTemplates200Response from a JSON string
get_query_email_templates200_response_instance = GetQueryEmailTemplates200Response.from_json(json)
# print the JSON string representation of the object
print(GetQueryEmailTemplates200Response.to_json())

# convert the object into a dict
get_query_email_templates200_response_dict = get_query_email_templates200_response_instance.to_dict()
# create an instance of GetQueryEmailTemplates200Response from a dict
get_query_email_templates200_response_from_dict = GetQueryEmailTemplates200Response.from_dict(get_query_email_templates200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


