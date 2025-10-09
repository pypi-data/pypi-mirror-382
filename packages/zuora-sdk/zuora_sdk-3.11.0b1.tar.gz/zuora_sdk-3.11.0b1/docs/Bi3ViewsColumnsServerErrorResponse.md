# Bi3ViewsColumnsServerErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response status | [optional] 
**message** | **str** | Server error message explaining the issue. | [optional] 

## Example

```python
from zuora_sdk.models.bi3_views_columns_server_error_response import Bi3ViewsColumnsServerErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of Bi3ViewsColumnsServerErrorResponse from a JSON string
bi3_views_columns_server_error_response_instance = Bi3ViewsColumnsServerErrorResponse.from_json(json)
# print the JSON string representation of the object
print(Bi3ViewsColumnsServerErrorResponse.to_json())

# convert the object into a dict
bi3_views_columns_server_error_response_dict = bi3_views_columns_server_error_response_instance.to_dict()
# create an instance of Bi3ViewsColumnsServerErrorResponse from a dict
bi3_views_columns_server_error_response_from_dict = Bi3ViewsColumnsServerErrorResponse.from_dict(bi3_views_columns_server_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


