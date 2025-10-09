# BiViews1ErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.bi_views1_error_response import BiViews1ErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BiViews1ErrorResponse from a JSON string
bi_views1_error_response_instance = BiViews1ErrorResponse.from_json(json)
# print the JSON string representation of the object
print(BiViews1ErrorResponse.to_json())

# convert the object into a dict
bi_views1_error_response_dict = bi_views1_error_response_instance.to_dict()
# create an instance of BiViews1ErrorResponse from a dict
bi_views1_error_response_from_dict = BiViews1ErrorResponse.from_dict(bi_views1_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


