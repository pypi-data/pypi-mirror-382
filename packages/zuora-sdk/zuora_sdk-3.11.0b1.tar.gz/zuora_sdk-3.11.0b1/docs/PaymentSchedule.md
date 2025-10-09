# PaymentSchedule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | ID of the account that owns the payment schedule.  | [optional] 
**account_number** | **str** | Number of the account that owns the payment schedule.  | [optional] 
**billing_document** | [**PaymentScheduleBillingDocument**](PaymentScheduleBillingDocument.md) |  | [optional] 
**cancel_date** | **str** | The date when the payment schedule item was cancelled.  | [optional] 
**cancelled_by_id** | **str** | The ID of the user who cancel the payment schedule item.  | [optional] 
**cancelled_on** | **str** | The date and time when the payment schedule item was cancelled.  | [optional] 
**created_by_id** | **str** | The ID of the user who created this payment schedule.  | [optional] 
**created_date** | **str** | The date and time the payment schedule is created.  | [optional] 
**description** | **str** | The description of the payment schedule.  | [optional] 
**id** | **str** | ID of the payment schedule.  | [optional] 
**is_custom** | **bool** | Indicates if the payment schedule is a custom payment schedule.  | [optional] 
**items** | [**List[PaymentScheduleItem]**](PaymentScheduleItem.md) | Container for payment schedule items.  | [optional] 
**next_payment_date** | **str** | The date the next payment will be processed.  | [optional] 
**occurrences** | **int** | The number of payment schedule items that are created by this payment schedule. | [optional] 
**payment_option** | [**List[PaymentSchedulePaymentOptionFields]**](PaymentSchedulePaymentOptionFields.md) | Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.   &#x60;paymentOption&#x60; of the payment schedule takes precedence over &#x60;paymentOption&#x60; of the payment schedule item.   This field is only available if &#x60;zuora-version&#x60; is set to &#x60;337.0&#x60; or later. | [optional] 
**payment_schedule_number** | **str** | Number of the payment schedule.  | [optional] 
**period** | **str** | For recurring payment schedule only. The period of payment generation. Available values include: &#x60;Monthly&#x60;, &#x60;Weekly&#x60;, &#x60;BiWeekly&#x60;.   Return &#x60;null&#x60; for custom payment schedules. | [optional] 
**prepayment** | **bool** | Indicates whether the payments created by the payment schedule are used as a reserved payment. This field is available only if the prepaid cash drawdown permission is enabled. See [Prepaid Cash with Drawdown](https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Invoicing/JA_Advanced_Consumption_Billing/Prepaid_Cash_with_Drawdown) for more information. | [optional] 
**recent_payment_date** | **date** | The date the last payment was processed.  | [optional] 
**run_hour** | **int** | [0,1,2,~,22,23]   At which hour in the day in the tenant’s timezone this payment will be collected.   Return &#x60;0&#x60; for custom payment schedules. | [optional] 
**standalone** | **bool** | Indicates if the payments that the payment schedule created are standalone payments. | [optional] 
**start_date** | **str** | The date when the first payment of this payment schedule is proccessed. | [optional] 
**status** | **str** | The status of the payment schedule.   - Active: There is still payment schedule item to process.  - Canceled: After a payment schedule is canceled by the user, the schedule is marked as &#x60;Canceled&#x60;.  - Completed: After all payment schedule items are processed, the schedule is marked as &#x60;Completed&#x60;. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**total_amount** | **float** | The total amount that will be collected by the payment schedule.  | [optional] 
**total_payments_errored** | **int** | The number of errored payments.  | [optional] 
**total_payments_processed** | **int** | The number of processed payments.  | [optional] 
**updated_by_id** | **str** | The ID of the user who last updated this payment schedule.  | [optional] 
**updated_date** | **str** | The date and time the payment schedule is last updated.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_schedule import PaymentSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentSchedule from a JSON string
payment_schedule_instance = PaymentSchedule.from_json(json)
# print the JSON string representation of the object
print(PaymentSchedule.to_json())

# convert the object into a dict
payment_schedule_dict = payment_schedule_instance.to_dict()
# create an instance of PaymentSchedule from a dict
payment_schedule_from_dict = PaymentSchedule.from_dict(payment_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


