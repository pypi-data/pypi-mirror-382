# GetScheduledEventResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | Indicate whether the scheduled event is active or inactive | [optional] 
**api_field** | **str** | The base field of the base object in the &#x60;apiObject&#x60; field, should be in date or timestamp format. The scheduled event notifications are triggered based on this date and the event parameters (before or after a specified number of days) from notification definitions. Should be specified in the pattern: ^[A-Z][\\\\w\\\\-]*$ | [optional] 
**api_object** | **str** | The base object that the scheduled event is defined upon. The base object should contain a date or timestamp format field. Should be specified in the pattern: ^[A-Z][\\\\w\\\\-]*$ | [optional] 
**condition** | **str** | The filter rule conditions, written in [JEXL](http://commons.apache.org/proper/commons-jexl/). The scheduled event is triggered only if the condition is evaluated as true.  The rule might contain event context merge fields and data source merge fields. Data source merge fields must be from [the base object of the event or from the joined objects of the base object](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL#Data_Sources_and_Objects).  Scheduled events with invalid merge fields will fail to evaluate, thus will not be triggered. For example, to trigger an invoice due date scheduled event to only invoices with an amount over 1000, you would define the following condition:   &#x60;&#x60;&#x60;Invoice.Amount &gt; 1000&#x60;&#x60;&#x60;   &#x60;Invoice.Amount&#x60; refers to the &#x60;Amount&#x60; field of the Zuora object &#x60;Invoice&#x60;. | [optional] 
**cron_expression** | **str** | The cron expression defines the time when scheduled event notifications will be sent. | [optional] 
**description** | **str** | The description of the scheduled event. | [optional] 
**display_name** | **str** | The display name of the scheduled event. | [optional] 
**id** | **str** | Scheduled event ID. | [optional] 
**name** | **str** | The name of the scheduled event. | [optional] 
**namespace** | **str** | The namespace of the scheduled event name in the &#x60;name&#x60; field. | [optional] 
**parameters** | [**Dict[str, GetScheduledEventResponseParametersValue]**](GetScheduledEventResponseParametersValue.md) | The parameter definitions of the filter rule. The names of the parameters must match with the filter rule and can&#39;t be duplicated. You should specify all the parameters when creating scheduled event notifications. | [optional] 

## Example

```python
from zuora_sdk.models.get_scheduled_event_response import GetScheduledEventResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetScheduledEventResponse from a JSON string
get_scheduled_event_response_instance = GetScheduledEventResponse.from_json(json)
# print the JSON string representation of the object
print(GetScheduledEventResponse.to_json())

# convert the object into a dict
get_scheduled_event_response_dict = get_scheduled_event_response_instance.to_dict()
# create an instance of GetScheduledEventResponse from a dict
get_scheduled_event_response_from_dict = GetScheduledEventResponse.from_dict(get_scheduled_event_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


