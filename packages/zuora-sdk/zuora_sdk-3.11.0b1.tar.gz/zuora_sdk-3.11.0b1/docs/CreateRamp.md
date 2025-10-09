# CreateRamp

Container of the ramp definitions. It is used to create, update, or remove the ramp definition for the new subscription.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charges** | [**List[RampChargeRequest]**](RampChargeRequest.md) | Container for the rate plan charges that are considered as part of the ramp deal.   * If this field is not specified, all the one-time and recurring regular charges of the new subscription are automatically considered as part of the ramp deal.  * If this field is specified, either &#39;chargeNumber&#39; or &#39;uniqueToken&#39; must be specified. | [optional] 
**delete** | **bool** | Whether to remove the ramp definition from the new subscription. If you want to remove the ramp definition, this field is the only required field for the &#x60;ramp&#x60; object.   | [optional] 
**description** | **str** | The short description of the ramp. | [optional] 
**intervals** | [**List[RampIntervalRequest]**](RampIntervalRequest.md) | Container for the intervals that the ramp is split into in its timeline.    It is required when you want to create or update the ramp definition. The ramp intervals cannot have any overlap or gap between each other. | [optional] 
**name** | **str** | The name of the ramp. | [optional] 

## Example

```python
from zuora_sdk.models.create_ramp import CreateRamp

# TODO update the JSON string below
json = "{}"
# create an instance of CreateRamp from a JSON string
create_ramp_instance = CreateRamp.from_json(json)
# print the JSON string representation of the object
print(CreateRamp.to_json())

# convert the object into a dict
create_ramp_dict = create_ramp_instance.to_dict()
# create an instance of CreateRamp from a dict
create_ramp_from_dict = CreateRamp.from_dict(create_ramp_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


