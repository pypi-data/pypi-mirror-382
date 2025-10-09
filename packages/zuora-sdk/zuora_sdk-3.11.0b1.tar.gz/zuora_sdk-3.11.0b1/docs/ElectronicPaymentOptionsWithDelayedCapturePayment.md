# ElectronicPaymentOptionsWithDelayedCapturePayment

Container for the electronic payment options. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_gateway_id** | **str** | Specifies the ID of a payment gateway to override the default gateway. If this field is not specified, the default payment gateway will be used to process the payment. | [optional] 
**payment_method_id** | **str** | Specifies an electronic payment method. It can be one that has already been associated with an invoice owner, or an orphan payment method, which is not associated with any invoice owner. For an orphan payment method, this operation will then associate it with the account that this order will be created under. | [optional] 
**auth_transaction_id** | **str** | The authorization transaction ID from the payment gateway.  When you create a payment to capture the funds that have been authorized  through [Create Authorization](https://developer.zuora.com/api-references/api/operation/POST_CreateAuthorization/), pass in the &#x60;authTransactionId&#x60; field.  It is highly recommended to also pass in &#x60;gatewayOrderId&#x60; that you used  when authorizing the funds.  &#x60;authTransactionId&#x60; is required, while &#x60;gatewayOrderId&#x60; is optional. | [optional] 
**gateway_order_id** | **str** | A merchant-specified natural key value that can be passed to the electronic payment gateway when  a payment is created. If not specified, the payment number will be passed in instead.  Gateways check duplicates on the gateway order ID to ensure that the same transaction  is not entered twice accidentally.   This ID can also be used to do reconciliation and tie the payment to a natural key in external systems.  The source of this ID varies by merchant. Some merchants use shopping cart order IDs, and others use something  different. Merchants use this ID to track transactions in their eCommerce systems.   When you create a payment to capture the funds that have been authorized through [Create Authorizattion](https://developer.zuora.com/api-references/api/operation/POST_CreateAuthorization/),  pass in the &#x60;authTransactionId&#x60; field. It is highly recommended to also pass in &#x60;gatewayOrderId&#x60; that you used  when authorizing the funds. &#x60;authTransactionId&#x60; is required, while &#x60;gatewayOrderId&#x60; is optional. | [optional] 

## Example

```python
from zuora_sdk.models.electronic_payment_options_with_delayed_capture_payment import ElectronicPaymentOptionsWithDelayedCapturePayment

# TODO update the JSON string below
json = "{}"
# create an instance of ElectronicPaymentOptionsWithDelayedCapturePayment from a JSON string
electronic_payment_options_with_delayed_capture_payment_instance = ElectronicPaymentOptionsWithDelayedCapturePayment.from_json(json)
# print the JSON string representation of the object
print(ElectronicPaymentOptionsWithDelayedCapturePayment.to_json())

# convert the object into a dict
electronic_payment_options_with_delayed_capture_payment_dict = electronic_payment_options_with_delayed_capture_payment_instance.to_dict()
# create an instance of ElectronicPaymentOptionsWithDelayedCapturePayment from a dict
electronic_payment_options_with_delayed_capture_payment_from_dict = ElectronicPaymentOptionsWithDelayedCapturePayment.from_dict(electronic_payment_options_with_delayed_capture_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


