# BillRunFilter


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filter_type** | **str** | To create bill run at account level or subscription level.  | [optional] 
**account_id** | **str** | The target account ID.  | [optional] 
**condition** | [**Condition**](.md) |  | [optional] 
**object_type** | **str** | The target object type of the condition when using FilterCondition filterType.  | [optional] 
**subscription_id** | **str** | The target subscription ID.  | [optional] 
**invoice_schedule_id** | **str** | The target invoice schedule ID.  | [optional] 
**invoice_schedule_item_id** | **str** | The target invoice schedule item ID.  | [optional] 

## Example

```python
from zuora_sdk.models.bill_run_filter import BillRunFilter

# TODO update the JSON string below
json = "{}"
# create an instance of BillRunFilter from a JSON string
bill_run_filter_instance = BillRunFilter.from_json(json)
# print the JSON string representation of the object
print(BillRunFilter.to_json())

# convert the object into a dict
bill_run_filter_dict = bill_run_filter_instance.to_dict()
# create an instance of BillRunFilter from a dict
bill_run_filter_from_dict = BillRunFilter.from_dict(bill_run_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


