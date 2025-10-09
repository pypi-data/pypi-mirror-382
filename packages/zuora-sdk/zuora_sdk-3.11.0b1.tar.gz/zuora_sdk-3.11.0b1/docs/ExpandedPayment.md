# ExpandedPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**applied_amount** | **float** |  | [optional] 
**applied_credit_balance_amount** | **float** |  | [optional] 
**auth_transaction_id** | **str** |  | [optional] 
**bank_identification_number** | **str** |  | [optional] 
**cancelled_on** | **str** |  | [optional] 
**comment** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**effective_date** | **date** |  | [optional] 
**gateway_order_id** | **str** |  | [optional] 
**gateway_reconciliation_reason** | **str** |  | [optional] 
**gateway_reconciliation_status** | **str** |  | [optional] 
**gateway_response** | **str** |  | [optional] 
**gateway_response_code** | **str** |  | [optional] 
**gateway_state** | **str** |  | [optional] 
**gateway_transaction_state** | **str** |  | [optional] 
**is_standalone** | **bool** |  | [optional] 
**marked_for_submission_on** | **str** |  | [optional] 
**payment_method_id** | **str** |  | [optional] 
**payment_method_snapshot_id** | **str** |  | [optional] 
**payment_option_id** | **str** |  | [optional] 
**payment_number** | **str** |  | [optional] 
**payout_id** | **str** |  | [optional] 
**prepayment** | **bool** |  | [optional] 
**referenced_payment_id** | **str** |  | [optional] 
**reference_id** | **str** |  | [optional] 
**refund_amount** | **float** |  | [optional] 
**second_payment_reference_id** | **str** |  | [optional] 
**settled_on** | **str** |  | [optional] 
**soft_descriptor** | **str** |  | [optional] 
**soft_descriptor_phone** | **str** |  | [optional] 
**source** | **str** |  | [optional] 
**source_name** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**submitted_on** | **str** |  | [optional] 
**transferred_to_accounting** | **str** |  | [optional] 
**transaction_source** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**unapplied_amount** | **float** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**last_email_date_time** | **str** |  | [optional] 
**gateway_routing_execution_id** | **str** |  | [optional] 
**gateway** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**payment_method** | [**ExpandedPaymentMethod**](ExpandedPaymentMethod.md) |  | [optional] 
**payment_applications** | [**List[ExpandedPaymentApplication]**](ExpandedPaymentApplication.md) |  | [optional] 
**payment_schedule_item_payments** | [**List[ExpandedPaymentScheduleItemPayment]**](ExpandedPaymentScheduleItemPayment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_payment import ExpandedPayment

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPayment from a JSON string
expanded_payment_instance = ExpandedPayment.from_json(json)
# print the JSON string representation of the object
print(ExpandedPayment.to_json())

# convert the object into a dict
expanded_payment_dict = expanded_payment_instance.to_dict()
# create an instance of ExpandedPayment from a dict
expanded_payment_from_dict = ExpandedPayment.from_dict(expanded_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


