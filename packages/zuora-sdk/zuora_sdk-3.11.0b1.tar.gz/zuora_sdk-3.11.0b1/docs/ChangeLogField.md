# ChangeLogField

Represents the order information that will be returned in the GET call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**field_name** | **str** | The field name. | [optional] 
**old_value** | **str** | The old value of this field. | [optional] 
**new_value** | **str** | The new value of this field. | [optional] 

## Example

```python
from zuora_sdk.models.change_log_field import ChangeLogField

# TODO update the JSON string below
json = "{}"
# create an instance of ChangeLogField from a JSON string
change_log_field_instance = ChangeLogField.from_json(json)
# print the JSON string representation of the object
print(ChangeLogField.to_json())

# convert the object into a dict
change_log_field_dict = change_log_field_instance.to_dict()
# create an instance of ChangeLogField from a dict
change_log_field_from_dict = ChangeLogField.from_dict(change_log_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


