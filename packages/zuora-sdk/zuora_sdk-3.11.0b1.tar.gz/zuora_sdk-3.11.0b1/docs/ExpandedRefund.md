# ExpandedRefund


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** |  | [optional] 
**payment_method_snapshot_id** | **str** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**cancelled_on** | **str** |  | [optional] 
**comment** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**gateway_reconciliation_reason** | **str** |  | [optional] 
**gateway_reconciliation_status** | **str** |  | [optional] 
**gateway_response** | **str** |  | [optional] 
**gateway_response_code** | **str** |  | [optional] 
**gateway_state** | **str** |  | [optional] 
**marked_for_submission_on** | **str** |  | [optional] 
**method_type** | **str** |  | [optional] 
**payment_method_id** | **str** |  | [optional] 
**payout_id** | **str** |  | [optional] 
**reason_code** | **str** |  | [optional] 
**reference_id** | **str** |  | [optional] 
**refund_date** | **date** |  | [optional] 
**refund_number** | **str** |  | [optional] 
**refund_transaction_time** | **str** |  | [optional] 
**second_refund_reference_id** | **str** |  | [optional] 
**settled_on** | **str** |  | [optional] 
**soft_descriptor** | **str** |  | [optional] 
**soft_descriptor_phone** | **str** |  | [optional] 
**source_type** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**submitted_on** | **str** |  | [optional] 
**transferred_to_accounting** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**associated_transaction_number** | **str** |  | [optional] 
**gateway** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**payment_method** | [**ExpandedPaymentMethod**](ExpandedPaymentMethod.md) |  | [optional] 
**refund_applications** | [**List[ExpandedRefundApplication]**](ExpandedRefundApplication.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_refund import ExpandedRefund

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRefund from a JSON string
expanded_refund_instance = ExpandedRefund.from_json(json)
# print the JSON string representation of the object
print(ExpandedRefund.to_json())

# convert the object into a dict
expanded_refund_dict = expanded_refund_instance.to_dict()
# create an instance of ExpandedRefund from a dict
expanded_refund_from_dict = ExpandedRefund.from_dict(expanded_refund_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


