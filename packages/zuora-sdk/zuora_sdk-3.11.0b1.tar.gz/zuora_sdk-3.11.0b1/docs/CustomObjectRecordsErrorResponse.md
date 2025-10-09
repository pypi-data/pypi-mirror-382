# CustomObjectRecordsErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** |  | [optional] 
**details** | [**List[CustomObjectRecordsWithError]**](CustomObjectRecordsWithError.md) |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_records_error_response import CustomObjectRecordsErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectRecordsErrorResponse from a JSON string
custom_object_records_error_response_instance = CustomObjectRecordsErrorResponse.from_json(json)
# print the JSON string representation of the object
print(CustomObjectRecordsErrorResponse.to_json())

# convert the object into a dict
custom_object_records_error_response_dict = custom_object_records_error_response_instance.to_dict()
# create an instance of CustomObjectRecordsErrorResponse from a dict
custom_object_records_error_response_from_dict = CustomObjectRecordsErrorResponse.from_dict(custom_object_records_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


