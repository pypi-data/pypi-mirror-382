# ExpandedSubscription


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**auto_renew** | **bool** |  | [optional] 
**cancelled_date** | **date** |  | [optional] 
**contract_acceptance_date** | **date** |  | [optional] 
**contract_effective_date** | **date** |  | [optional] 
**creator_account_id** | **str** |  | [optional] 
**creator_invoice_owner_id** | **str** |  | [optional] 
**current_term** | **int** |  | [optional] 
**current_term_period_type** | **str** |  | [optional] 
**initial_term** | **int** |  | [optional] 
**initial_term_period_type** | **str** |  | [optional] 
**invoice_group_number** | **str** |  | [optional] 
**invoice_owner_id** | **str** |  | [optional] 
**is_invoice_separate** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**notes** | **str** |  | [optional] 
**original_created_date** | **str** |  | [optional] 
**original_id** | **str** |  | [optional] 
**previous_subscription_id** | **str** |  | [optional] 
**renewal_setting** | **str** |  | [optional] 
**renewal_term** | **int** |  | [optional] 
**renewal_term_period_type** | **str** |  | [optional] 
**revision** | **str** |  | [optional] 
**service_activation_date** | **date** |  | [optional] 
**status** | **str** |  | [optional] 
**is_latest_version** | **bool** |  | [optional] 
**subscription_end_date** | **date** |  | [optional] 
**subscription_start_date** | **date** |  | [optional] 
**subscription_version_amendment_id** | **str** |  | [optional] 
**term_end_date** | **date** |  | [optional] 
**term_start_date** | **date** |  | [optional] 
**term_type** | **str** |  | [optional] 
**version** | **int** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**c_mrr** | **float** |  | [optional] 
**bill_to_contact_snapshot_id** | **str** |  | [optional] 
**bill_to_contact_id** | **str** |  | [optional] 
**invoice_template_id** | **str** |  | [optional] 
**communication_profile_id** | **str** |  | [optional] 
**sequence_set_id** | **str** |  | [optional] 
**sold_to_contact_id** | **str** |  | [optional] 
**sold_to_contact_snapshot_id** | **str** |  | [optional] 
**ship_to_contact_id** | **str** |  | [optional] 
**ship_to_contact_snapshot_id** | **str** |  | [optional] 
**externally_managed_by** | **str** |  | [optional] 
**last_booking_date** | **date** |  | [optional] 
**invoice_schedule_id** | **str** |  | [optional] 
**cancel_reason** | **str** |  | [optional] 
**prepayment** | **bool** |  | [optional] 
**currency** | **str** |  | [optional] 
**is_single_versioned** | **bool** |  | [optional] 
**order_id** | **str** |  | [optional] 
**ramp_id** | **str** |  | [optional] 
**payment_term** | **str** |  | [optional] 
**payment_method_id** | **str** |  | [optional] 
**payment_gateway_id** | **str** |  | [optional] 
**quote_number__qt** | **str** |  | [optional] 
**quote_type__qt** | **str** |  | [optional] 
**quote_business_type__qt** | **str** |  | [optional] 
**opportunity_name__qt** | **str** |  | [optional] 
**opportunity_close_date__qt** | **date** |  | [optional] 
**cpq_bundle_json_id__qt** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**invoice_owner** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**bill_to_contact** | [**ExpandedContact**](ExpandedContact.md) |  | [optional] 
**invoice_items** | [**List[ExpandedInvoiceItem]**](ExpandedInvoiceItem.md) |  | [optional] 
**rate_plans** | [**List[ExpandedRatePlan]**](ExpandedRatePlan.md) |  | [optional] 
**order** | [**ExpandedOrders**](ExpandedOrders.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_subscription import ExpandedSubscription

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedSubscription from a JSON string
expanded_subscription_instance = ExpandedSubscription.from_json(json)
# print the JSON string representation of the object
print(ExpandedSubscription.to_json())

# convert the object into a dict
expanded_subscription_dict = expanded_subscription_instance.to_dict()
# create an instance of ExpandedSubscription from a dict
expanded_subscription_from_dict = ExpandedSubscription.from_dict(expanded_subscription_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


