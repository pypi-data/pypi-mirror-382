# Bi3ViewsErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response status | [optional] 
**message** | **str** | Error message | [optional] 

## Example

```python
from zuora_sdk.models.bi3_views_error_response import Bi3ViewsErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of Bi3ViewsErrorResponse from a JSON string
bi3_views_error_response_instance = Bi3ViewsErrorResponse.from_json(json)
# print the JSON string representation of the object
print(Bi3ViewsErrorResponse.to_json())

# convert the object into a dict
bi3_views_error_response_dict = bi3_views_error_response_instance.to_dict()
# create an instance of Bi3ViewsErrorResponse from a dict
bi3_views_error_response_from_dict = Bi3ViewsErrorResponse.from_dict(bi3_views_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


