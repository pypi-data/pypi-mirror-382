# CustomObjectBulkDeleteFilter

Filters to determine which records to be deleted in the bulk delete operation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conditions** | [**List[CustomObjectBulkDeleteFilterCondition]**](CustomObjectBulkDeleteFilterCondition.md) | Group of field filter conditions that are evaluated in conjunction with each other using the AND operator. The minimum number of conditions is 1 and the maximum is 2. | 

## Example

```python
from zuora_sdk.models.custom_object_bulk_delete_filter import CustomObjectBulkDeleteFilter

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectBulkDeleteFilter from a JSON string
custom_object_bulk_delete_filter_instance = CustomObjectBulkDeleteFilter.from_json(json)
# print the JSON string representation of the object
print(CustomObjectBulkDeleteFilter.to_json())

# convert the object into a dict
custom_object_bulk_delete_filter_dict = custom_object_bulk_delete_filter_instance.to_dict()
# create an instance of CustomObjectBulkDeleteFilter from a dict
custom_object_bulk_delete_filter_from_dict = CustomObjectBulkDeleteFilter.from_dict(custom_object_bulk_delete_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


