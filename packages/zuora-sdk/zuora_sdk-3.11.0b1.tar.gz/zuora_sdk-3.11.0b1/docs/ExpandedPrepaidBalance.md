# ExpandedPrepaidBalance


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**total_fund** | **float** |  | [optional] 
**balance** | **float** |  | [optional] 
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 
**account_id** | **str** |  | [optional] 
**orig_subscription_id** | **str** |  | [optional] 
**u_om** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**prepaid_balance_state** | **str** |  | [optional] 
**prepaid_type** | **int** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**orig_subscription** | [**ExpandedSubscription**](ExpandedSubscription.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_prepaid_balance import ExpandedPrepaidBalance

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPrepaidBalance from a JSON string
expanded_prepaid_balance_instance = ExpandedPrepaidBalance.from_json(json)
# print the JSON string representation of the object
print(ExpandedPrepaidBalance.to_json())

# convert the object into a dict
expanded_prepaid_balance_dict = expanded_prepaid_balance_instance.to_dict()
# create an instance of ExpandedPrepaidBalance from a dict
expanded_prepaid_balance_from_dict = ExpandedPrepaidBalance.from_dict(expanded_prepaid_balance_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


