# StageErrorResponseResultInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **int** |  | [optional] 
**crtd_by** | **str** |  | [optional] 
**crtd_dt** | **datetime** |  | [optional] 
**err_msg** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**inv_line_id** | **str** |  | [optional] 
**inv_line_num** | **str** |  | [optional] 
**processed_flag** | **str** |  | [optional] 
**sec_atr_val** | **str** |  | [optional] 
**so_line_id** | **str** |  | [optional] 
**so_line_num** | **str** |  | [optional] 
**so_num** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**updt_by** | **str** |  | [optional] 
**updt_dt** | **datetime** |  | [optional] 
**upload_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.stage_error_response_result_inner import StageErrorResponseResultInner

# TODO update the JSON string below
json = "{}"
# create an instance of StageErrorResponseResultInner from a JSON string
stage_error_response_result_inner_instance = StageErrorResponseResultInner.from_json(json)
# print the JSON string representation of the object
print(StageErrorResponseResultInner.to_json())

# convert the object into a dict
stage_error_response_result_inner_dict = stage_error_response_result_inner_instance.to_dict()
# create an instance of StageErrorResponseResultInner from a dict
stage_error_response_result_inner_from_dict = StageErrorResponseResultInner.from_dict(stage_error_response_result_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


