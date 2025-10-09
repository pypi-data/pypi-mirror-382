# StageErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Status | [optional] [default to 'Success']
**result** | [**List[StageErrorResponseResultInner]**](StageErrorResponseResultInner.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.stage_error_response import StageErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StageErrorResponse from a JSON string
stage_error_response_instance = StageErrorResponse.from_json(json)
# print the JSON string representation of the object
print(StageErrorResponse.to_json())

# convert the object into a dict
stage_error_response_dict = stage_error_response_instance.to_dict()
# create an instance of StageErrorResponse from a dict
stage_error_response_from_dict = StageErrorResponse.from_dict(stage_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


