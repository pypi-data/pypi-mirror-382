# ActionsErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.actions_error_response import ActionsErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ActionsErrorResponse from a JSON string
actions_error_response_instance = ActionsErrorResponse.from_json(json)
# print the JSON string representation of the object
print(ActionsErrorResponse.to_json())

# convert the object into a dict
actions_error_response_dict = actions_error_response_instance.to_dict()
# create an instance of ActionsErrorResponse from a dict
actions_error_response_from_dict = ActionsErrorResponse.from_dict(actions_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


