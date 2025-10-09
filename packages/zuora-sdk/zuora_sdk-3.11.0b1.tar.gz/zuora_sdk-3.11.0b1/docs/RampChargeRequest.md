# RampChargeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | The number of the rate plan charge. | [optional] 
**unique_token** | **str** | Unique identifier for the charge. This identifier enables you to refer to the charge before the charge has an internal identifier in Zuora. | [optional] 

## Example

```python
from zuora_sdk.models.ramp_charge_request import RampChargeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RampChargeRequest from a JSON string
ramp_charge_request_instance = RampChargeRequest.from_json(json)
# print the JSON string representation of the object
print(RampChargeRequest.to_json())

# convert the object into a dict
ramp_charge_request_dict = ramp_charge_request_instance.to_dict()
# create an instance of RampChargeRequest from a dict
ramp_charge_request_from_dict = RampChargeRequest.from_dict(ramp_charge_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


