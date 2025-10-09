# RampChargeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | The number of the rate plan charge. | [optional] 

## Example

```python
from zuora_sdk.models.ramp_charge_response import RampChargeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RampChargeResponse from a JSON string
ramp_charge_response_instance = RampChargeResponse.from_json(json)
# print the JSON string representation of the object
print(RampChargeResponse.to_json())

# convert the object into a dict
ramp_charge_response_dict = ramp_charge_response_instance.to_dict()
# create an instance of RampChargeResponse from a dict
ramp_charge_response_from_dict = RampChargeResponse.from_dict(ramp_charge_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


