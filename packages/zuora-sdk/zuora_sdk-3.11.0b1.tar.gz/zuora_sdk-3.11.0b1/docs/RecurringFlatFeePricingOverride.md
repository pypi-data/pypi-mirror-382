# RecurringFlatFeePricingOverride

Pricing information about a recurring charge that uses the \"flat fee\" charge model. In this charge model, the charge has a fixed price. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**list_price** | **float** | Price of the charge in each recurring period.  | [optional] 
**original_list_price** | **float** | The original list price is the price of a product or service at which it is listed for sale by a manufacturer or retailer.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 
**list_price_base** | [**ChargeListPriceBase**](ChargeListPriceBase.md) |  | [optional] 
**specific_list_price_base** | **int** | The number of months for the list price base of the charge. This field is required if you set the value of the &#x60;listPriceBase&#x60; field to &#x60;Per_Specific_Months&#x60;.  **Note**:    - This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Product_Catalog/I_Annual_List_Price\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Annual List Price&lt;/a&gt; feature enabled.   - The value of this field is &#x60;null&#x60; if you do not set the value of the &#x60;listPriceBase&#x60; field to &#x60;Per_Specific_Months&#x60;.                | [optional] 

## Example

```python
from zuora_sdk.models.recurring_flat_fee_pricing_override import RecurringFlatFeePricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of RecurringFlatFeePricingOverride from a JSON string
recurring_flat_fee_pricing_override_instance = RecurringFlatFeePricingOverride.from_json(json)
# print the JSON string representation of the object
print(RecurringFlatFeePricingOverride.to_json())

# convert the object into a dict
recurring_flat_fee_pricing_override_dict = recurring_flat_fee_pricing_override_instance.to_dict()
# create an instance of RecurringFlatFeePricingOverride from a dict
recurring_flat_fee_pricing_override_from_dict = RecurringFlatFeePricingOverride.from_dict(recurring_flat_fee_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


