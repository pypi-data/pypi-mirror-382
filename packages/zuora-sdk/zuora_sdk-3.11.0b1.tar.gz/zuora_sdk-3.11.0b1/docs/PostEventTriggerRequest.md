# PostEventTriggerRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the event trigger. | 
**base_object** | **str** | The base object that the trigger rule is defined upon. Should be specified in the pattern: ^[A-Z][\\\\w\\\\-]*$ | 
**condition** | **str** | The JEXL expression to be evaluated against object changes. See above for more information and an example. | 
**description** | **str** | The description of the event trigger. | [optional] 
**event_type** | [**EventType**](EventType.md) |  | 

## Example

```python
from zuora_sdk.models.post_event_trigger_request import PostEventTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostEventTriggerRequest from a JSON string
post_event_trigger_request_instance = PostEventTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(PostEventTriggerRequest.to_json())

# convert the object into a dict
post_event_trigger_request_dict = post_event_trigger_request_instance.to_dict()
# create an instance of PostEventTriggerRequest from a dict
post_event_trigger_request_from_dict = PostEventTriggerRequest.from_dict(post_event_trigger_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


