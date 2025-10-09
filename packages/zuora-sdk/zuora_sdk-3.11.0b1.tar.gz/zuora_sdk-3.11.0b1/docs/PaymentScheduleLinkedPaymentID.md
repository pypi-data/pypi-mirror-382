# PaymentScheduleLinkedPaymentID


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_id** | **str** | ID of the payment.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_schedule_linked_payment_id import PaymentScheduleLinkedPaymentID

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentScheduleLinkedPaymentID from a JSON string
payment_schedule_linked_payment_id_instance = PaymentScheduleLinkedPaymentID.from_json(json)
# print the JSON string representation of the object
print(PaymentScheduleLinkedPaymentID.to_json())

# convert the object into a dict
payment_schedule_linked_payment_id_dict = payment_schedule_linked_payment_id_instance.to_dict()
# create an instance of PaymentScheduleLinkedPaymentID from a dict
payment_schedule_linked_payment_id_from_dict = PaymentScheduleLinkedPaymentID.from_dict(payment_schedule_linked_payment_id_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


