# PaymentSchedulePaymentOptionFieldsDetail

The field used to pass the transactional payment data to the gateway side in the key-value format.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | The name of the field.  | [optional] 
**value** | **str** | The value of the field.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_schedule_payment_option_fields_detail import PaymentSchedulePaymentOptionFieldsDetail

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentSchedulePaymentOptionFieldsDetail from a JSON string
payment_schedule_payment_option_fields_detail_instance = PaymentSchedulePaymentOptionFieldsDetail.from_json(json)
# print the JSON string representation of the object
print(PaymentSchedulePaymentOptionFieldsDetail.to_json())

# convert the object into a dict
payment_schedule_payment_option_fields_detail_dict = payment_schedule_payment_option_fields_detail_instance.to_dict()
# create an instance of PaymentSchedulePaymentOptionFieldsDetail from a dict
payment_schedule_payment_option_fields_detail_from_dict = PaymentSchedulePaymentOptionFieldsDetail.from_dict(payment_schedule_payment_option_fields_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


