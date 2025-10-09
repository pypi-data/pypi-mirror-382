# OrderActionRatePlanAmendment

The amendment that is related to the subscription rate plan. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The amendment code.  | [optional] 
**contract_effective_date** | **date** | The date when the amendment becomes effective for billing purposes, as &#x60;yyyy-mm-dd&#x60;. | [optional] 
**created_by** | **str** | The ID of the user who created this amendment.  | [optional] 
**created_date** | **str** | The time that the amendment gets created in the system, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format. | [optional] 
**customer_acceptance_date** | **date** | The date when the customer accepts the amendment changes to the subscription, as &#x60;yyyy-mm-dd&#x60;. | [optional] 
**description** | **str** | Description of the amendment.  | [optional] 
**effective_date** | **date** | The date when the amendment changes take effective.   | [optional] 
**id** | **str** | The amendment ID.  | [optional] 
**name** | **str** | The name of the amendment.  | [optional] 
**service_activation_date** | **date** | The date when service is activated, as &#x60;yyyy-mm-dd&#x60;.  | [optional] 
**type** | **str** | Type of the amendment. Possible values are:   - NewProduct - RemoveProduct - UpdateProduct  | [optional] 
**updated_by** | **str** | The ID of the user who updated this amendment. | [optional] 
**updated_date** | **str** | The time that the amendment gets updated in the system, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of Amendment object. | [optional] 
**is_created_by_order** | **bool** | Indicates whether the amendment was created by an order.  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_amendment import OrderActionRatePlanAmendment

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanAmendment from a JSON string
order_action_rate_plan_amendment_instance = OrderActionRatePlanAmendment.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanAmendment.to_json())

# convert the object into a dict
order_action_rate_plan_amendment_dict = order_action_rate_plan_amendment_instance.to_dict()
# create an instance of OrderActionRatePlanAmendment from a dict
order_action_rate_plan_amendment_from_dict = OrderActionRatePlanAmendment.from_dict(order_action_rate_plan_amendment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


