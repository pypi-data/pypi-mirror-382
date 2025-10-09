# DataQueryErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** | Error code.  | [optional] 
**message** | **str** | Error message.  | [optional] 

## Example

```python
from zuora_sdk.models.data_query_error_response import DataQueryErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DataQueryErrorResponse from a JSON string
data_query_error_response_instance = DataQueryErrorResponse.from_json(json)
# print the JSON string representation of the object
print(DataQueryErrorResponse.to_json())

# convert the object into a dict
data_query_error_response_dict = data_query_error_response_instance.to_dict()
# create an instance of DataQueryErrorResponse from a dict
data_query_error_response_from_dict = DataQueryErrorResponse.from_dict(data_query_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


