# UpdatePaymentScheduleItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **decimal.Decimal** | The amount of the payment.  | [optional] 
**currency** | **str** | The currency of the payment.  | [optional] 
**description** | **str** | The description of the payment schedule item.  | [optional] 
**link_payments** | [**List[PaymentScheduleLinkedPaymentID]**](PaymentScheduleLinkedPaymentID.md) | Container for payments linked to the payment schedule item.  | [optional] 
**payment_gateway_id** | **str** | ID of the payment gateway of the payment schedule item.  | [optional] 
**payment_id** | **str** | ID of the payment to be linked to the payment schedule item.   **Note**: This feild is version controlled. To enable this field, you must set &#x60;zuora-version&#x60; to equal or smaller than &#x60;336.0&#x60;. | [optional] 
**payment_method_id** | **str** | ID of the payment method of the payment schedule item.  | [optional] 
**payment_option** | [**List[PaymentSchedulePaymentOptionFields]**](PaymentSchedulePaymentOptionFields.md) | Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.   Here is an example:  &#x60;&#x60;&#x60;  \&quot;paymentOption\&quot;: [   {     \&quot;type\&quot;: \&quot;GatewayOptions\&quot;,     \&quot;detail\&quot;: {       \&quot;SecCode\&quot;:\&quot;WEB\&quot;     }   } ]  &#x60;&#x60;&#x60;   &#x60;paymentOption&#x60; of the payment schedule takes precedence over &#x60;paymentOption&#x60; of the payment schedule item.   To enable this field, submit a request at [Zuora Global Support](https://support.zuora.com/). This field is only available if &#x60;zuora-version&#x60; is set to &#x60;337.0&#x60; or later. | [optional] 
**run_hour** | **int** | At which hour of the day in the tenant’s timezone this payment will be collected. If the payment &#x60;runHour&#x60; and &#x60;scheduledDate&#x60; are backdated, the system will collect the payment when the next runHour occurs. | [optional] 
**scheduled_date** | **date** | The scheduled date when the payment is processed.  | [optional] 
**unlink_payments** | [**List[PaymentScheduleLinkedPaymentID]**](PaymentScheduleLinkedPaymentID.md) | Container for payments to be unlinked from the payment schedule item.  | [optional] 

## Example

```python
from zuora_sdk.models.update_payment_schedule_item_request import UpdatePaymentScheduleItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdatePaymentScheduleItemRequest from a JSON string
update_payment_schedule_item_request_instance = UpdatePaymentScheduleItemRequest.from_json(json)
# print the JSON string representation of the object
print(UpdatePaymentScheduleItemRequest.to_json())

# convert the object into a dict
update_payment_schedule_item_request_dict = update_payment_schedule_item_request_instance.to_dict()
# create an instance of UpdatePaymentScheduleItemRequest from a dict
update_payment_schedule_item_request_from_dict = UpdatePaymentScheduleItemRequest.from_dict(update_payment_schedule_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


