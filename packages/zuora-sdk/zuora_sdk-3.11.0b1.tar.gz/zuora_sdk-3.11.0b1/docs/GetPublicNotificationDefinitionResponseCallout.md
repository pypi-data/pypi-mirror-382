# GetPublicNotificationDefinitionResponseCallout


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the callout. The default value is &#x60;true&#x60;. | [optional] [default to True]
**callout_auth** | [**CalloutAuth**](CalloutAuth.md) |  | [optional] 
**callout_baseurl** | **str** | The callout URL. It must start with &#39;https://&#39; | [optional] 
**callout_params** | **Dict[str, str]** | A key-value map of merge fields of this callout.  | [optional] 
**callout_retry** | **bool** | Specified whether to retry the callout when the callout fails. The default value is &#x60;true&#x60;. | [optional] [default to True]
**description** | **str** | Description for the callout. | [optional] 
**event_type_name** | **str** | The name of the custom event type. | [optional] 
**http_method** | [**GetPublicNotificationDefinitionResponseCalloutHttpMethod**](GetPublicNotificationDefinitionResponseCalloutHttpMethod.md) |  | [optional] 
**id** | **str** | The ID of the callout. If &#x60;calloutActive&#x60; is &#x60;true&#x60;, a callout is required. The eventTypeName of the callout MUST be the same as the eventTypeName. | [optional] 
**name** | **str** | The name of the created callout. | [optional] 
**required_auth** | **bool** | Specifies whether the callout requires auth. | [optional] 
**created_by** | **str** | The user who created the notification definition. | [optional] 
**updated_on** | **str** | The time when the notification was updated. Specified in the UTC timezone in the ISO860 format (YYYY-MM-DDThh:mm:ss.sTZD). E.g. 1997-07-16T19:20:30.45+00:00 | [optional] 

## Example

```python
from zuora_sdk.models.get_public_notification_definition_response_callout import GetPublicNotificationDefinitionResponseCallout

# TODO update the JSON string below
json = "{}"
# create an instance of GetPublicNotificationDefinitionResponseCallout from a JSON string
get_public_notification_definition_response_callout_instance = GetPublicNotificationDefinitionResponseCallout.from_json(json)
# print the JSON string representation of the object
print(GetPublicNotificationDefinitionResponseCallout.to_json())

# convert the object into a dict
get_public_notification_definition_response_callout_dict = get_public_notification_definition_response_callout_instance.to_dict()
# create an instance of GetPublicNotificationDefinitionResponseCallout from a dict
get_public_notification_definition_response_callout_from_dict = GetPublicNotificationDefinitionResponseCallout.from_dict(get_public_notification_definition_response_callout_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


