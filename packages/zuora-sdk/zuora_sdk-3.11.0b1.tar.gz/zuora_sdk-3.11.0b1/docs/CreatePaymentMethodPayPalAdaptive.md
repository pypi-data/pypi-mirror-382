# CreatePaymentMethodPayPalAdaptive


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**preapproval_key** | **str** | The PayPal preapproval key.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_pay_pal_adaptive import CreatePaymentMethodPayPalAdaptive

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodPayPalAdaptive from a JSON string
create_payment_method_pay_pal_adaptive_instance = CreatePaymentMethodPayPalAdaptive.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodPayPalAdaptive.to_json())

# convert the object into a dict
create_payment_method_pay_pal_adaptive_dict = create_payment_method_pay_pal_adaptive_instance.to_dict()
# create an instance of CreatePaymentMethodPayPalAdaptive from a dict
create_payment_method_pay_pal_adaptive_from_dict = CreatePaymentMethodPayPalAdaptive.from_dict(create_payment_method_pay_pal_adaptive_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


