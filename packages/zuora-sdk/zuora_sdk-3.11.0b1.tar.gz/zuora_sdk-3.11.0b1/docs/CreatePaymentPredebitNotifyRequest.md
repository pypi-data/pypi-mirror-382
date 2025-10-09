# CreatePaymentPredebitNotifyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_key** | **str** | The unique ID or number of an invoice. For example, &#x60;4a8082e65b27f6c3015b89e4344c16b1&#x60;, or &#x60;INV00000003&#x60;. | 
**payment_method_id** | **str** | The ID of the payment method you want to use. If not provided, the default payment method of the customer account is used. | [optional] 
**payment_gateway_id** | **str** | The ID of the payment gateway instance you want to use. If not provided, the default payment gateway instance of the customer account is used. | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_predebit_notify_request import CreatePaymentPredebitNotifyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentPredebitNotifyRequest from a JSON string
create_payment_predebit_notify_request_instance = CreatePaymentPredebitNotifyRequest.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentPredebitNotifyRequest.to_json())

# convert the object into a dict
create_payment_predebit_notify_request_dict = create_payment_predebit_notify_request_instance.to_dict()
# create an instance of CreatePaymentPredebitNotifyRequest from a dict
create_payment_predebit_notify_request_from_dict = CreatePaymentPredebitNotifyRequest.from_dict(create_payment_predebit_notify_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


