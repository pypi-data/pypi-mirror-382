# CreatePaymentScheduleItemsRequestItems


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount that needs to be collected by this payment schedule item.  | 
**currency** | **str** | The currency of the payment.   **Note**:  - This field is optional. If not specified, the default value is the currency set for the account. | [optional] 
**description** | **str** | Description of the payment schedule item.  | [optional] 
**payment_gateway_id** | **str** | The ID of the payment gateway.   **Note**:  - This field is optional. If not specified, the default value is the payment gateway id set for the account. | [optional] 
**payment_method_id** | **str** | The ID of the payment method.   **Note**:  - This field is optional. If not specified, the default value is the payment method id set for the account. | [optional] 
**payment_option** | [**List[PaymentSchedulePaymentOptionFields]**](PaymentSchedulePaymentOptionFields.md) | Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.   Here is an example:  &#x60;&#x60;&#x60;  \&quot;paymentOption\&quot;: [   {     \&quot;type\&quot;: \&quot;GatewayOptions\&quot;,     \&quot;detail\&quot;: {       \&quot;SecCode\&quot;:\&quot;WEB\&quot;     }   } ]  &#x60;&#x60;&#x60;   &#x60;paymentOption&#x60; of the payment schedule takes precedence over &#x60;paymentOption&#x60; of the payment schedule item.   To enable this field, submit a request at [Zuora Global Support](https://support.zuora.com/). This field is only available if &#x60;zuora-version&#x60; is set to &#x60;337.0&#x60; or later. | [optional] 
**run_hour** | **int** | At which hour of the day in the tenant’s timezone this payment will be collected. Available values:&#x60;[0,1,2,~,22,23]&#x60;.  If the payment &#x60;runHour&#x60; and &#x60;scheduledDate&#x60; are backdated, the system will collect the payment when the next runHour occurs.  The default value is &#x60;0&#x60;. | [optional] 
**scheduled_date** | **date** | The date to collect the payment.  | 

## Example

```python
from zuora_sdk.models.create_payment_schedule_items_request_items import CreatePaymentScheduleItemsRequestItems

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentScheduleItemsRequestItems from a JSON string
create_payment_schedule_items_request_items_instance = CreatePaymentScheduleItemsRequestItems.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentScheduleItemsRequestItems.to_json())

# convert the object into a dict
create_payment_schedule_items_request_items_dict = create_payment_schedule_items_request_items_instance.to_dict()
# create an instance of CreatePaymentScheduleItemsRequestItems from a dict
create_payment_schedule_items_request_items_from_dict = CreatePaymentScheduleItemsRequestItems.from_dict(create_payment_schedule_items_request_items_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


