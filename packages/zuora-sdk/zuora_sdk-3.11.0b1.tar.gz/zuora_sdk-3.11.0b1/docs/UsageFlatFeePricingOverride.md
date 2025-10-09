# UsageFlatFeePricingOverride

Pricing information about a usage charge that uses the \"flat fee\" charge model. In this charge model, the charge has a fixed price.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**list_price** | **float** | Price of the charge.  | [optional] 
**original_list_price** | **float** | The original list price is the price of a product or service at which it is listed for sale by a manufacturer or retailer.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.usage_flat_fee_pricing_override import UsageFlatFeePricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of UsageFlatFeePricingOverride from a JSON string
usage_flat_fee_pricing_override_instance = UsageFlatFeePricingOverride.from_json(json)
# print the JSON string representation of the object
print(UsageFlatFeePricingOverride.to_json())

# convert the object into a dict
usage_flat_fee_pricing_override_dict = usage_flat_fee_pricing_override_instance.to_dict()
# create an instance of UsageFlatFeePricingOverride from a dict
usage_flat_fee_pricing_override_from_dict = UsageFlatFeePricingOverride.from_dict(usage_flat_fee_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


