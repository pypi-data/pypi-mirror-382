# SignUpResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The account id for the order. | [optional] 
**account_number** | **str** | The account number for the order. | [optional] 
**credit_memo_id** | **str** | An array of the credit memo id generated in this order request. The credit memo is only available if you have the Invoice Settlement feature enabled. | [optional] 
**credit_memo_number** | **str** | An array of the credit memo numbers generated in this order request. The credit memo is only available if you have the Invoice Settlement feature enabled. | [optional] 
**invoice_id** | **str** | The invoice id generated in this order request | [optional] 
**invoice_number** | **str** | The invoice number generated in this order request | [optional] 
**order_number** | **str** | The order number of the order created. | [optional] 
**paid_amount** | **str** | The total amount collected in this order request. | [optional] 
**payment_id** | **str** | The payment id that is collected in this order request. | [optional] 
**payment_number** | **str** | The payment number that is collected in this order request. | [optional] 
**process_id** | **str** | The Id of the process that handles the operation.  | [optional] 
**reasons** | [**List[SignUpResponseReasons]**](SignUpResponseReasons.md) |  | [optional] 
**status** | [**SignUpResponseStatus**](SignUpResponseStatus.md) |  | [optional] 
**subscription_id** | **str** | The subscription id of the order. | [optional] 
**subscription_number** | **str** | The subscription number of the order. | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.sign_up_response import SignUpResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpResponse from a JSON string
sign_up_response_instance = SignUpResponse.from_json(json)
# print the JSON string representation of the object
print(SignUpResponse.to_json())

# convert the object into a dict
sign_up_response_dict = sign_up_response_instance.to_dict()
# create an instance of SignUpResponse from a dict
sign_up_response_from_dict = SignUpResponse.from_dict(sign_up_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


