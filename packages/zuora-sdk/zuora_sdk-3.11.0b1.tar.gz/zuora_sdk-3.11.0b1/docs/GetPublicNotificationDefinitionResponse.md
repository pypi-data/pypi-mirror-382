# GetPublicNotificationDefinitionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the notification definition. The default value is &#x60;true&#x60;. | [optional] 
**associated_account** | **str** | Indicates with which type of account this notification is associated.  | [optional] 
**callout** | [**GetPublicNotificationDefinitionResponseCallout**](GetPublicNotificationDefinitionResponseCallout.md) |  | [optional] 
**callout_active** | **bool** | The status of the callout action. The default value is &#x60;false&#x60;. | [optional] 
**communication_profile_id** | **str** | The profile that the notification definition belongs to. | [optional] 
**created_by** | **str** | The ID of the user who created the notification definition. | [optional] 
**created_on** | **str** | The time when the notification definition was created. Specified in the UTC timezone in the ISO860 format (YYYY-MM-DDThh:mm:ss.sTZD). E.g. 1997-07-16T19:20:30.45+00:00 | [optional] 
**description** | **str** | Description of the notification definition | [optional] 
**email_active** | **bool** | The status of the email action. The default value is &#x60;false&#x60;. | [optional] 
**email_template_id** | **str** | The ID of the email template. In the request, there should be at least one email template or callout. | [optional] 
**event_type_name** | **str** | The name of the event type. | [optional] 
**event_type_namespace** | **str** | The namespace of the &#x60;eventTypeName&#x60; field.   | [optional] 
**filter_rule** | [**GetPublicNotificationDefinitionResponseFilterRule**](GetPublicNotificationDefinitionResponseFilterRule.md) |  | [optional] 
**filter_rule_params** | **Dict[str, str]** | The parameter values used to configure the filter rule.  | [optional] 
**id** | **str** | The ID associated with this notification definition. | [optional] 
**name** | **str** | The name of the notification definition. | [optional] 
**updated_by** | **str** | The ID of the user who updated the notification definition. | [optional] 
**updated_on** | **str** | The time when the notification was updated. Specified in the UTC timezone in the ISO860 format (YYYY-MM-DDThh:mm:ss.sTZD). E.g. 1997-07-16T19:20:30.45+00:00 | [optional] 

## Example

```python
from zuora_sdk.models.get_public_notification_definition_response import GetPublicNotificationDefinitionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPublicNotificationDefinitionResponse from a JSON string
get_public_notification_definition_response_instance = GetPublicNotificationDefinitionResponse.from_json(json)
# print the JSON string representation of the object
print(GetPublicNotificationDefinitionResponse.to_json())

# convert the object into a dict
get_public_notification_definition_response_dict = get_public_notification_definition_response_instance.to_dict()
# create an instance of GetPublicNotificationDefinitionResponse from a dict
get_public_notification_definition_response_from_dict = GetPublicNotificationDefinitionResponse.from_dict(get_public_notification_definition_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


