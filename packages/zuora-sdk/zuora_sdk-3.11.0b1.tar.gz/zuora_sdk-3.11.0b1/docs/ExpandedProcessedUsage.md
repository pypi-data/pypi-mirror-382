# ExpandedProcessedUsage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**usage_id** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**billing_period_end_date** | **str** |  | [optional] 
**billing_period_start_date** | **str** |  | [optional] 
**invoice_item_id** | **str** |  | [optional] 
**rate_plan_charge_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**credit_memo_item_id** | **str** |  | [optional] 
**usage** | [**ExpandedUsage**](ExpandedUsage.md) |  | [optional] 
**invoice_item** | [**ExpandedInvoiceItem**](ExpandedInvoiceItem.md) |  | [optional] 
**credit_memo_item** | [**ExpandedCreditMemoItem**](ExpandedCreditMemoItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_processed_usage import ExpandedProcessedUsage

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedProcessedUsage from a JSON string
expanded_processed_usage_instance = ExpandedProcessedUsage.from_json(json)
# print the JSON string representation of the object
print(ExpandedProcessedUsage.to_json())

# convert the object into a dict
expanded_processed_usage_dict = expanded_processed_usage_instance.to_dict()
# create an instance of ExpandedProcessedUsage from a dict
expanded_processed_usage_from_dict = ExpandedProcessedUsage.from_dict(expanded_processed_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


