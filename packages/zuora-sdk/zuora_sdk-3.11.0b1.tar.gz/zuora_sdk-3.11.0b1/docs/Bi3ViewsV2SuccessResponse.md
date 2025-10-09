# Bi3ViewsV2SuccessResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response status | [optional] [default to 'success']
**result** | **List[object]** | List of data returned for the BI view. | [optional] 
**message** | **str** | Optional message | [optional] 

## Example

```python
from zuora_sdk.models.bi3_views_v2_success_response import Bi3ViewsV2SuccessResponse

# TODO update the JSON string below
json = "{}"
# create an instance of Bi3ViewsV2SuccessResponse from a JSON string
bi3_views_v2_success_response_instance = Bi3ViewsV2SuccessResponse.from_json(json)
# print the JSON string representation of the object
print(Bi3ViewsV2SuccessResponse.to_json())

# convert the object into a dict
bi3_views_v2_success_response_dict = bi3_views_v2_success_response_instance.to_dict()
# create an instance of Bi3ViewsV2SuccessResponse from a dict
bi3_views_v2_success_response_from_dict = Bi3ViewsV2SuccessResponse.from_dict(bi3_views_v2_success_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


