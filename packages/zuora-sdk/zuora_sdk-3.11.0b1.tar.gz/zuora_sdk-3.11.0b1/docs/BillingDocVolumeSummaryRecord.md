# BillingDocVolumeSummaryRecord

A volume summary record. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_failed_accounts** | **int** | The count of total accounts who have failed records. | [optional] 
**total_generated_credit_memos** | **int** | The count of total generated credit memos.  | [optional] 
**total_generated_invoices** | **int** | The count of total generated invoices.  | [optional] 

## Example

```python
from zuora_sdk.models.billing_doc_volume_summary_record import BillingDocVolumeSummaryRecord

# TODO update the JSON string below
json = "{}"
# create an instance of BillingDocVolumeSummaryRecord from a JSON string
billing_doc_volume_summary_record_instance = BillingDocVolumeSummaryRecord.from_json(json)
# print the JSON string representation of the object
print(BillingDocVolumeSummaryRecord.to_json())

# convert the object into a dict
billing_doc_volume_summary_record_dict = billing_doc_volume_summary_record_instance.to_dict()
# create an instance of BillingDocVolumeSummaryRecord from a dict
billing_doc_volume_summary_record_from_dict = BillingDocVolumeSummaryRecord.from_dict(billing_doc_volume_summary_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


