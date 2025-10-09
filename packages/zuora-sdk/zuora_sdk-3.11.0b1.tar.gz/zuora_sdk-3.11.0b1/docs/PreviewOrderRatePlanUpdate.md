# PreviewOrderRatePlanUpdate

Information about an order action of type `UpdateProduct`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_updates** | [**List[PreviewOrderChargeUpdate]**](PreviewOrderChargeUpdate.md) | Array of the JSON objects containing the information for a charge update in the &#x60;updateProduct&#x60; type of order action.   When previewing an &#x60;updateProduct&#x60; order action, either the &#x60;chargeNumber&#x60; or &#x60;uniqueToken&#x60; field is required to specify the charge to update. | [optional] 
**clearing_existing_features** | **bool** | Specifies whether all features in the rate plan will be cleared.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of the Rate Plan object. The custom fields of  the Rate Plan object are used when rate plans are subscribed. | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription.  | [optional] 
**rate_plan_id** | **str** | The id of the rate plan to be updated. It can be the latest version or any history version id. | [optional] 
**specific_update_date** | **date** |  The date when the Update Product order action takes effect. This field is only applicable if there is already a future-dated Update Product order action on the subscription. The format of the date is yyyy-mm-dd.  See [Update a Product on Subscription with Future-dated Updates](https://knowledgecenter.zuora.com/BC_Subscription_Management/Orders/AC_Orders_Tutorials/C_Update_a_Product_in_a_Subscription/Update_a_Product_on_Subscription_with_Future-dated_Updates) for more information about this feature.  | [optional] 
**subscription_product_features** | [**List[CreateOrderRatePlanFeatureOverride]**](CreateOrderRatePlanFeatureOverride.md) | List of features associated with the rate plan.  The system compares the &#x60;subscriptionProductFeatures&#x60; and &#x60;featureId&#x60; fields in the request with the counterpart fields in a rate plan. The comparison results are as follows:  * If there is no &#x60;subscriptionProductFeatures&#x60; field or the field is empty, features in the rate plan remain unchanged. But if the &#x60;clearingExistingFeatures&#x60; field is additionally set to true, all features in the rate plan are cleared.  * If the &#x60;subscriptionProductFeatures&#x60; field contains the &#x60;featureId&#x60; nested fields, as well as the optional &#x60;description&#x60; and &#x60;customFields&#x60; nested fields, the features indicated by the featureId nested fields in the request overwrite all features in the rate plan. | [optional] 
**subscription_rate_plan_number** | **str** | Number of a rate plan for this subscription.  | [optional] 
**unique_token** | **str** | A unique string to represent the rate plan in the order. The unique token is used to perform multiple actions against a newly added rate plan. For example, if you want to add and update a product in the same order, assign a unique token to the newly added rate plan and use that token in future order actions. | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_rate_plan_update import PreviewOrderRatePlanUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderRatePlanUpdate from a JSON string
preview_order_rate_plan_update_instance = PreviewOrderRatePlanUpdate.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderRatePlanUpdate.to_json())

# convert the object into a dict
preview_order_rate_plan_update_dict = preview_order_rate_plan_update_instance.to_dict()
# create an instance of PreviewOrderRatePlanUpdate from a dict
preview_order_rate_plan_update_from_dict = PreviewOrderRatePlanUpdate.from_dict(preview_order_rate_plan_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


