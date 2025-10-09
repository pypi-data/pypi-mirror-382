# DeliverySchedule

The `deliveryScheudule` is used for the Delivery Pricing charge model only.  To enable the Delivery Pricing charge model, submit a request at <a href=\"http://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a> and check **Delivery Pricing** in **Billing Settings** > **Enable Charge Types / Models**. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**frequency** | [**DeliveryFrequency**](DeliveryFrequency.md) |  | [optional] 
**monday** | **bool** | Indicates whether delivery occurs on Monday. | [optional] 
**tuesday** | **bool** | Indicates whether delivery occurs on Tuesday. | [optional] 
**wednesday** | **bool** | Indicates whether delivery occurs on Wednesday. | [optional] 
**thursday** | **bool** | Indicates whether delivery occurs on Thursday. | [optional] 
**friday** | **bool** | Indicates whether delivery occurs on Friday. | [optional] 
**saturday** | **bool** | Indicates whether delivery occurs on Saturday. | [optional] 
**sunday** | **bool** | Indicates whether delivery occurs on Sunday. | [optional] 

## Example

```python
from zuora_sdk.models.delivery_schedule import DeliverySchedule

# TODO update the JSON string below
json = "{}"
# create an instance of DeliverySchedule from a JSON string
delivery_schedule_instance = DeliverySchedule.from_json(json)
# print the JSON string representation of the object
print(DeliverySchedule.to_json())

# convert the object into a dict
delivery_schedule_dict = delivery_schedule_instance.to_dict()
# create an instance of DeliverySchedule from a dict
delivery_schedule_from_dict = DeliverySchedule.from_dict(delivery_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


