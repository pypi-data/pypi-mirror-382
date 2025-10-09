# PutPublicNotificationDefinitionRequestCallout


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the callout. The default value is &#x60;true&#x60;. | [optional] [default to True]
**callout_auth** | [**CalloutAuth**](CalloutAuth.md) |  | [optional] 
**callout_baseurl** | **str** | The callout URL. It must start with &#39;https://&#39; | 
**callout_params** | **Dict[str, str]** | A key-value map of merge fields of this callout.  | [optional] 
**callout_retry** | **bool** | Specified whether to retry the callout when the callout fails. The default value is &#x60;true&#x60;. | [optional] [default to True]
**description** | **str** | Description for the callout. | [optional] 
**http_method** | [**PutPublicNotificationDefinitionRequestCalloutHttpMethod**](PutPublicNotificationDefinitionRequestCalloutHttpMethod.md) |  | 
**name** | **str** | The name of the created callout. | 
**required_auth** | **bool** | Specifies whether the callout requires auth. | 

## Example

```python
from zuora_sdk.models.put_public_notification_definition_request_callout import PutPublicNotificationDefinitionRequestCallout

# TODO update the JSON string below
json = "{}"
# create an instance of PutPublicNotificationDefinitionRequestCallout from a JSON string
put_public_notification_definition_request_callout_instance = PutPublicNotificationDefinitionRequestCallout.from_json(json)
# print the JSON string representation of the object
print(PutPublicNotificationDefinitionRequestCallout.to_json())

# convert the object into a dict
put_public_notification_definition_request_callout_dict = put_public_notification_definition_request_callout_instance.to_dict()
# create an instance of PutPublicNotificationDefinitionRequestCallout from a dict
put_public_notification_definition_request_callout_from_dict = PutPublicNotificationDefinitionRequestCallout.from_dict(put_public_notification_definition_request_callout_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


