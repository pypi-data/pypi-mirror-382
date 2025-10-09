# BiViews1SelectSuccessResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Status | [optional] [default to 'success']
**view_data** | **object** | Data for the selected BI View | [optional] 

## Example

```python
from zuora_sdk.models.bi_views1_select_success_response import BiViews1SelectSuccessResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BiViews1SelectSuccessResponse from a JSON string
bi_views1_select_success_response_instance = BiViews1SelectSuccessResponse.from_json(json)
# print the JSON string representation of the object
print(BiViews1SelectSuccessResponse.to_json())

# convert the object into a dict
bi_views1_select_success_response_dict = bi_views1_select_success_response_instance.to_dict()
# create an instance of BiViews1SelectSuccessResponse from a dict
bi_views1_select_success_response_from_dict = BiViews1SelectSuccessResponse.from_dict(bi_views1_select_success_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


