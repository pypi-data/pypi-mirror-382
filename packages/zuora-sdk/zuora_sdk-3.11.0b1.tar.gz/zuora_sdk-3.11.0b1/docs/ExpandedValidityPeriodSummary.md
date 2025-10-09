# ExpandedValidityPeriodSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**prepaid_balance_id** | **str** |  | [optional] 
**start_date** | **date** |  | [optional] 
**billing_timing** | **str** |  | [optional] 
**end_date** | **date** |  | [optional] 
**total_balance** | **float** |  | [optional] 
**remaining_balance** | **float** |  | [optional] 
**total_billed_amount** | **float** |  | [optional] 
**billed_balance_amount** | **float** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**uom** | **str** |  | [optional] 
**account_number** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**overage_rated_quantity** | **float** |  | [optional] 
**overage_rated_amount** | **float** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**prepaid_balance** | [**ExpandedPrepaidBalance**](ExpandedPrepaidBalance.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_validity_period_summary import ExpandedValidityPeriodSummary

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedValidityPeriodSummary from a JSON string
expanded_validity_period_summary_instance = ExpandedValidityPeriodSummary.from_json(json)
# print the JSON string representation of the object
print(ExpandedValidityPeriodSummary.to_json())

# convert the object into a dict
expanded_validity_period_summary_dict = expanded_validity_period_summary_instance.to_dict()
# create an instance of ExpandedValidityPeriodSummary from a dict
expanded_validity_period_summary_from_dict = ExpandedValidityPeriodSummary.from_dict(expanded_validity_period_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


