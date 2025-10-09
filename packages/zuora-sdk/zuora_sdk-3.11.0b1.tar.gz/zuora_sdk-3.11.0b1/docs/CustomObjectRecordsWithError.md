# CustomObjectRecordsWithError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** | See [Custom Objects API error code](https://knowledgecenter.zuora.com/Central_Platform/Custom_Objects/Z_Custom_Objects_API#Custom_Objects_API_error_code) for details. | [optional] 
**message** | **str** |  | [optional] 
**record** | [**CustomObjectRecordWithAllFields**](CustomObjectRecordWithAllFields.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_records_with_error import CustomObjectRecordsWithError

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectRecordsWithError from a JSON string
custom_object_records_with_error_instance = CustomObjectRecordsWithError.from_json(json)
# print the JSON string representation of the object
print(CustomObjectRecordsWithError.to_json())

# convert the object into a dict
custom_object_records_with_error_dict = custom_object_records_with_error_instance.to_dict()
# create an instance of CustomObjectRecordsWithError from a dict
custom_object_records_with_error_from_dict = CustomObjectRecordsWithError.from_dict(custom_object_records_with_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


