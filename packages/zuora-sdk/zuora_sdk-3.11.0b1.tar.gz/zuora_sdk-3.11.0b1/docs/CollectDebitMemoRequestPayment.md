# CollectDebitMemoRequestPayment

Some detail info that would be used to processed an electronic payment. The info would only effect when `collect` set to `true`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gateway_id** | **str** | The ID of the gateway instance that processes the payment. The ID must be a valid gateway instance ID and this gateway must support the specific payment method.  If no gateway ID is specified in the request body, the default gateway for the customer account is used automatically, if this default one is not configured, the default gateway of the tenant would be used. | [optional] 
**payment_method_id** | **str** | The unique ID of the payment method that the customer used to make the payment.  If no payment method ID is specified in the request body, the default payment method for the customer account is used automatically. If the default payment method is different from the type of payments that you want to create, an error occurs. | [optional] 
**cryptogram** | **str** | Cryptogram value supplied by the token provider if DPAN or network scheme token is present  To ensure PCI compliance, this value is not stored and cannot be queried. | [optional] 

## Example

```python
from zuora_sdk.models.collect_debit_memo_request_payment import CollectDebitMemoRequestPayment

# TODO update the JSON string below
json = "{}"
# create an instance of CollectDebitMemoRequestPayment from a JSON string
collect_debit_memo_request_payment_instance = CollectDebitMemoRequestPayment.from_json(json)
# print the JSON string representation of the object
print(CollectDebitMemoRequestPayment.to_json())

# convert the object into a dict
collect_debit_memo_request_payment_dict = collect_debit_memo_request_payment_instance.to_dict()
# create an instance of CollectDebitMemoRequestPayment from a dict
collect_debit_memo_request_payment_from_dict = CollectDebitMemoRequestPayment.from_dict(collect_debit_memo_request_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


