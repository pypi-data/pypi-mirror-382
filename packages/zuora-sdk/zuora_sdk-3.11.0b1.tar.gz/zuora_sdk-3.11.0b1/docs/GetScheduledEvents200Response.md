# GetScheduledEvents200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[GetScheduledEventResponse]**](GetScheduledEventResponse.md) |  | [optional] 
**next** | **str** | The link to the next page. No value if it is last page. | [optional] 

## Example

```python
from zuora_sdk.models.get_scheduled_events200_response import GetScheduledEvents200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetScheduledEvents200Response from a JSON string
get_scheduled_events200_response_instance = GetScheduledEvents200Response.from_json(json)
# print the JSON string representation of the object
print(GetScheduledEvents200Response.to_json())

# convert the object into a dict
get_scheduled_events200_response_dict = get_scheduled_events200_response_instance.to_dict()
# create an instance of GetScheduledEvents200Response from a dict
get_scheduled_events200_response_from_dict = GetScheduledEvents200Response.from_dict(get_scheduled_events200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


