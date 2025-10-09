# GetScheduledEventResponseParametersValue

Definition of a filter rule parameter.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description of the parameter. | [optional] 
**display_name** | **str** | The display name of the parameter. | [optional] 
**options** | **List[str]** | The option values of the parameter. | [optional] 
**value_type** | **str** | The type of the value. | [optional] 

## Example

```python
from zuora_sdk.models.get_scheduled_event_response_parameters_value import GetScheduledEventResponseParametersValue

# TODO update the JSON string below
json = "{}"
# create an instance of GetScheduledEventResponseParametersValue from a JSON string
get_scheduled_event_response_parameters_value_instance = GetScheduledEventResponseParametersValue.from_json(json)
# print the JSON string representation of the object
print(GetScheduledEventResponseParametersValue.to_json())

# convert the object into a dict
get_scheduled_event_response_parameters_value_dict = get_scheduled_event_response_parameters_value_instance.to_dict()
# create an instance of GetScheduledEventResponseParametersValue from a dict
get_scheduled_event_response_parameters_value_from_dict = GetScheduledEventResponseParametersValue.from_dict(get_scheduled_event_response_parameters_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


