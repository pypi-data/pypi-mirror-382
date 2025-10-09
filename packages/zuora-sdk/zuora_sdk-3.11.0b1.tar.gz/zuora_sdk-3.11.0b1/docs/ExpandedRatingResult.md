# ExpandedRatingResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**rate_plan_charge_id** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] 
**amount** | **float** |  | [optional] 
**service_start_date** | **date** |  | [optional] 
**service_end_date** | **date** |  | [optional] 
**status** | **str** |  | [optional] 
**is_partial** | **bool** |  | [optional] 
**charge_segment_number** | **int** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**invoice_item_id** | **str** |  | [optional] 
**actual_period_start_date** | **date** |  | [optional] 
**actual_period_end_date** | **date** |  | [optional] 
**billing_cycle_day** | **int** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**rate_plan_charge** | [**ExpandedRatePlanCharge**](ExpandedRatePlanCharge.md) |  | [optional] 
**subscription** | [**ExpandedSubscription**](ExpandedSubscription.md) |  | [optional] 
**invoice_item** | [**ExpandedInvoiceItem**](ExpandedInvoiceItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_rating_result import ExpandedRatingResult

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRatingResult from a JSON string
expanded_rating_result_instance = ExpandedRatingResult.from_json(json)
# print the JSON string representation of the object
print(ExpandedRatingResult.to_json())

# convert the object into a dict
expanded_rating_result_dict = expanded_rating_result_instance.to_dict()
# create an instance of ExpandedRatingResult from a dict
expanded_rating_result_from_dict = ExpandedRatingResult.from_dict(expanded_rating_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


