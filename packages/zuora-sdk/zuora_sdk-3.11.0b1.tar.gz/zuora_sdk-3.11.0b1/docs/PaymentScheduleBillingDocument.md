# PaymentScheduleBillingDocument

Object of the billing document with which the payment schedule is associated.  **Note:** - This field is optional. If you have the Standalone Payment feature enabled, you can leave this field blank and set `standalone` to `true` to create standalone payments. You can also choose to create unapplied payments by leaving this object blank and setting `standalone` to `false`. - If Standalone Payment is not enabled, leaving this object unspecified will create unapplied payments. - Object for the billing document with which the payment schedule item is associated. - Note: You must specify the same billing document for all the payment schedule items in one payment schedule. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the billing document.  **Note:**  If a billing document is specified, either &#x60;id&#x60; or &#x60;number&#x60; of the billing document must be specified. You cannot specify both of them or skip both.  | [optional] 
**number** | **str** | ID of the billing document.  **Note:**  If a billing document is specified, either &#x60;id&#x60; or &#x60;number&#x60; of the billing document must be specified. You cannot specify both of them or skip both.  | [optional] 
**type** | [**PostPaymentScheduleRequestAllOfBillingDocumentType**](PostPaymentScheduleRequestAllOfBillingDocumentType.md) |  | 

## Example

```python
from zuora_sdk.models.payment_schedule_billing_document import PaymentScheduleBillingDocument

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentScheduleBillingDocument from a JSON string
payment_schedule_billing_document_instance = PaymentScheduleBillingDocument.from_json(json)
# print the JSON string representation of the object
print(PaymentScheduleBillingDocument.to_json())

# convert the object into a dict
payment_schedule_billing_document_dict = payment_schedule_billing_document_instance.to_dict()
# create an instance of PaymentScheduleBillingDocument from a dict
payment_schedule_billing_document_from_dict = PaymentScheduleBillingDocument.from_dict(payment_schedule_billing_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


