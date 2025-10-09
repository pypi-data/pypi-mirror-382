# ExpandedPrepaidBalanceFund


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**balance** | **float** |  | [optional] 
**charge_segment_number** | **int** |  | [optional] 
**end_date** | **date** |  | [optional] 
**funded_balance** | **float** |  | [optional] 
**fund_source_type** | **str** |  | [optional] 
**funding_price** | **float** |  | [optional] 
**total_billed** | **float** |  | [optional] 
**total_balance** | **float** |  | [optional] 
**original_total_balance** | **float** |  | [optional] 
**original_funding_price** | **float** |  | [optional] 
**original_fund_end_date** | **date** |  | [optional] 
**rollover_validity_period_start_date** | **date** |  | [optional] 
**rollover_validity_period_end_date** | **date** |  | [optional] 
**prepaid_balance_id** | **str** |  | [optional] 
**priority** | **int** |  | [optional] 
**source_id** | **str** |  | [optional] 
**start_date** | **date** |  | [optional] 
**vp_summary_id** | **str** |  | [optional] 
**rollover_count** | **int** |  | [optional] 
**origin_fund_id** | **str** |  | [optional] 
**rollover_apply_option** | **str** |  | [optional] 
**done** | **int** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**prepaid_balance** | [**ExpandedPrepaidBalance**](ExpandedPrepaidBalance.md) |  | [optional] 
**source** | [**ExpandedRatePlanCharge**](ExpandedRatePlanCharge.md) |  | [optional] 
**vp_summary** | [**ExpandedValidityPeriodSummary**](ExpandedValidityPeriodSummary.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_prepaid_balance_fund import ExpandedPrepaidBalanceFund

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPrepaidBalanceFund from a JSON string
expanded_prepaid_balance_fund_instance = ExpandedPrepaidBalanceFund.from_json(json)
# print the JSON string representation of the object
print(ExpandedPrepaidBalanceFund.to_json())

# convert the object into a dict
expanded_prepaid_balance_fund_dict = expanded_prepaid_balance_fund_instance.to_dict()
# create an instance of ExpandedPrepaidBalanceFund from a dict
expanded_prepaid_balance_fund_from_dict = ExpandedPrepaidBalanceFund.from_dict(expanded_prepaid_balance_fund_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


