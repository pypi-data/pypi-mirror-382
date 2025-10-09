# GetPaymentRunsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | The URL for requesting the next page of the response, if it exists; otherwise absent. | [optional] 
**payment_runs** | [**List[PaymentRun]**](PaymentRun.md) | Container for payment runs.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_runs_response import GetPaymentRunsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentRunsResponse from a JSON string
get_payment_runs_response_instance = GetPaymentRunsResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentRunsResponse.to_json())

# convert the object into a dict
get_payment_runs_response_dict = get_payment_runs_response_instance.to_dict()
# create an instance of GetPaymentRunsResponse from a dict
get_payment_runs_response_from_dict = GetPaymentRunsResponse.from_dict(get_payment_runs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


