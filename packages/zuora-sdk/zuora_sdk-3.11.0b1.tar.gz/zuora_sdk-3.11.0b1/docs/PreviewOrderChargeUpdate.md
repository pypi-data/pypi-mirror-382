# PreviewOrderChargeUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing** | [**BillingUpdate**](BillingUpdate.md) |  | [optional] 
**charge_number** | **str** | The number of the charge to be updated. The value of this field is inherited from the &#x60;subscriptions&#x60; &gt; &#x60;orderActions&#x60; &gt; &#x60;addProduct&#x60; &gt; &#x60;chargeOverrides&#x60; &gt; &#x60;chargeNumber&#x60; field. | [optional] 
**product_rate_plan_charge_number** | **str** | Number of a product rate-plan charge for this subscription. | [optional] 
**product_rate_plan_charge_id** | **str** | ID of a product rate-plan charge for this subscription.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan Charge object.  | [optional] 
**description** | **str** |  | [optional] 
**estimated_start_date** | **date** | Estimated start date of the charge. This field is only available when the charge is changed through the related order actions. **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Pending Charge Flexibility&lt;/a&gt; feature is enabled.  | [optional] 
**effective_date** | [**TriggerParams**](TriggerParams.md) |  | [optional] 
**prepaid_quantity** | **float** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.   The number of units included in a [prepayment charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge). Must be a positive number (&gt;0).       | [optional] 
**pricing** | [**PreviewOrderPricingUpdate**](PreviewOrderPricingUpdate.md) | Pricing information about the charge.  | [optional] 
**unique_token** | **str** | A unique string to represent the rate plan charge in the order. The unique token is used to perform multiple actions against a newly added rate plan charge. For example, if you want to add and update a product in the same order, assign a unique token to the newly added rate plan charge and use that token in future order actions. | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_charge_update import PreviewOrderChargeUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderChargeUpdate from a JSON string
preview_order_charge_update_instance = PreviewOrderChargeUpdate.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderChargeUpdate.to_json())

# convert the object into a dict
preview_order_charge_update_dict = preview_order_charge_update_instance.to_dict()
# create an instance of PreviewOrderChargeUpdate from a dict
preview_order_charge_update_from_dict = PreviewOrderChargeUpdate.from_dict(preview_order_charge_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


