# ElectronicPaymentOptions

Container for the electronic payment options. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_gateway_id** | **str** | Specifies the ID of a payment gateway to override the default gateway. If this field is not specified, the default payment gateway will be used to process the payment. | [optional] 
**payment_method_id** | **str** | Specifies an electronic payment method. It can be one that has already been associated with an invoice owner, or an orphan payment method, which is not associated with any invoice owner. For an orphan payment method, this operation will then associate it with the account that this order will be created under. | [optional] 

## Example

```python
from zuora_sdk.models.electronic_payment_options import ElectronicPaymentOptions

# TODO update the JSON string below
json = "{}"
# create an instance of ElectronicPaymentOptions from a JSON string
electronic_payment_options_instance = ElectronicPaymentOptions.from_json(json)
# print the JSON string representation of the object
print(ElectronicPaymentOptions.to_json())

# convert the object into a dict
electronic_payment_options_dict = electronic_payment_options_instance.to_dict()
# create an instance of ElectronicPaymentOptions from a dict
electronic_payment_options_from_dict = ElectronicPaymentOptions.from_dict(electronic_payment_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


