# ExpandedUsage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** |  | [optional] 
**account_number** | **str** |  | [optional] 
**rate_plan_charge_id** | **str** |  | [optional] 
**end_date_time** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] 
**rbe_status** | **str** |  | [optional] 
**source_type** | **str** |  | [optional] 
**start_date_time** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**submission_date_time** | **str** |  | [optional] 
**u_om** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**import_id** | **str** |  | [optional] 
**unique_key** | **str** |  | [optional] 
**file_id** | **str** |  | [optional] 
**file_name** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_usage import ExpandedUsage

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedUsage from a JSON string
expanded_usage_instance = ExpandedUsage.from_json(json)
# print the JSON string representation of the object
print(ExpandedUsage.to_json())

# convert the object into a dict
expanded_usage_dict = expanded_usage_instance.to_dict()
# create an instance of ExpandedUsage from a dict
expanded_usage_from_dict = ExpandedUsage.from_dict(expanded_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


