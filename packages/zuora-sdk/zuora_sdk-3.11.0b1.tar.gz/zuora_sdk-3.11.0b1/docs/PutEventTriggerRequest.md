# PutEventTriggerRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the trigger. | [optional] 
**condition** | **str** | The JEXL expression to be evaluated against object changes. See above for more information and an example. | [optional] 
**description** | **str** | The description of the trigger. | [optional] 
**event_type** | [**PutEventTriggerRequestEventType**](PutEventTriggerRequestEventType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.put_event_trigger_request import PutEventTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PutEventTriggerRequest from a JSON string
put_event_trigger_request_instance = PutEventTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(PutEventTriggerRequest.to_json())

# convert the object into a dict
put_event_trigger_request_dict = put_event_trigger_request_instance.to_dict()
# create an instance of PutEventTriggerRequest from a dict
put_event_trigger_request_from_dict = PutEventTriggerRequest.from_dict(put_event_trigger_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


