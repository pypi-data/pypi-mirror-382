# DiscountPricingOverride

Pricing information about a discount charge. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**apply_discount_to** | [**ApplyDiscountTo**](ApplyDiscountTo.md) |  | [optional] 
**original_discount_amount** | **float** | The manufacturer&#39;s suggested retail discount price for standalone charge.  Only applicable if the standalone discount charge is a fixed-amount discount.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 
**discount_amount** | **float** | Only applicable if the discount charge is a fixed-amount discount.  | [optional] 
**discount_level** | [**DiscountLevel**](DiscountLevel.md) |  | [optional] 
**original_discount_percentage** | **float** | The manufacturer&#39;s suggested retail discount percentage for standalone charge.  Only applicable if the standalone discount charge is a percentage discount.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 
**discount_percentage** | **float** | Only applicable if the discount charge is a percentage discount.  | [optional] 
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**discount_class** | **str** | The discount class defines the sequence in which discount product rate plan charges are applied.  **Note**: You must enable the [Enhanced Discounts](https://knowledgecenter.zuora.com/Zuora_Billing/Build_products_and_prices/Basic_concepts_and_terms/B_Charge_Models/D_Manage_Enhanced_Discount) feature to access this field.  | [optional] 
**apply_to_billing_period_partially** | **bool** | Allow the discount duration to be aligned with the billing period partially.  **Note**: You must enable the [Enhanced Discounts](https://knowledgecenter.zuora.com/Zuora_Billing/Build_products_and_prices/Basic_concepts_and_terms/B_Charge_Models/D_Manage_Enhanced_Discount) feature to access this field.  | [optional] 
**discount_apply_details** | [**List[OverrideDiscountApplyDetail]**](OverrideDiscountApplyDetail.md) | Charge list of discount be applied to.  **Note**: You must enable the [Enhanced Discounts](https://knowledgecenter.zuora.com/Zuora_Billing/Build_products_and_prices/Basic_concepts_and_terms/B_Charge_Models/D_Manage_Enhanced_Discount) feature to access this field.  | [optional] 

## Example

```python
from zuora_sdk.models.discount_pricing_override import DiscountPricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of DiscountPricingOverride from a JSON string
discount_pricing_override_instance = DiscountPricingOverride.from_json(json)
# print the JSON string representation of the object
print(DiscountPricingOverride.to_json())

# convert the object into a dict
discount_pricing_override_dict = discount_pricing_override_instance.to_dict()
# create an instance of DiscountPricingOverride from a dict
discount_pricing_override_from_dict = DiscountPricingOverride.from_dict(discount_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


