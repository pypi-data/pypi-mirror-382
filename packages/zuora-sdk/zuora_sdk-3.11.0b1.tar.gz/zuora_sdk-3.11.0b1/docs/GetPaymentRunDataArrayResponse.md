# GetPaymentRunDataArrayResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[GetPaymentRunDataElementResponse]**](GetPaymentRunDataElementResponse.md) | Container for payment run data. Each element in the array is a record processed by the payment run. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_run_data_array_response import GetPaymentRunDataArrayResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentRunDataArrayResponse from a JSON string
get_payment_run_data_array_response_instance = GetPaymentRunDataArrayResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentRunDataArrayResponse.to_json())

# convert the object into a dict
get_payment_run_data_array_response_dict = get_payment_run_data_array_response_instance.to_dict()
# create an instance of GetPaymentRunDataArrayResponse from a dict
get_payment_run_data_array_response_from_dict = GetPaymentRunDataArrayResponse.from_dict(get_payment_run_data_array_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


