# GatewayOptions

The field used to pass gateway-specific parameters and parameter values. The fields supported by gateways vary. For more information, see the Overview topic of each gateway integration in [Zuora Knowledge Center](https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Payments/M_Payment_Gateways/Supported_Payment_Gateways).   Zuora sends all the information that you specified to the gateway. If you specify any unsupported gateway option parameters, they will be ignored without error prompts.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | The name of a gateway-specific parameter.  | [optional] 
**value** | **str** | The value of the gateway-specific parameter.  | [optional] 

## Example

```python
from zuora_sdk.models.gateway_options import GatewayOptions

# TODO update the JSON string below
json = "{}"
# create an instance of GatewayOptions from a JSON string
gateway_options_instance = GatewayOptions.from_json(json)
# print the JSON string representation of the object
print(GatewayOptions.to_json())

# convert the object into a dict
gateway_options_dict = gateway_options_instance.to_dict()
# create an instance of GatewayOptions from a dict
gateway_options_from_dict = GatewayOptions.from_dict(gateway_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


