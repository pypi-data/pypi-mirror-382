# CustomObjectRecordWithAllFields

Record data from an object

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by_id** | **str** | The creator&#39;s Id | [optional] 
**created_date** | **datetime** | The record creation time in the date-time format | [optional] 
**id** | **str** | The unique Id of the custom object record | [optional] 
**updated_by_id** | **str** | The modifier&#39;s Id | [optional] 
**updated_date** | **datetime** | The record modification time in the date-time format | [optional] 
**type** | **str** | The type of the custom object record. It is the API name of the custom object definition. | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_record_with_all_fields import CustomObjectRecordWithAllFields

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectRecordWithAllFields from a JSON string
custom_object_record_with_all_fields_instance = CustomObjectRecordWithAllFields.from_json(json)
# print the JSON string representation of the object
print(CustomObjectRecordWithAllFields.to_json())

# convert the object into a dict
custom_object_record_with_all_fields_dict = custom_object_record_with_all_fields_instance.to_dict()
# create an instance of CustomObjectRecordWithAllFields from a dict
custom_object_record_with_all_fields_from_dict = CustomObjectRecordWithAllFields.from_dict(custom_object_record_with_all_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


