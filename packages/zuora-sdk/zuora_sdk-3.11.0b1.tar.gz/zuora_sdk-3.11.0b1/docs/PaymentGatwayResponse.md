# PaymentGatwayResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the payment gateway. | [optional] 
**is_active** | **bool** | Specifies if this payment gateway is in active status. | [optional] 
**is_default** | **bool** | Specifies if this is the default payment gateway to process payments for your customer accounts. | [optional] 
**name** | **str** | The name of the payment gateway. | [optional] 
**number** | **str** | The number of the payment gateway. | [optional] 
**type** | **str** | The type of the payment gateway | [optional] 

## Example

```python
from zuora_sdk.models.payment_gatway_response import PaymentGatwayResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentGatwayResponse from a JSON string
payment_gatway_response_instance = PaymentGatwayResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentGatwayResponse.to_json())

# convert the object into a dict
payment_gatway_response_dict = payment_gatway_response_instance.to_dict()
# create an instance of PaymentGatwayResponse from a dict
payment_gatway_response_from_dict = PaymentGatwayResponse.from_dict(payment_gatway_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


