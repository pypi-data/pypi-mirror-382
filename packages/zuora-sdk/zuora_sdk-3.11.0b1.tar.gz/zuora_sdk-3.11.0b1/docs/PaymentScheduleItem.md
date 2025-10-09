# PaymentScheduleItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | ID of the customer account that owns the payment schedule item, for example &#x60;402880e741112b310149b7343ef81234&#x60;. | [optional] 
**amount** | **decimal.Decimal** | The total amount of the payment schedule.  | [optional] 
**balance** | **decimal.Decimal** | The remaining balance of payment schedule item.  | [optional] 
**billing_document** | [**PaymentScheduleBillingDocument**](PaymentScheduleBillingDocument.md) |  | [optional] 
**cancellation_reason** | **str** | The reason for the cancellation of payment schedule item.  | [optional] 
**cancelled_by_id** | **str** | The ID of the user who cancel the payment schedule item.  | [optional] 
**cancelled_on** | **str** | The date and time when the payment schedule item was cancelled.  | [optional] 
**created_by_id** | **str** | The ID of the user who created the payment schedule item.  | [optional] 
**created_date** | **str** | The date and time when the payment schedule item was created.  | [optional] 
**currency** | **str** | The currency of the payment.  | [optional] 
**description** | **str** | The description of the payment schedule item.  | [optional] 
**error_message** | **str** | The error message indicating if the error is related to the configuration or the payment collection. | [optional] 
**id** | **str** | ID of the payment schedule item. For example, &#x60;412880e749b72b310149b7343ef81346&#x60;. | [optional] 
**number** | **str** | Number of the payment schedule item.  | [optional] 
**payment_gateway_id** | **str** | ID of the payment gateway of the payment schedule item.  | [optional] 
**payment_id** | **str** | ID of the payment that is created by the payment schedule item, or linked to the payment schedule item. This field is only available if the request doesn’t specify &#x60;zuora-version&#x60;, or &#x60;zuora-version&#x60; is set to a value equal to or smaller than &#x60;336.0&#x60;.   | [optional] 
**payment_method_id** | **str** | ID of the payment method of the payment schedule item.  | [optional] 
**payment_option** | [**List[PaymentSchedulePaymentOptionFields]**](PaymentSchedulePaymentOptionFields.md) | Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.   &#x60;paymentOption&#x60; of the payment schedule takes precedence over &#x60;paymentOption&#x60; of the payment schedule item.   This field is only available if &#x60;zuora-version&#x60; is set to &#x60;337.0&#x60; or later. | [optional] 
**payment_schedule_id** | **str** | ID of the payment schedule that contains the payment schedule item, for example, &#x60;ID402880e749b72b310149b7343ef80005&#x60;. | [optional] 
**payment_schedule_number** | **str** | Number of the payment schedule that contains the payment schedule item, for example, &#x60;ID402880e749b72b310149b7343ef80005&#x60;. | [optional] 
**psi_payments** | [**List[PaymentScheduleLinkedPaymentID]**](PaymentScheduleLinkedPaymentID.md) | Container for payments linked to the payment schedule item.  | [optional] 
**run_hour** | **int** | At which hour in the day in the tenant’s timezone this payment will be collected. If the payment &#x60;runHour&#x60; and &#x60;scheduledDate&#x60; are backdated, the system will collect the payment when the next runHour occurs. | [optional] 
**scheduled_date** | **str** | The scheduled date when the payment is processed.  | [optional] 
**standalone** | **bool** | Indicates if the payment created by the payment schedule item is a standalone payment or not. | [optional] 
**status** | **str** | ID of the payment method of the payment schedule item.   - &#x60;Pending&#x60;: Payment schedule item is waiting for processing.  - &#x60;Processed&#x60;: The payment has been collected.  - &#x60;Error&#x60;: Failed to collect the payment.  - &#x60;Canceled&#x60;: After a pending payment schedule item is canceled by the user, the item is marked as &#x60;Canceled&#x60;. | [optional] 
**updated_by_id** | **str** | The ID of the user who updated the payment schedule item.  | [optional] 
**updated_date** | **str** | The date and time when the payment schedule item was last updated.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_schedule_item import PaymentScheduleItem

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentScheduleItem from a JSON string
payment_schedule_item_instance = PaymentScheduleItem.from_json(json)
# print the JSON string representation of the object
print(PaymentScheduleItem.to_json())

# convert the object into a dict
payment_schedule_item_dict = payment_schedule_item_instance.to_dict()
# create an instance of PaymentScheduleItem from a dict
payment_schedule_item_from_dict = PaymentScheduleItem.from_dict(payment_schedule_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


