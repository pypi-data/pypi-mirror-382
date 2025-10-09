# UsageTieredPricingOverride

Pricing information about a usage charge that uses the \"tiered pricing\" charge model. In this charge model, the charge has cumulative pricing tiers that become effective as units are consumed.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**rating_group** | **str** | Specifies how Zuora groups usage records when rating usage. See [Usage Rating by Group](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Usage/Usage_Rating_by_Group) for more information.   * ByBillingPeriod (default): The rating is based on all the usages in a billing period.   * ByUsageStartDate: The rating is based on all the usages on the same usage start date.    * ByUsageRecord: The rating is based on each usage record.   * ByUsageUpload: The rating is based on all the usages in a uploaded usage file (.xls or .csv). If you import a mass usage in a single upload, which contains multiple usage files in .xls or .csv format, usage records are grouped for each usage file. | [optional] 
**tiers** | [**List[ChargeTier]**](ChargeTier.md) | List of cumulative pricing tiers in the charge.  | [optional] 
**uom** | **str** | Unit of measure of the standalone charge.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.usage_tiered_pricing_override import UsageTieredPricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of UsageTieredPricingOverride from a JSON string
usage_tiered_pricing_override_instance = UsageTieredPricingOverride.from_json(json)
# print the JSON string representation of the object
print(UsageTieredPricingOverride.to_json())

# convert the object into a dict
usage_tiered_pricing_override_dict = usage_tiered_pricing_override_instance.to_dict()
# create an instance of UsageTieredPricingOverride from a dict
usage_tiered_pricing_override_from_dict = UsageTieredPricingOverride.from_dict(usage_tiered_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


