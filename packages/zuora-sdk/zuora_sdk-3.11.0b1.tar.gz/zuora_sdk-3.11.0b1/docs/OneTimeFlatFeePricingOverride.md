# OneTimeFlatFeePricingOverride

Pricing information about a one-time charge that uses the \"flat fee\" charge model. In this charge model, the charge has a fixed price.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**list_price** | **float** | Price of the charge.  | 
**original_list_price** | **float** | The original list price is the price of a product or service at which it is listed for sale by a manufacturer or retailer.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.one_time_flat_fee_pricing_override import OneTimeFlatFeePricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of OneTimeFlatFeePricingOverride from a JSON string
one_time_flat_fee_pricing_override_instance = OneTimeFlatFeePricingOverride.from_json(json)
# print the JSON string representation of the object
print(OneTimeFlatFeePricingOverride.to_json())

# convert the object into a dict
one_time_flat_fee_pricing_override_dict = one_time_flat_fee_pricing_override_instance.to_dict()
# create an instance of OneTimeFlatFeePricingOverride from a dict
one_time_flat_fee_pricing_override_from_dict = OneTimeFlatFeePricingOverride.from_dict(one_time_flat_fee_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


