# StageErrorNoRecordResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Status | [optional] [default to 'No Records Found']
**result** | **object** | Response result | [optional] 
**message** | **str** | Response Message | [optional] 

## Example

```python
from zuora_sdk.models.stage_error_no_record_response import StageErrorNoRecordResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StageErrorNoRecordResponse from a JSON string
stage_error_no_record_response_instance = StageErrorNoRecordResponse.from_json(json)
# print the JSON string representation of the object
print(StageErrorNoRecordResponse.to_json())

# convert the object into a dict
stage_error_no_record_response_dict = stage_error_no_record_response_instance.to_dict()
# create an instance of StageErrorNoRecordResponse from a dict
stage_error_no_record_response_from_dict = StageErrorNoRecordResponse.from_dict(stage_error_no_record_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


