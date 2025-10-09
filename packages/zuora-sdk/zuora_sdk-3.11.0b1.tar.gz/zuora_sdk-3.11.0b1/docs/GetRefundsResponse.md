# GetRefundsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**refunds** | [**List[Refund]**](Refund.md) | Container for refunds.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_refunds_response import GetRefundsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetRefundsResponse from a JSON string
get_refunds_response_instance = GetRefundsResponse.from_json(json)
# print the JSON string representation of the object
print(GetRefundsResponse.to_json())

# convert the object into a dict
get_refunds_response_dict = get_refunds_response_instance.to_dict()
# create an instance of GetRefundsResponse from a dict
get_refunds_response_from_dict = GetRefundsResponse.from_dict(get_refunds_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


