# CustomObjectBulkDeleteFilterCondition

Condition evaluated on a single object field

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **str** | The object field that is evaluated. Only filterable fields can be evaluated in the filter. | 
**operator** | [**CustomObjectBulkDeleteFilterConditionOperator**](CustomObjectBulkDeleteFilterConditionOperator.md) |  | 
**value** | **object** | The value that the filterable &#x60;field&#x60; is evaluated against in the filter. The data type of &#x60;value&#x60; is consistent with that of the &#x60;field&#x60;. | 

## Example

```python
from zuora_sdk.models.custom_object_bulk_delete_filter_condition import CustomObjectBulkDeleteFilterCondition

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectBulkDeleteFilterCondition from a JSON string
custom_object_bulk_delete_filter_condition_instance = CustomObjectBulkDeleteFilterCondition.from_json(json)
# print the JSON string representation of the object
print(CustomObjectBulkDeleteFilterCondition.to_json())

# convert the object into a dict
custom_object_bulk_delete_filter_condition_dict = custom_object_bulk_delete_filter_condition_instance.to_dict()
# create an instance of CustomObjectBulkDeleteFilterCondition from a dict
custom_object_bulk_delete_filter_condition_from_dict = CustomObjectBulkDeleteFilterCondition.from_dict(custom_object_bulk_delete_filter_condition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


