# GetPaymentsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**payments** | [**List[Payment]**](Payment.md) | Container for payments.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_payments_response import GetPaymentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentsResponse from a JSON string
get_payments_response_instance = GetPaymentsResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentsResponse.to_json())

# convert the object into a dict
get_payments_response_dict = get_payments_response_instance.to_dict()
# create an instance of GetPaymentsResponse from a dict
get_payments_response_from_dict = GetPaymentsResponse.from_dict(get_payments_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


