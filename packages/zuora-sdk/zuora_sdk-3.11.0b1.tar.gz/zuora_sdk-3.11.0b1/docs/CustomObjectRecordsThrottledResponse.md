# CustomObjectRecordsThrottledResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** |  | [optional] 
**details** | [**List[CustomObjectRecordsWithError]**](CustomObjectRecordsWithError.md) |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_records_throttled_response import CustomObjectRecordsThrottledResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectRecordsThrottledResponse from a JSON string
custom_object_records_throttled_response_instance = CustomObjectRecordsThrottledResponse.from_json(json)
# print the JSON string representation of the object
print(CustomObjectRecordsThrottledResponse.to_json())

# convert the object into a dict
custom_object_records_throttled_response_dict = custom_object_records_throttled_response_instance.to_dict()
# create an instance of CustomObjectRecordsThrottledResponse from a dict
custom_object_records_throttled_response_from_dict = CustomObjectRecordsThrottledResponse.from_dict(custom_object_records_throttled_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


