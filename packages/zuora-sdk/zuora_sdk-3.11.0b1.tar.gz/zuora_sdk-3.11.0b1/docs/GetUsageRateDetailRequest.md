# GetUsageRateDetailRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**GetUsageRateDetailRequestData**](GetUsageRateDetailRequestData.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.    Returns &#x60;false&#x60; if the request was not processed successfully.   | [optional] 

## Example

```python
from zuora_sdk.models.get_usage_rate_detail_request import GetUsageRateDetailRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GetUsageRateDetailRequest from a JSON string
get_usage_rate_detail_request_instance = GetUsageRateDetailRequest.from_json(json)
# print the JSON string representation of the object
print(GetUsageRateDetailRequest.to_json())

# convert the object into a dict
get_usage_rate_detail_request_dict = get_usage_rate_detail_request_instance.to_dict()
# create an instance of GetUsageRateDetailRequest from a dict
get_usage_rate_detail_request_from_dict = GetUsageRateDetailRequest.from_dict(get_usage_rate_detail_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


