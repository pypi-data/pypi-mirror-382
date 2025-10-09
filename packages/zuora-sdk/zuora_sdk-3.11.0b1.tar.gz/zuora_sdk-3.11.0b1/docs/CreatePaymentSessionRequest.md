# CreatePaymentSessionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account in Zuora that is associated with this payment method. | [optional] 
**amount** | **float** | The amount of the payment.  This field is required if &#x60;processPayment&#x60; is &#x60;true&#x60;.  | [optional] 
**auth_amount** | **float** | The authorization amount for the payment method. Specify a value greater than 0.   This field is required if &#x60;processPayment&#x60; is false. | [optional] 
**currency** | **str** | The currency of the payment in the format of the three-character ISO currency code. | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**payment_gateway** | **str** | The ID of the payment gateway instance configured in Zuora that will process the payment, such as &#x60;e884322ab8c711edab030242ac120004&#x60;. | [optional] 
**process_payment** | **bool** | Indicate whether a payment should be processed after creating the payment method.   If this field is set to &#x60;true&#x60;, you must specify the &#x60;amount&#x60; field.   If this field is set to &#x60;false&#x60;, you must specify the &#x60;authAmount&#x60; field. The payment method will be verified through the payment gateway instance specified in the &#x60;paymentGateway&#x60; field. | [optional] [default to True]
**store_payment_method** | **bool** | true indicates that the payment method will be stored in Zuora and will be used in subsequent recurring payments. false indicates that the payment method will not be stored in Zuora. End-customers need to be brought back on-session to authenticate the payment. | [optional] [default to True]
**invoices** | [**List[CreatePaymentSessionInvoice]**](CreatePaymentSessionInvoice.md) | Container for invoices. The maximum number of invoices is 1,000.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_session_request import CreatePaymentSessionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentSessionRequest from a JSON string
create_payment_session_request_instance = CreatePaymentSessionRequest.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentSessionRequest.to_json())

# convert the object into a dict
create_payment_session_request_dict = create_payment_session_request_instance.to_dict()
# create an instance of CreatePaymentSessionRequest from a dict
create_payment_session_request_from_dict = CreatePaymentSessionRequest.from_dict(create_payment_session_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


