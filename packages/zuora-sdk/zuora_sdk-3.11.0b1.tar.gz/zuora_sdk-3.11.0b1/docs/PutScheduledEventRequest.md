# PutScheduledEventRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | Indicate whether the scheduled event is active or inactive | [optional] 
**condition** | **str** | The filter rule conditions, written in [JEXL](http://commons.apache.org/proper/commons-jexl/). The scheduled event is triggered only if the condition is evaluated as true.  The rule might contain event context merge fields and data source merge fields. Data source merge fields must be from [the base object of the event or from the joined objects of the base object](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL#Data_Sources_and_Objects).  Scheduled events with invalid merge fields will fail to evaluate, thus will not be triggered. For example, to trigger an invoice due date scheduled event to only invoices with an amount over 1000, you would define the following condition:   &#x60;&#x60;&#x60;Invoice.Amount &gt; 1000&#x60;&#x60;&#x60;   &#x60;Invoice.Amount&#x60; refers to the &#x60;Amount&#x60; field of the Zuora object &#x60;Invoice&#x60;. | [optional] 
**description** | **str** | The description of the scheduled event. | [optional] 
**display_name** | **str** | The display name of the scheduled event. | [optional] 
**hours** | **int** | The scheduled time (hour) that the scheduled event notifications are sent. This time is based on the localized timezone of your tenant. | [optional] 
**minutes** | **int** | The scheduled time (minute) that the scheduled event notifications are sent. This time is based on the localized timezone of your tenant. | [optional] 
**parameters** | [**Dict[str, PostScheduledEventRequestParametersValue]**](PostScheduledEventRequestParametersValue.md) | The parameters of the filter rule. The names of the parameters must match with the filter rule and can&#39;t be duplicated. | [optional] 

## Example

```python
from zuora_sdk.models.put_scheduled_event_request import PutScheduledEventRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PutScheduledEventRequest from a JSON string
put_scheduled_event_request_instance = PutScheduledEventRequest.from_json(json)
# print the JSON string representation of the object
print(PutScheduledEventRequest.to_json())

# convert the object into a dict
put_scheduled_event_request_dict = put_scheduled_event_request_instance.to_dict()
# create an instance of PutScheduledEventRequest from a dict
put_scheduled_event_request_from_dict = PutScheduledEventRequest.from_dict(put_scheduled_event_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


