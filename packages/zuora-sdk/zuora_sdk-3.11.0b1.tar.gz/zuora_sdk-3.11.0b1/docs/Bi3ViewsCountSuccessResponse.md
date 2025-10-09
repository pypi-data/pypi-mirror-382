# Bi3ViewsCountSuccessResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response status | [optional] [default to 'success']
**count** | **int** | Total record count for the BI View. | [optional] 

## Example

```python
from zuora_sdk.models.bi3_views_count_success_response import Bi3ViewsCountSuccessResponse

# TODO update the JSON string below
json = "{}"
# create an instance of Bi3ViewsCountSuccessResponse from a JSON string
bi3_views_count_success_response_instance = Bi3ViewsCountSuccessResponse.from_json(json)
# print the JSON string representation of the object
print(Bi3ViewsCountSuccessResponse.to_json())

# convert the object into a dict
bi3_views_count_success_response_dict = bi3_views_count_success_response_instance.to_dict()
# create an instance of Bi3ViewsCountSuccessResponse from a dict
bi3_views_count_success_response_from_dict = Bi3ViewsCountSuccessResponse.from_dict(bi3_views_count_success_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


