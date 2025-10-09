# ChargeUpdate

The JSON object containing the information for a charge update in the 'UpdateProduct' type order action.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing** | [**BillingUpdate**](BillingUpdate.md) |  | [optional] 
**charge_number** | **str** | The number of the charge to be updated. The value of this field is inherited from the &#x60;subscriptions&#x60; &gt; &#x60;orderActions&#x60; &gt; &#x60;addProduct&#x60; &gt; &#x60;chargeOverrides&#x60; &gt; &#x60;chargeNumber&#x60; field.   | [optional] 
**estimated_start_date** | **date** | Estimated start date of the charge. This field is only available when the charge is changed through the related order actions. **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Pending Charge Flexibility&lt;/a&gt; feature is enabled.  | [optional] 
**new_rate_plan_charge_id** | **str** | The ID of the new rate plan charge. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan Charge object.  | [optional] 
**description** | **str** |  | [optional] 
**effective_date** | [**TriggerParams**](TriggerParams.md) |  | [optional] 
**pricing** | [**PricingUpdate**](PricingUpdate.md) | Pricing information about the charge.  | [optional] 
**unique_token** | **str** | description: |   A unique string to represent the rate plan charge in the order. The unique token is used to perform multiple actions against a newly added rate plan charge. For example, if you want to add and update a product in the same order, assign a unique token to the newly added rate plan charge and use that token in future order actions.  | [optional] 
**is_dimensional_price** | **bool** | Indicates whether the charge uses dimensional pricing.  **Note**: This field is only available in response payloads.  | [optional] [readonly] 
**pricing_attributes** | **Dict[str, object]** | Container for pricing attributes used in dynamic pricing.  **Note**: This field requires the DynamicPricing permission to be accessible.  | [optional] 
**negotiated_price_table** | **Dict[str, object]** | Container for negotiated price table information.  **Note**: This field requires the NegotiatedPriceTable permission to be accessible.  | [optional] 

## Example

```python
from zuora_sdk.models.charge_update import ChargeUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ChargeUpdate from a JSON string
charge_update_instance = ChargeUpdate.from_json(json)
# print the JSON string representation of the object
print(ChargeUpdate.to_json())

# convert the object into a dict
charge_update_dict = charge_update_instance.to_dict()
# create an instance of ChargeUpdate from a dict
charge_update_from_dict = ChargeUpdate.from_dict(charge_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


