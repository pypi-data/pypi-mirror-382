# ErrorResponse401Record


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** |  | [optional] 
**details** | [**List[Error401]**](Error401.md) |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.error_response401_record import ErrorResponse401Record

# TODO update the JSON string below
json = "{}"
# create an instance of ErrorResponse401Record from a JSON string
error_response401_record_instance = ErrorResponse401Record.from_json(json)
# print the JSON string representation of the object
print(ErrorResponse401Record.to_json())

# convert the object into a dict
error_response401_record_dict = error_response401_record_instance.to_dict()
# create an instance of ErrorResponse401Record from a dict
error_response401_record_from_dict = ErrorResponse401Record.from_dict(error_response401_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


