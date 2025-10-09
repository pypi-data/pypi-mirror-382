# CancelAuthorizationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account. This field is generally required, but is optional if you are using the Ingenico ePayments gateway. | [optional] 
**account_number** | **str** | The number of the customer account. This field is generally required, but is optional if you are using the Ingenico ePayments gateway. | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**gateway_order_id** | **str** | The order ID for the specific gateway.   The specified order ID will be used in transaction authorization. If you specify an empty value for this field, Zuora will generate an ID and you will have to associate this ID with your order ID by yourself if needed. It is recommended to specify an ID for this field. | 
**payment_gateway_id** | **str** | The ID of the payment gateway instance. This field is required if you do not specify the &#x60;accountId&#x60; and &#x60;accountNumber&#x60; fields. | [optional] 
**transaction_id** | **str** | The ID of the transaction. | 

## Example

```python
from zuora_sdk.models.cancel_authorization_request import CancelAuthorizationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CancelAuthorizationRequest from a JSON string
cancel_authorization_request_instance = CancelAuthorizationRequest.from_json(json)
# print the JSON string representation of the object
print(CancelAuthorizationRequest.to_json())

# convert the object into a dict
cancel_authorization_request_dict = cancel_authorization_request_instance.to_dict()
# create an instance of CancelAuthorizationRequest from a dict
cancel_authorization_request_from_dict = CancelAuthorizationRequest.from_dict(cancel_authorization_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


