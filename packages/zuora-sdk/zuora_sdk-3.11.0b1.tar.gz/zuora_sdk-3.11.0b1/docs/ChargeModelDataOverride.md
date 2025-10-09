# ChargeModelDataOverride

Container for charge model configuration data.   **Note**: This field is only available if you have the High Water Mark, Pre-Rated Pricing, or Multi-Attribute Pricing charge models enabled. The High Water Mark and Pre-Rated Pricing charge models are available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_model_configuration** | [**ChargeModelConfigurationForSubscription**](ChargeModelConfigurationForSubscription.md) |  | [optional] 
**quantity** | **float** | Number of units purchased. This field is used if the Multi-Attribute Pricing formula uses the &#x60;quantity()&#x60; function.   This field is only available for one-time and recurring charges that use the Multi-Attribute Pricing charge model. | [optional] 
**tiers** | [**List[ChargeTier]**](ChargeTier.md) | List of cumulative pricing tiers in the charge.   **Note**: When you override the tiers of a usage-based charge using High Water Mark Pricing charge model, you have to provide all of the tiers, including the ones you do not want to change. The new tiers will completely override the previous ones. The High Water Mark Pricing charge models are available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information. | [optional] 

## Example

```python
from zuora_sdk.models.charge_model_data_override import ChargeModelDataOverride

# TODO update the JSON string below
json = "{}"
# create an instance of ChargeModelDataOverride from a JSON string
charge_model_data_override_instance = ChargeModelDataOverride.from_json(json)
# print the JSON string representation of the object
print(ChargeModelDataOverride.to_json())

# convert the object into a dict
charge_model_data_override_dict = charge_model_data_override_instance.to_dict()
# create an instance of ChargeModelDataOverride from a dict
charge_model_data_override_from_dict = ChargeModelDataOverride.from_dict(charge_model_data_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


