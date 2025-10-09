# ExpandedRefundApplication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** |  | [optional] 
**application_group_id** | **str** |  | [optional] 
**apply_amount** | **float** |  | [optional] 
**credit_memo_id** | **str** |  | [optional] 
**effective_date** | **date** |  | [optional] 
**invoice_id** | **str** |  | [optional] 
**payment_id** | **str** |  | [optional] 
**refund_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**cash_accounting_code_id** | **str** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**on_account_accounting_code_id** | **str** |  | [optional] 
**unapplied_payment_accounting_code_id** | **str** |  | [optional] 
**refund** | [**ExpandedRefund**](ExpandedRefund.md) |  | [optional] 
**payment** | [**ExpandedPayment**](ExpandedPayment.md) |  | [optional] 
**refund_application_items** | [**List[ExpandedRefundApplicationItem]**](ExpandedRefundApplicationItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_refund_application import ExpandedRefundApplication

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRefundApplication from a JSON string
expanded_refund_application_instance = ExpandedRefundApplication.from_json(json)
# print the JSON string representation of the object
print(ExpandedRefundApplication.to_json())

# convert the object into a dict
expanded_refund_application_dict = expanded_refund_application_instance.to_dict()
# create an instance of ExpandedRefundApplication from a dict
expanded_refund_application_from_dict = ExpandedRefundApplication.from_dict(expanded_refund_application_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


