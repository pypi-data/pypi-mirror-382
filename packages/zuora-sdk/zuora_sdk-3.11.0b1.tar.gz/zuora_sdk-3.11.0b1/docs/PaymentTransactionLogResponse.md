# PaymentTransactionLogResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**avs_response_code** | **str** | The response code returned by the payment gateway referring to the AVS international response of the payment transaction.  | [optional] 
**batch_id** | **str** | The ID of the batch used to send the transaction if the request was sent in a batch.  | [optional] 
**cvv_response_code** | **str** | The response code returned by the payment gateway referring to the CVV international response of the payment transaction.  | [optional] 
**gateway** | **str** | The name of the payment gateway used to transact the current payment transaction log.  | [optional] 
**gateway_reason_code** | **str** | The code returned by the payment gateway for the payment. This code is gateway-dependent.  | [optional] 
**gateway_reason_code_description** | **str** | The message returned by the payment gateway for the payment. This message is gateway-dependent.   | [optional] 
**gateway_state** | [**GatewayState**](GatewayState.md) |  | [optional] 
**gateway_transaction_type** | [**GetPaymentTransactionLogResponseGatewayTransactionType**](GetPaymentTransactionLogResponseGatewayTransactionType.md) |  | [optional] 
**id** | **str** | The ID of the payment transaction log.  | [optional] 
**payment_id** | **str** | The ID of the payment wherein the payment transaction log was recorded.   | [optional] 
**request_string** | **str** | The payment transaction request string sent to the payment gateway.   | [optional] 
**response_string** | **str** | The payment transaction response string returned by the payment gateway.   | [optional] 
**transaction_date** | **datetime** | The transaction date when the payment was performed.   | [optional] 
**transaction_id** | **str** | The transaction ID returned by the payment gateway. This field is used to reconcile payment transactions between the payment gateway and records in Zuora.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_transaction_log_response import PaymentTransactionLogResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentTransactionLogResponse from a JSON string
payment_transaction_log_response_instance = PaymentTransactionLogResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentTransactionLogResponse.to_json())

# convert the object into a dict
payment_transaction_log_response_dict = payment_transaction_log_response_instance.to_dict()
# create an instance of PaymentTransactionLogResponse from a dict
payment_transaction_log_response_from_dict = PaymentTransactionLogResponse.from_dict(payment_transaction_log_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


