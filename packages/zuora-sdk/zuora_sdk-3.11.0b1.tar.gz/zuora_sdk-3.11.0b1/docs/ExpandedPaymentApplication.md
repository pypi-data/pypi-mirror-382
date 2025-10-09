# ExpandedPaymentApplication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**apply_amount** | **float** |  | [optional] 
**effective_date** | **date** |  | [optional] 
**payment_application_status** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**payment_id** | **str** |  | [optional] 
**invoice_id** | **str** |  | [optional] 
**application_group_id** | **str** |  | [optional] 
**debit_memo_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**billing_document_owner_id** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**unapplied_payment_accounting_code_id** | **str** |  | [optional] 
**cash_accounting_code_id** | **str** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**payment** | [**ExpandedPayment**](ExpandedPayment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_payment_application import ExpandedPaymentApplication

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPaymentApplication from a JSON string
expanded_payment_application_instance = ExpandedPaymentApplication.from_json(json)
# print the JSON string representation of the object
print(ExpandedPaymentApplication.to_json())

# convert the object into a dict
expanded_payment_application_dict = expanded_payment_application_instance.to_dict()
# create an instance of ExpandedPaymentApplication from a dict
expanded_payment_application_from_dict = ExpandedPaymentApplication.from_dict(expanded_payment_application_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


