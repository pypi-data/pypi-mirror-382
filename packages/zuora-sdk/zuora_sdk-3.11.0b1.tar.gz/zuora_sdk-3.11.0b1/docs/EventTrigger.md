# EventTrigger


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the trigger. | [optional] 
**base_object** | **str** | The base object that the trigger rule is defined upon. Should be specified in the pattern: ^[A-Z][\\\\w\\\\-]*$ | [optional] 
**condition** | **str** | The JEXL expression to be evaluated against object changes. See above for more information and an example. | [optional] 
**description** | **str** | The description of the trigger. | [optional] 
**event_type** | [**EventType**](EventType.md) |  | [optional] 
**id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.event_trigger import EventTrigger

# TODO update the JSON string below
json = "{}"
# create an instance of EventTrigger from a JSON string
event_trigger_instance = EventTrigger.from_json(json)
# print the JSON string representation of the object
print(EventTrigger.to_json())

# convert the object into a dict
event_trigger_dict = event_trigger_instance.to_dict()
# create an instance of EventTrigger from a dict
event_trigger_from_dict = EventTrigger.from_dict(event_trigger_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


