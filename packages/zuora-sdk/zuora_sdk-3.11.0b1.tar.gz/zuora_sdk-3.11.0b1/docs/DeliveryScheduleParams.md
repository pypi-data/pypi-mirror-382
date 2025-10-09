# DeliveryScheduleParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**frequency** | [**DeliveryScheduleFrequency**](DeliveryScheduleFrequency.md) |  | [optional] 
**friday** | **bool** | Indicates whether delivery on friday.  | [optional] 
**monday** | **bool** | Indicates whether delivery on monday.  | [optional] 
**saturday** | **bool** | Indicates whether delivery on saturday.  | [optional] 
**sunday** | **bool** | Indicates whether delivery on sunday.  | [optional] 
**thursday** | **bool** | Indicates whether delivery on thursday.  | [optional] 
**tuesday** | **bool** | Indicates whether delivery on tuesday.  | [optional] 
**wednesday** | **bool** | Indicates whether delivery on wednesday.  | [optional] 

## Example

```python
from zuora_sdk.models.delivery_schedule_params import DeliveryScheduleParams

# TODO update the JSON string below
json = "{}"
# create an instance of DeliveryScheduleParams from a JSON string
delivery_schedule_params_instance = DeliveryScheduleParams.from_json(json)
# print the JSON string representation of the object
print(DeliveryScheduleParams.to_json())

# convert the object into a dict
delivery_schedule_params_dict = delivery_schedule_params_instance.to_dict()
# create an instance of DeliveryScheduleParams from a dict
delivery_schedule_params_from_dict = DeliveryScheduleParams.from_dict(delivery_schedule_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


