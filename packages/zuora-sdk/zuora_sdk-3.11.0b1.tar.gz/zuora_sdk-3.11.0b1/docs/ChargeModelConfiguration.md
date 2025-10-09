# ChargeModelConfiguration

Container for charge model configuration data.  **Notes**:   - This field is only available if you have the Pre-Rated Pricing or Multi-Attribute Pricing charge models enabled. These charge models are available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information.   - To use this field, you must set the `X-Zuora-WSDL-Version` request header to `102` or later. Otherwise, an error occurs with \"Code: INVALID_VALUE\". 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**configuration_item** | [**List[ChargeModelConfigurationItem]**](ChargeModelConfigurationItem.md) | An array of Charge Model Configuration Key-Value pairs.  | [optional] 

## Example

```python
from zuora_sdk.models.charge_model_configuration import ChargeModelConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of ChargeModelConfiguration from a JSON string
charge_model_configuration_instance = ChargeModelConfiguration.from_json(json)
# print the JSON string representation of the object
print(ChargeModelConfiguration.to_json())

# convert the object into a dict
charge_model_configuration_dict = charge_model_configuration_instance.to_dict()
# create an instance of ChargeModelConfiguration from a dict
charge_model_configuration_from_dict = ChargeModelConfiguration.from_dict(charge_model_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


