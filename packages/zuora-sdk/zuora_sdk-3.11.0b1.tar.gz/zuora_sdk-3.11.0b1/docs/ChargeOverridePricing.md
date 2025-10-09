# ChargeOverridePricing

Pricing information about the charge. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_model_data** | [**ChargeModelDataOverride**](ChargeModelDataOverride.md) |  | [optional] 
**discount** | [**DiscountPricingOverride**](DiscountPricingOverride.md) |  | [optional] 
**one_time_flat_fee** | [**OneTimeFlatFeePricingOverride**](OneTimeFlatFeePricingOverride.md) |  | [optional] 
**one_time_per_unit** | [**OneTimePerUnitPricingOverride**](OneTimePerUnitPricingOverride.md) |  | [optional] 
**one_time_tiered** | [**OneTimeTieredPricingOverride**](OneTimeTieredPricingOverride.md) |  | [optional] 
**one_time_volume** | [**OneTimeVolumePricingOverride**](OneTimeVolumePricingOverride.md) |  | [optional] 
**recurring_delivery** | [**RecurringDeliveryPricingOverride**](RecurringDeliveryPricingOverride.md) |  | [optional] 
**recurring_flat_fee** | [**RecurringFlatFeePricingOverride**](RecurringFlatFeePricingOverride.md) |  | [optional] 
**recurring_per_unit** | [**RecurringPerUnitPricingOverride**](RecurringPerUnitPricingOverride.md) |  | [optional] 
**recurring_tiered** | [**RecurringTieredPricingOverride**](RecurringTieredPricingOverride.md) |  | [optional] 
**recurring_volume** | [**RecurringVolumePricingOverride**](RecurringVolumePricingOverride.md) |  | [optional] 
**usage_flat_fee** | [**UsageFlatFeePricingOverride**](UsageFlatFeePricingOverride.md) |  | [optional] 
**usage_overage** | [**UsageOveragePricingOverride**](UsageOveragePricingOverride.md) |  | [optional] 
**usage_per_unit** | [**UsagePerUnitPricingOverride**](UsagePerUnitPricingOverride.md) |  | [optional] 
**usage_tiered** | [**UsageTieredPricingOverride**](UsageTieredPricingOverride.md) |  | [optional] 
**usage_tiered_with_overage** | [**UsageTieredWithOveragePricingOverride**](UsageTieredWithOveragePricingOverride.md) |  | [optional] 
**usage_volume** | [**UsageVolumePricingOverride**](UsageVolumePricingOverride.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.charge_override_pricing import ChargeOverridePricing

# TODO update the JSON string below
json = "{}"
# create an instance of ChargeOverridePricing from a JSON string
charge_override_pricing_instance = ChargeOverridePricing.from_json(json)
# print the JSON string representation of the object
print(ChargeOverridePricing.to_json())

# convert the object into a dict
charge_override_pricing_dict = charge_override_pricing_instance.to_dict()
# create an instance of ChargeOverridePricing from a dict
charge_override_pricing_from_dict = ChargeOverridePricing.from_dict(charge_override_pricing_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


