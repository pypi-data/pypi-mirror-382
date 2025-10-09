# Bi3ViewsServerErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response status | [optional] 
**message** | **str** | Server error message explaining the issue. | [optional] 

## Example

```python
from zuora_sdk.models.bi3_views_server_error_response import Bi3ViewsServerErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of Bi3ViewsServerErrorResponse from a JSON string
bi3_views_server_error_response_instance = Bi3ViewsServerErrorResponse.from_json(json)
# print the JSON string representation of the object
print(Bi3ViewsServerErrorResponse.to_json())

# convert the object into a dict
bi3_views_server_error_response_dict = bi3_views_server_error_response_instance.to_dict()
# create an instance of Bi3ViewsServerErrorResponse from a dict
bi3_views_server_error_response_from_dict = Bi3ViewsServerErrorResponse.from_dict(bi3_views_server_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


