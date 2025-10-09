# AddSubscriptionRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**booking_date** | **date** | The booking date that you want to set for the amendment contract. The booking date of an amendment is the equivalent of the order date of an order. This field must be in the &#x60;yyyy-mm-dd&#x60; format. The default value is the current date when you make the API call.              | [optional] 
**charge_overrides** | [**List[AddSubscriptionComponent]**](AddSubscriptionComponent.md) | This optional container is used to override the quantity of one or more product rate plan charges for this subscription.  | [optional] 
**contract_effective_date** | **date** | The date when the amendment changes take effect. The format of the date is yyyy-mm-dd.  If there is already a future-dated Update Product amendment on the subscription, the &#x60;specificUpdateDate&#x60; field will be used instead of this field to specify when the Update Product amendment takes effect.  | 
**customer_acceptance_date** | **date** | The date when the customer accepts the contract in yyyy-mm-dd format.  If this field is not set:  * If the &#x60;serviceActivationDate&#x60; field is not set, the value of this field is set to be the contract effective date. * If the &#x60;serviceActivationDate&#x60; field is set, the value of this field is set to be the service activation date.  The billing trigger dates must follow this rule:  contractEffectiveDate &lt;&#x3D; serviceActivationDate &lt;&#x3D; contractAcceptanceDate  | [optional] 
**external_catalog_plan_id** | **str** | An external ID of the product rate plan to be added. You can use this field to specify a product rate plan that is imported from an external system. The value of the &#x60;externalCatalogPlanId&#x60; field must match one of the values that are predefined in the &#x60;externallyManagedPlanIds&#x60; field on a product rate plan.  **Note:** If both &#x60;externalCatalogPlanId&#x60; and &#x60;productRatePlanId&#x60; are provided. They must point to the same product rate plan. Otherwise, the request would fail.  | [optional] 
**external_id_source_system** | **str** | The ID of the external source system. You can use this field and &#x60;externalCatalogPlanId&#x60; to specify a product rate plan that is imported from an external system.  **Note:** If both &#x60;externalCatalogPlanId&#x60;, &#x60;externalIdSourceSystem&#x60; and &#x60;productRatePlanId&#x60; are provided. They must point to the same product rate plan. Otherwise, the request would fail.  | [optional] 
**externally_managed_plan_id** | **str** | Indicates the unique identifier for the rate plan purchased on a third-party store. This field is used to represent a subscription rate plan created through third-party stores.  | [optional] 
**product_rate_plan_id** | **str** | ID of a product rate plan for this subscription  | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription  | [optional] 
**service_activation_date** | **date** | The date when the new product in the subscription is activated in yyyy-mm-dd format.  You must specify a Service Activation date if the Customer Acceptance date is set. If the Customer Acceptance date is not set, the value of the &#x60;serviceActivationDate&#x60; field defaults to be the Contract Effective Date.  The billing trigger dates must follow this rule:  contractEffectiveDate &lt;&#x3D; serviceActivationDate &lt;&#x3D; contractAcceptanceDate  | [optional] 

## Example

```python
from zuora_sdk.models.add_subscription_rate_plan import AddSubscriptionRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of AddSubscriptionRatePlan from a JSON string
add_subscription_rate_plan_instance = AddSubscriptionRatePlan.from_json(json)
# print the JSON string representation of the object
print(AddSubscriptionRatePlan.to_json())

# convert the object into a dict
add_subscription_rate_plan_dict = add_subscription_rate_plan_instance.to_dict()
# create an instance of AddSubscriptionRatePlan from a dict
add_subscription_rate_plan_from_dict = AddSubscriptionRatePlan.from_dict(add_subscription_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


