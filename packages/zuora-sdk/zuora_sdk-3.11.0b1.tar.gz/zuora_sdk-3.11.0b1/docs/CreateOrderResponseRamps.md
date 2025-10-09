# CreateOrderResponseRamps


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ramp_number** | **str** | The number of the ramp definition. | [optional] 
**subscription_number** | **str** | The number of the subscription that this ramp deal definition is applied to. | [optional] 

## Example

```python
from zuora_sdk.models.create_order_response_ramps import CreateOrderResponseRamps

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResponseRamps from a JSON string
create_order_response_ramps_instance = CreateOrderResponseRamps.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResponseRamps.to_json())

# convert the object into a dict
create_order_response_ramps_dict = create_order_response_ramps_instance.to_dict()
# create an instance of CreateOrderResponseRamps from a dict
create_order_response_ramps_from_dict = CreateOrderResponseRamps.from_dict(create_order_response_ramps_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


