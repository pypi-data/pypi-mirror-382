# GetCalloutHistoryVOType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attempted_num** | **str** | The number of times the callout was retried.  | [optional] 
**create_time** | **str** | The time that the calloutHistory record was made.  | [optional] 
**event_category** | **str** | The event category for the callout.  | [optional] 
**event_context** | **str** | The context of the callout event.  | [optional] 
**notification** | **str** | The name of the notification.  | [optional] 
**request_method** | **str** | The request method set in notifications settings.  | [optional] 
**request_url** | **str** | The base url set in notifications settings.  | [optional] 
**response_code** | **str** | The responseCode of the request.  | [optional] 
**response_content** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.get_callout_history_vo_type import GetCalloutHistoryVOType

# TODO update the JSON string below
json = "{}"
# create an instance of GetCalloutHistoryVOType from a JSON string
get_callout_history_vo_type_instance = GetCalloutHistoryVOType.from_json(json)
# print the JSON string representation of the object
print(GetCalloutHistoryVOType.to_json())

# convert the object into a dict
get_callout_history_vo_type_dict = get_callout_history_vo_type_instance.to_dict()
# create an instance of GetCalloutHistoryVOType from a dict
get_callout_history_vo_type_from_dict = GetCalloutHistoryVOType.from_dict(get_callout_history_vo_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


