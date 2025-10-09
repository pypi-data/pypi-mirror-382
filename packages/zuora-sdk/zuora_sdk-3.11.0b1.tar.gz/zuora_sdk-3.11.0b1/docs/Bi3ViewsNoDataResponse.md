# Bi3ViewsNoDataResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response status | [optional] [default to 'success']
**message** | **str** | No data available for the given query. | [optional] 

## Example

```python
from zuora_sdk.models.bi3_views_no_data_response import Bi3ViewsNoDataResponse

# TODO update the JSON string below
json = "{}"
# create an instance of Bi3ViewsNoDataResponse from a JSON string
bi3_views_no_data_response_instance = Bi3ViewsNoDataResponse.from_json(json)
# print the JSON string representation of the object
print(Bi3ViewsNoDataResponse.to_json())

# convert the object into a dict
bi3_views_no_data_response_dict = bi3_views_no_data_response_instance.to_dict()
# create an instance of Bi3ViewsNoDataResponse from a dict
bi3_views_no_data_response_from_dict = Bi3ViewsNoDataResponse.from_dict(bi3_views_no_data_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


