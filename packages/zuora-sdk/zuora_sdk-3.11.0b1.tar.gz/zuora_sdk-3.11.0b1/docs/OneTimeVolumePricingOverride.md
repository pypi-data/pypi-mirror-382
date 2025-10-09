# OneTimeVolumePricingOverride

Pricing information about a one-time charge that uses the \"volume pricing\" charge model. In this charge model, the charge has a variable price per unit, depending on how many units are purchased.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**quantity** | **float** | Number of units purchased.  | [optional] 
**tiers** | [**List[ChargeTier]**](ChargeTier.md) | List of variable pricing tiers in the charge.  | [optional] 
**uom** | **str** | Unit of measure of the standalone charge.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.one_time_volume_pricing_override import OneTimeVolumePricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of OneTimeVolumePricingOverride from a JSON string
one_time_volume_pricing_override_instance = OneTimeVolumePricingOverride.from_json(json)
# print the JSON string representation of the object
print(OneTimeVolumePricingOverride.to_json())

# convert the object into a dict
one_time_volume_pricing_override_dict = one_time_volume_pricing_override_instance.to_dict()
# create an instance of OneTimeVolumePricingOverride from a dict
one_time_volume_pricing_override_from_dict = OneTimeVolumePricingOverride.from_dict(one_time_volume_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


