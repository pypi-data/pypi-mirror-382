# CreateAuthorizationResponsePaymentGateway

The response data returned from the gateway. This field is available only if the `success` field is `false` and the support for returning additional error information from the gateway is enabled.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**additional_info** | **object** | The additional information returned from the gateway. The returned fields vary for gateways. Here is an example.   &#x60;&#x60;&#x60;  \&quot;additionalInfo\&quot;: {   \&quot;ProcessorName\&quot;: \&quot;MasterCard Saferpay Test\&quot;,   \&quot;ProcessorResult\&quot;: \&quot;51\&quot;,   \&quot;ProcessorMessage\&quot;: \&quot;Insufficient funds\&quot;,   \&quot;ErrorName\&quot;: \&quot;TRANSACTION_DECLINED\&quot; }  &#x60;&#x60;&#x60; | [optional] 
**gateway_response_code** | **str** | The HTTP response code.  | [optional] 
**gateway_response_message** | **str** | The error message returned from the gateway.  | [optional] 
**gateway_type** | **str** | The gateway type.  | [optional] 
**gateway_version** | **str** | The gateway version.  | [optional] 

## Example

```python
from zuora_sdk.models.create_authorization_response_payment_gateway import CreateAuthorizationResponsePaymentGateway

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAuthorizationResponsePaymentGateway from a JSON string
create_authorization_response_payment_gateway_instance = CreateAuthorizationResponsePaymentGateway.from_json(json)
# print the JSON string representation of the object
print(CreateAuthorizationResponsePaymentGateway.to_json())

# convert the object into a dict
create_authorization_response_payment_gateway_dict = create_authorization_response_payment_gateway_instance.to_dict()
# create an instance of CreateAuthorizationResponsePaymentGateway from a dict
create_authorization_response_payment_gateway_from_dict = CreateAuthorizationResponsePaymentGateway.from_dict(create_authorization_response_payment_gateway_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


