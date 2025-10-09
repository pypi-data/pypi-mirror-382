# DeliveryScheduleProductRatePlanCharge


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**frequency** | [**DeliveryFrequency**](DeliveryFrequency.md) |  | [optional] 
**friday** | **bool** | The flag to indicate should the delivery happen on Friday  | [optional] 
**monday** | **bool** | The flag to indicate should the delivery happen on Monday  | [optional] 
**saturday** | **bool** | The flag to indicate should the delivery happen on Saturday  | [optional] 
**sunday** | **bool** | The flag to indicate should the delivery happen on Sunday  | [optional] 
**thursday** | **bool** | The flag to indicate should the delivery happen on Thursday  | [optional] 
**tuesday** | **bool** | The flag to indicate should the delivery happen on Tuesday  | [optional] 
**wendesday** | **bool** | The flag to indicate should the delivery happen on Wendesday  | [optional] 

## Example

```python
from zuora_sdk.models.delivery_schedule_product_rate_plan_charge import DeliveryScheduleProductRatePlanCharge

# TODO update the JSON string below
json = "{}"
# create an instance of DeliveryScheduleProductRatePlanCharge from a JSON string
delivery_schedule_product_rate_plan_charge_instance = DeliveryScheduleProductRatePlanCharge.from_json(json)
# print the JSON string representation of the object
print(DeliveryScheduleProductRatePlanCharge.to_json())

# convert the object into a dict
delivery_schedule_product_rate_plan_charge_dict = delivery_schedule_product_rate_plan_charge_instance.to_dict()
# create an instance of DeliveryScheduleProductRatePlanCharge from a dict
delivery_schedule_product_rate_plan_charge_from_dict = DeliveryScheduleProductRatePlanCharge.from_dict(delivery_schedule_product_rate_plan_charge_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


