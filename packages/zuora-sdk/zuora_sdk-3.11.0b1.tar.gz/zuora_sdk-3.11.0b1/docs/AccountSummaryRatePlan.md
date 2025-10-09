# AccountSummaryRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** | Product ID.  | [optional] 
**product_name** | **str** | Product name.  | [optional] 
**product_rate_plan_id** | **str** | Product Rate Plan ID.  | [optional] 
**product_sku** | **str** |  | [optional] 
**rate_plan_name** | **str** | Rate plan name.  | [optional] 

## Example

```python
from zuora_sdk.models.account_summary_rate_plan import AccountSummaryRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of AccountSummaryRatePlan from a JSON string
account_summary_rate_plan_instance = AccountSummaryRatePlan.from_json(json)
# print the JSON string representation of the object
print(AccountSummaryRatePlan.to_json())

# convert the object into a dict
account_summary_rate_plan_dict = account_summary_rate_plan_instance.to_dict()
# create an instance of AccountSummaryRatePlan from a dict
account_summary_rate_plan_from_dict = AccountSummaryRatePlan.from_dict(account_summary_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


