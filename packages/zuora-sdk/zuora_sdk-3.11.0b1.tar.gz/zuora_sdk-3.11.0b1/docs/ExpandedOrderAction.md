# ExpandedOrderAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**contract_effective_date** | **date** |  | [optional] 
**customer_acceptance_date** | **date** |  | [optional] 
**type** | **str** |  | [optional] 
**sequence** | **int** |  | [optional] 
**subscription_version_amendment_id** | **str** |  | [optional] 
**order_id** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**change_reason** | **str** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**service_activation_date** | **date** |  | [optional] 
**auto_renew** | **bool** |  | [optional] 
**renew_setting** | **str** |  | [optional] 
**renewal_term** | **int** |  | [optional] 
**renewal_term_period_type** | **str** |  | [optional] 
**term_start_date** | **date** |  | [optional] 
**term_type** | **str** |  | [optional] 
**current_term** | **int** |  | [optional] 
**current_term_period_type** | **str** |  | [optional] 
**suspend_date** | **date** |  | [optional] 
**resume_date** | **date** |  | [optional] 
**cancellation_effective_date** | **date** |  | [optional] 
**cancellation_policy** | **str** |  | [optional] 
**payment_term** | **str** |  | [optional] 
**bill_to_contact_id** | **str** |  | [optional] 
**invoice_group_number** | **str** |  | [optional] 
**invoice_template_id** | **str** |  | [optional] 
**communication_profile_id** | **str** |  | [optional] 
**sequence_set_id** | **str** |  | [optional] 
**ship_to_contact_id** | **str** |  | [optional] 
**sold_to_contact_id** | **str** |  | [optional] 
**clearing_existing_payment_term** | **bool** |  | [optional] 
**clearing_existing_bill_to_contact** | **bool** |  | [optional] 
**clearing_existing_invoice_group_number** | **bool** |  | [optional] 
**clearing_existing_invoice_template** | **bool** |  | [optional] 
**clearing_existing_sequence_set** | **bool** |  | [optional] 
**clearing_existing_sold_to_contact** | **bool** |  | [optional] 
**clearing_existing_ship_to_contact** | **bool** |  | [optional] 
**clearing_existing_communication_profile** | **bool** |  | [optional] 
**sub_type** | **str** |  | [optional] 
**effective_policy** | **str** |  | [optional] 
**subscription** | [**ExpandedSubscription**](ExpandedSubscription.md) |  | [optional] 
**order** | [**ExpandedOrders**](ExpandedOrders.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_order_action import ExpandedOrderAction

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedOrderAction from a JSON string
expanded_order_action_instance = ExpandedOrderAction.from_json(json)
# print the JSON string representation of the object
print(ExpandedOrderAction.to_json())

# convert the object into a dict
expanded_order_action_dict = expanded_order_action_instance.to_dict()
# create an instance of ExpandedOrderAction from a dict
expanded_order_action_from_dict = ExpandedOrderAction.from_dict(expanded_order_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


