# ChargeModelConfigurationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | The name of the field that is specified for a specific charge model.   Configuration keys supported are as follows:   * &#x60;formula&#x60; (only available if you have the Multi-Attribute Pricing charge model enabled. The charge model is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information.)  * &#x60;customFieldPerUnitRate&#x60; (only available if you have the Pre-Rated Per Unit Pricing charge model enabled. The charge model is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information.)  * &#x60;customFieldTotalAmount&#x60; (only available if you have the Pre-Rated Pricing model enabled. The charge model is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information.) | 
**value** | **str** | The value of the field that is specified in the &#x60;Key&#x60; field.   Possible values are follows:   * A valid pricing formula to calculate actual rating amount for each usage record. For example, &#x60;usageQuantity()*10&#x60;. Use it with Key &#x60;formula&#x60; when the Multi-Attribute Pricing charge model is used. The charge model is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information.  * A name of a usage custom field that carries the per-unit rate for a usage record. For example, &#x60;perUnitRate__c&#x60;. Use it with Key &#x60;customFieldPerUnitRate&#x60; when the Pre-Rated Per Unit Pricing charge model is used. The charge model is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information.  * A name of a usage custom field that carries the total amount for a usage record. For example, &#x60;totalAmount__c&#x60;. Use it with Key &#x60;customFieldTotalAmount&#x60; when the Pre-Rated Pricing model is used. The charge model is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information. | 

## Example

```python
from zuora_sdk.models.charge_model_configuration_item import ChargeModelConfigurationItem

# TODO update the JSON string below
json = "{}"
# create an instance of ChargeModelConfigurationItem from a JSON string
charge_model_configuration_item_instance = ChargeModelConfigurationItem.from_json(json)
# print the JSON string representation of the object
print(ChargeModelConfigurationItem.to_json())

# convert the object into a dict
charge_model_configuration_item_dict = charge_model_configuration_item_instance.to_dict()
# create an instance of ChargeModelConfigurationItem from a dict
charge_model_configuration_item_from_dict = ChargeModelConfigurationItem.from_dict(charge_model_configuration_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


