# DailyConsumptionRevRecRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**original_charge_id** | **str** | Original RPC ID  | 
**charge_segment_number** | **str** | RPC number  | [optional] 
**fund_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.daily_consumption_rev_rec_request import DailyConsumptionRevRecRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DailyConsumptionRevRecRequest from a JSON string
daily_consumption_rev_rec_request_instance = DailyConsumptionRevRecRequest.from_json(json)
# print the JSON string representation of the object
print(DailyConsumptionRevRecRequest.to_json())

# convert the object into a dict
daily_consumption_rev_rec_request_dict = daily_consumption_rev_rec_request_instance.to_dict()
# create an instance of DailyConsumptionRevRecRequest from a dict
daily_consumption_rev_rec_request_from_dict = DailyConsumptionRevRecRequest.from_dict(daily_consumption_rev_rec_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


