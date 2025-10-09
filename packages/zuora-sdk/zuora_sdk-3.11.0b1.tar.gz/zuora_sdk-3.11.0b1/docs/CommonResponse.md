# CommonResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]

## Example

```python
from zuora_sdk.models.common_response import CommonResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CommonResponse from a JSON string
common_response_instance = CommonResponse.from_json(json)
# print the JSON string representation of the object
print(CommonResponse.to_json())

# convert the object into a dict
common_response_dict = common_response_instance.to_dict()
# create an instance of CommonResponse from a dict
common_response_from_dict = CommonResponse.from_dict(common_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


