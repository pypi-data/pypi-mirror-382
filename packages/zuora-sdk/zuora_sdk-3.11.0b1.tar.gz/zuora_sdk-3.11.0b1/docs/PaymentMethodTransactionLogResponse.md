# PaymentMethodTransactionLogResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gateway** | **str** |  | [optional] 
**gateway_reason_code** | **str** |  | [optional] 
**gateway_reason_code_description** | **str** |  | [optional] 
**gateway_transaction_type** | **str** |  | [optional] 
**id** | **str** | Object identifier. | [optional] 
**payment_method_id** | **str** |  | [optional] 
**payment_method_type** | **str** |  | [optional] 
**request_string** | **str** |  | [optional] 
**response_string** | **str** |  | [optional] 
**transaction_date** | **datetime** |  | [optional] 
**transaction_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_transaction_log_response import PaymentMethodTransactionLogResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodTransactionLogResponse from a JSON string
payment_method_transaction_log_response_instance = PaymentMethodTransactionLogResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodTransactionLogResponse.to_json())

# convert the object into a dict
payment_method_transaction_log_response_dict = payment_method_transaction_log_response_instance.to_dict()
# create an instance of PaymentMethodTransactionLogResponse from a dict
payment_method_transaction_log_response_from_dict = PaymentMethodTransactionLogResponse.from_dict(payment_method_transaction_log_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


