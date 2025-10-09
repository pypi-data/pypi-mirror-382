# PaymentGatewaysResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**paymentgateways** | [**List[PaymentGatwayResponse]**](PaymentGatwayResponse.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.payment_gateways_response import PaymentGatewaysResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentGatewaysResponse from a JSON string
payment_gateways_response_instance = PaymentGatewaysResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentGatewaysResponse.to_json())

# convert the object into a dict
payment_gateways_response_dict = payment_gateways_response_instance.to_dict()
# create an instance of PaymentGatewaysResponse from a dict
payment_gateways_response_from_dict = PaymentGatewaysResponse.from_dict(payment_gateways_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


