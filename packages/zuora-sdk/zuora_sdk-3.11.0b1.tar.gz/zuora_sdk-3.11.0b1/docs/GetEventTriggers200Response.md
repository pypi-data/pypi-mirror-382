# GetEventTriggers200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[EventTrigger]**](EventTrigger.md) |  | [optional] 
**next** | **str** | The link to the next page. No value if it is last page. | [optional] 

## Example

```python
from zuora_sdk.models.get_event_triggers200_response import GetEventTriggers200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetEventTriggers200Response from a JSON string
get_event_triggers200_response_instance = GetEventTriggers200Response.from_json(json)
# print the JSON string representation of the object
print(GetEventTriggers200Response.to_json())

# convert the object into a dict
get_event_triggers200_response_dict = get_event_triggers200_response_instance.to_dict()
# create an instance of GetEventTriggers200Response from a dict
get_event_triggers200_response_from_dict = GetEventTriggers200Response.from_dict(get_event_triggers200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


