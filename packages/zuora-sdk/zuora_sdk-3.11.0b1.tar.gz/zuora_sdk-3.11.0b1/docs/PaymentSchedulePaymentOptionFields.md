# PaymentSchedulePaymentOptionFields


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | [**PaymentSchedulePaymentOptionFieldsDetail**](PaymentSchedulePaymentOptionFieldsDetail.md) |  | [optional] 
**type** | **str** | The type of the payment option. Currently, only &#x60;GatewayOptions&#x60; is supported for specifying Gateway Options fields supported by a payment gateway. | [optional] 

## Example

```python
from zuora_sdk.models.payment_schedule_payment_option_fields import PaymentSchedulePaymentOptionFields

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentSchedulePaymentOptionFields from a JSON string
payment_schedule_payment_option_fields_instance = PaymentSchedulePaymentOptionFields.from_json(json)
# print the JSON string representation of the object
print(PaymentSchedulePaymentOptionFields.to_json())

# convert the object into a dict
payment_schedule_payment_option_fields_dict = payment_schedule_payment_option_fields_instance.to_dict()
# create an instance of PaymentSchedulePaymentOptionFields from a dict
payment_schedule_payment_option_fields_from_dict = PaymentSchedulePaymentOptionFields.from_dict(payment_schedule_payment_option_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


