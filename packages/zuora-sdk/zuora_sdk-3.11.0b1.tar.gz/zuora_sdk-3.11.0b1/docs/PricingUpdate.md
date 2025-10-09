# PricingUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_model_data** | [**ChargeModelDataOverride**](ChargeModelDataOverride.md) | Container for charge model configuration data.   **Note**: This field is only available if you have the High Water Mark, Pre-Rated Pricing, or Multi-Attribute Pricing charge models enabled. The High Water Mark and Pre-Rated Pricing charge models are available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information. | [optional] 
**discount** | [**DiscountPricingUpdate**](DiscountPricingUpdate.md) | Pricing information about a discount charge.  | [optional] 
**recurring_delivery** | [**RecurringDeliveryPricingUpdate**](RecurringDeliveryPricingUpdate.md) | Pricing information about a recurring charge that uses the \&quot;delivery\&quot; charge model. This field is only available if you have the Delivery Pricing charge model enabled.   **Note**: The Delivery Pricing charge model is in the **Early Adopter** phase. We are actively soliciting feedback from a small set of early adopters before releasing it as generally available. If you want to join this early adopter program, submit a request at &lt;a href&#x3D;\&quot;http://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;. | [optional] 
**recurring_flat_fee** | [**RecurringFlatFeePricingUpdate**](RecurringFlatFeePricingUpdate.md) | Pricing information about a recurring charge that uses the \&quot;flat fee\&quot; charge model. In this charge model, the charge has a fixed price. | [optional] 
**recurring_per_unit** | [**RecurringPerUnitPricingUpdate**](RecurringPerUnitPricingUpdate.md) | Pricing information about a recurring charge that uses the \&quot;per unit\&quot; charge model. In this charge model, the charge has a fixed price per unit purchased. | [optional] 
**recurring_tiered** | [**RecurringTieredPricingUpdate**](RecurringTieredPricingUpdate.md) | Pricing information about a recurring charge that uses the \&quot;tiered pricing\&quot; charge model. In this charge model, the charge has cumulative pricing tiers that become effective as units are purchased. | [optional] 
**recurring_volume** | [**RecurringVolumePricingUpdate**](RecurringVolumePricingUpdate.md) | Pricing information about a recurring charge that uses the \&quot;volume pricing\&quot; charge model. In this charge model, the charge has a variable price per unit, depending on how many units are purchased. | [optional] 
**usage_flat_fee** | [**UsageFlatFeePricingUpdate**](UsageFlatFeePricingUpdate.md) | Pricing information about a usage charge that uses the \&quot;flat fee\&quot; charge model. In this charge model, the charge has a fixed price. | [optional] 
**usage_overage** | [**UsageOveragePricingUpdate**](UsageOveragePricingUpdate.md) | Pricing information about a usage charge that uses the \&quot;overage\&quot; charge model. In this charge model, the charge has an allowance of free units and a fixed price per additional unit consumed. | [optional] 
**usage_per_unit** | [**UsagePerUnitPricingUpdate**](UsagePerUnitPricingUpdate.md) | Pricing information about a usage charge that uses the \&quot;per unit\&quot; charge model. In this charge model, the charge has a fixed price per unit consumed. | [optional] 
**usage_tiered** | [**UsageTieredPricingUpdate**](UsageTieredPricingUpdate.md) | Pricing information about a usage charge that uses the \&quot;tiered pricing\&quot; charge model. In this charge model, the charge has cumulative pricing tiers that become effective as units are consumed. | [optional] 
**usage_tiered_with_overage** | [**UsageTieredWithOveragePricingUpdate**](UsageTieredWithOveragePricingUpdate.md) | Pricing information about a usage charge that uses the \&quot;tiered with overage\&quot; charge model. In this charge model, the charge has cumulative pricing tiers that become effective as units are consumed. The charge also has a fixed price per unit consumed beyond the limit of the final tier. | [optional] 
**usage_volume** | [**UsageVolumePricingUpdate**](UsageVolumePricingUpdate.md) | Pricing information about a usage charge that uses the \&quot;volume pricing\&quot; charge model. In this charge model, the charge has a variable price per unit, depending on how many units are consumed. | [optional] 

## Example

```python
from zuora_sdk.models.pricing_update import PricingUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of PricingUpdate from a JSON string
pricing_update_instance = PricingUpdate.from_json(json)
# print the JSON string representation of the object
print(PricingUpdate.to_json())

# convert the object into a dict
pricing_update_dict = pricing_update_instance.to_dict()
# create an instance of PricingUpdate from a dict
pricing_update_from_dict = PricingUpdate.from_dict(pricing_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


