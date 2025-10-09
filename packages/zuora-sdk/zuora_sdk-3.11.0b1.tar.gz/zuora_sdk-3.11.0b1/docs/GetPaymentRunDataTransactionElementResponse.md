# GetPaymentRunDataTransactionElementResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The total amount of the newly generated payment.  **Note:** This field is only available if &#x60;type&#x60; is &#x60;Payment&#x60;.  | [optional] 
**applied_amount** | **float** | The amount allocated to this data record.  | [optional] 
**error_code** | **str** | The error code of the response.  **Note:** This field is only available if &#x60;type&#x60; is &#x60;Payment&#x60;.  | [optional] 
**error_message** | **str** | The detailed information of the error response.  **Note:** This field is only available if &#x60;type&#x60; is &#x60;Payment&#x60;.  | [optional] 
**id** | **str** | The ID of the current transaction.  | [optional] 
**status** | [**GetPaymentRunDataTransactionElementResponseStatus**](GetPaymentRunDataTransactionElementResponseStatus.md) |  | [optional] 
**type** | [**GetPaymentRunDataTransactionElementResponseType**](GetPaymentRunDataTransactionElementResponseType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_run_data_transaction_element_response import GetPaymentRunDataTransactionElementResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentRunDataTransactionElementResponse from a JSON string
get_payment_run_data_transaction_element_response_instance = GetPaymentRunDataTransactionElementResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentRunDataTransactionElementResponse.to_json())

# convert the object into a dict
get_payment_run_data_transaction_element_response_dict = get_payment_run_data_transaction_element_response_instance.to_dict()
# create an instance of GetPaymentRunDataTransactionElementResponse from a dict
get_payment_run_data_transaction_element_response_from_dict = GetPaymentRunDataTransactionElementResponse.from_dict(get_payment_run_data_transaction_element_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


