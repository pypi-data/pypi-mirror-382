# PostScheduledEventRequestParametersValue

Definition of a filter rule parameter.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description of the parameter. | [optional] 
**display_name** | **str** | The display name of the parameter. | [optional] 
**options** | **List[str]** | The option values of the parameter. | [optional] 
**value_type** | [**PostScheduledEventRequestParametersValueValueType**](PostScheduledEventRequestParametersValueValueType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.post_scheduled_event_request_parameters_value import PostScheduledEventRequestParametersValue

# TODO update the JSON string below
json = "{}"
# create an instance of PostScheduledEventRequestParametersValue from a JSON string
post_scheduled_event_request_parameters_value_instance = PostScheduledEventRequestParametersValue.from_json(json)
# print the JSON string representation of the object
print(PostScheduledEventRequestParametersValue.to_json())

# convert the object into a dict
post_scheduled_event_request_parameters_value_dict = post_scheduled_event_request_parameters_value_instance.to_dict()
# create an instance of PostScheduledEventRequestParametersValue from a dict
post_scheduled_event_request_parameters_value_from_dict = PostScheduledEventRequestParametersValue.from_dict(post_scheduled_event_request_parameters_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


