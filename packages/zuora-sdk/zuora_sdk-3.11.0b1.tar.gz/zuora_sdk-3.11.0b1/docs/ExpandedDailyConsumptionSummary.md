# ExpandedDailyConsumptionSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**origin_charge_id** | **str** |  | [optional] 
**charge_segment_number** | **int** |  | [optional] 
**fund_id** | **str** |  | [optional] 
**daily_consumption_amount** | **float** |  | [optional] 
**daily_total_quantity** | **float** |  | [optional] 
**transaction_date** | **date** |  | [optional] 
**rating_result_id** | **str** |  | [optional] 
**daily_group_summary_id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**drawdown_origin_charge_id** | **str** |  | [optional] 
**drawdown_charge_segment_number** | **int** |  | [optional] 
**drawdown_recognized_revenue_gl_account_number** | **str** |  | [optional] 
**drawdown_adjustment_revenue_gl_account_number** | **str** |  | [optional] 
**usage_charge_name** | **str** |  | [optional] 
**usage_charge_number** | **str** |  | [optional] 
**adjustment_revenue_gl_string** | **str** |  | [optional] 
**recognized_revenue_gl_string** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_daily_consumption_summary import ExpandedDailyConsumptionSummary

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedDailyConsumptionSummary from a JSON string
expanded_daily_consumption_summary_instance = ExpandedDailyConsumptionSummary.from_json(json)
# print the JSON string representation of the object
print(ExpandedDailyConsumptionSummary.to_json())

# convert the object into a dict
expanded_daily_consumption_summary_dict = expanded_daily_consumption_summary_instance.to_dict()
# create an instance of ExpandedDailyConsumptionSummary from a dict
expanded_daily_consumption_summary_from_dict = ExpandedDailyConsumptionSummary.from_dict(expanded_daily_consumption_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


