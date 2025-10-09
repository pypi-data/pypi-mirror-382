# ExpandedCommitment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**commitment_number** | **str** |  | [optional] 
**version** | **int** |  | [optional] 
**account_number** | **str** |  | [optional] 
**order_number** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**priority** | **int** |  | [optional] 
**type** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**taxable** | **bool** |  | [optional] 
**tax_code** | **str** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**cycle_period_type** | **str** |  | [optional] 
**cycle_period_length** | **int** |  | [optional] 
**cycle_day_type** | **str** |  | [optional] 
**cycle_day** | **int** |  | [optional] 
**cycle_alignment_date** | **date** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**adjustment_liability_accounting_code** | **str** |  | [optional] 
**adjustment_revenue_accounting_code** | **str** |  | [optional] 
**contract_asset_accounting_code** | **str** |  | [optional] 
**contract_liability_accounting_code** | **str** |  | [optional] 
**contract_recognized_revenue_accounting_code** | **str** |  | [optional] 
**deferred_revenue_accounting_code** | **str** |  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** |  | [optional] 
**is_allocation_eligible** | **bool** |  | [optional] 
**is_unbilled** | **bool** |  | [optional] 
**recognized_revenue_accounting_code** | **str** |  | [optional] 
**revenue_recognition_rule_name** | **str** |  | [optional] 
**unbilled_receivables_accounting_code** | **str** |  | [optional] 
**revenue_recognition_timing** | **str** |  | [optional] 
**revenue_amortization_method** | **str** |  | [optional] 
**account_receivable_accounting_code** | **str** |  | [optional] 
**proration_option** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_commitment import ExpandedCommitment

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedCommitment from a JSON string
expanded_commitment_instance = ExpandedCommitment.from_json(json)
# print the JSON string representation of the object
print(ExpandedCommitment.to_json())

# convert the object into a dict
expanded_commitment_dict = expanded_commitment_instance.to_dict()
# create an instance of ExpandedCommitment from a dict
expanded_commitment_from_dict = ExpandedCommitment.from_dict(expanded_commitment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


