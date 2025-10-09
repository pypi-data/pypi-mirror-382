# GetPaymentRunDataElementResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The customer account ID specified in the &#x60;data&#x60; field when creating the payment run.  | [optional] 
**account_number** | **str** | The customer account number specified in the &#x60;data&#x60; field when creating the payment run.  | [optional] 
**amount** | **float** | The amount specified in the &#x60;data&#x60; field when creating the payment run. &#x60;null&#x60; is returned if it was not specified.  | [optional] 
**amount_collected** | **float** | The amount that is collected.  | [optional] 
**amount_to_collect** | **float** | The amount to be collected.  | [optional] 
**comment** | **str** | The comment specified in the &#x60;data&#x60; field when creating the payment run. &#x60;null&#x60; is returned if it was not specified.  | [optional] 
**currency** | **str** | This field is only available if support for standalone payments is enabled.  The currency of the standalone payment. The currency of the standalone payment can be different from the payment currency defined in the customer account settings.  | [optional] 
**document_id** | **str** | The billing document ID specified in the &#x60;data&#x60; field when creating the payment run. &#x60;null&#x60; is returned if it was not specified.  | [optional] 
**document_number** | **str** | The billing document number specified in the &#x60;data&#x60; field when creating the payment run. &#x60;null&#x60; is returned if it was not specified.  | [optional] 
**document_type** | **str** | The billing document type specified in the &#x60;data&#x60; field when creating the payment run. &#x60;null&#x60; is returned if it was not specified.  | [optional] 
**error_code** | **str** | The error code of the response.  | [optional] 
**error_message** | **str** | The detailed information of the error response.  | [optional] 
**payment_gateway_id** | **str** | The payment gateway ID specified in the &#x60;data&#x60; field when creating the payment run. &#x60;null&#x60; is returned if it was not specified.  | [optional] 
**payment_method_id** | **str** | The payment method ID specified in the &#x60;data&#x60; field when creating the payment run. &#x60;null&#x60; is returned if it was not specified.  | [optional] 
**result** | **str** | Indicates whether the data is processed successfully or not.  | [optional] 
**standalone** | **bool** | This field is only available if the support for standalone payment is enabled.  The value &#x60;true&#x60; indicates this is a standalone payment that is created and processed in Zuora through Zuora gateway integration but will be settled outside of Zuora. No settlement data will be created. The standalone payment cannot be applied, unapplied, or transferred.  | [optional] 
**transactions** | [**List[GetPaymentRunDataTransactionElementResponse]**](GetPaymentRunDataTransactionElementResponse.md) | Container for transactions that apply to the current request. Each element contains an array of the settlement/payment applied to the record.  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_run_data_element_response import GetPaymentRunDataElementResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentRunDataElementResponse from a JSON string
get_payment_run_data_element_response_instance = GetPaymentRunDataElementResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentRunDataElementResponse.to_json())

# convert the object into a dict
get_payment_run_data_element_response_dict = get_payment_run_data_element_response_instance.to_dict()
# create an instance of GetPaymentRunDataElementResponse from a dict
get_payment_run_data_element_response_from_dict = GetPaymentRunDataElementResponse.from_dict(get_payment_run_data_element_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


