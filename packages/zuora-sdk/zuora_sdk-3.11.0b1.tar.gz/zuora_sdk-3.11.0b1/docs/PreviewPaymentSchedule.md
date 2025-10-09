# PreviewPaymentSchedule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | Indicates the updated amount of the pending payment schedule items.  | [optional] 
**currency** | **str** | Indicates the updated currency of the pending payment schedule items. | [optional] 
**occurrences** | **int** | Indicates the updated number of payment schedule items that are created by the payment schedule. | [optional] 
**payment_gateway_id** | **str** | Indicates the updated payment gateway ID of the pending payment schedule items. | [optional] 
**payment_method_id** | **str** | Indicates the updated payment method ID of the pending payment schedule items. | [optional] 
**payment_option** | [**List[PaymentSchedulePaymentOptionFields]**](PaymentSchedulePaymentOptionFields.md) | Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.   Here is an example:  &#x60;&#x60;&#x60;  \&quot;paymentOption\&quot;: [   {     \&quot;type\&quot;: \&quot;GatewayOptions\&quot;,     \&quot;detail\&quot;: {       \&quot;SecCode\&quot;:\&quot;WEB\&quot;     }   } ]  &#x60;&#x60;&#x60;   &#x60;paymentOption&#x60; of the payment schedule takes precedence over &#x60;paymentOption&#x60; of the payment schedule item.   To enable this field, submit a request at [Zuora Global Support](https://support.zuora.com/). This field is only available if &#x60;zuora-version&#x60; is set to &#x60;337.0&#x60; or later. | [optional] 
**period** | **str** | Indicates the updated period of the pending payment schedule items.  | [optional] 
**period_start_date** | **date** | Indicates the updated collection date for the next pending payment schedule item. | [optional] 
**run_hour** | **int** | Specifies at which hour of the day in the tenant’s time zone this payment will be collected. Available values: &#x60;[0,1,2,~,22,23]&#x60;.    If the time difference between your tenant’s timezone and the timezone where Zuora servers are is not in full hours, for example, 2.5 hours, the payment schedule items will be triggered half hour later than your scheduled time. If the payment &#x60;runHour&#x60; and &#x60;scheduledDate&#x60; are backdated, the system will collect the payment when the next runHour occurs. | [optional] 

## Example

```python
from zuora_sdk.models.preview_payment_schedule import PreviewPaymentSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewPaymentSchedule from a JSON string
preview_payment_schedule_instance = PreviewPaymentSchedule.from_json(json)
# print the JSON string representation of the object
print(PreviewPaymentSchedule.to_json())

# convert the object into a dict
preview_payment_schedule_dict = preview_payment_schedule_instance.to_dict()
# create an instance of PreviewPaymentSchedule from a dict
preview_payment_schedule_from_dict = PreviewPaymentSchedule.from_dict(preview_payment_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


