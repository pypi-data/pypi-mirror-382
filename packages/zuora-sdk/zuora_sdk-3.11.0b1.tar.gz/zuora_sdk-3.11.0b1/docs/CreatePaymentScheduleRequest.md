# CreatePaymentScheduleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | ID of the customer account the payment schedule belongs to.   **Note:**  &#x60;accountId&#x60; and &#x60;accountNumber&#x60; cannot both be &#x60;null&#x60;. When both fields are specified, the two values must match each other. | [optional] 
**account_number** | **str** | Account number of the customer account the payment schedule belongs to.   **Note:**  &#x60;accountId&#x60; and &#x60;accountNumber&#x60; cannot both be &#x60;null&#x60;. When both fields are specified, the two values must match each other. | [optional] 
**amount** | **float** | The amount of each payment schedule item in the payment schedule.   **Note:**  - This field is required when &#x60;items&#x60; is not specified.  - This field will be ignored when &#x60;items&#x60; is specified.  - When creating recurring payment schedules, there are 2 options to specify amounts:     - Specify &#x60;totalAmount&#x60; and &#x60;occurrences&#x60;, &#x60;amount&#x60; will be calculated.   - Specify &#x60;amount&#x60; and &#x60;occurrences&#x60;, &#x60;totalAmount&#x60; will be calculated.   You must specify either &#x60;totalAmount&#x60; or &#x60;amount&#x60;. Specifying both fields at the same time is not allowed. | [optional] 
**billing_document** | [**PaymentScheduleBillingDocument**](PaymentScheduleBillingDocument.md) |  | [optional] 
**currency** | **str** | Currency of the payment schedule.   **Note:**  - This field is optional. The default value is the account&#39;s default currency.  - This field will be ignored when &#x60;items&#x60; is specified. | [optional] 
**description** | **str** | Description of the payment schedule. Max length is 255.  | [optional] 
**items** | [**List[CreatePaymentScheduleRequestItems]**](CreatePaymentScheduleRequestItems.md) | Container array for payment schedule items.  | [optional] 
**occurrences** | **int** | The number of payment schedule item to be created. Maximum value is 1000.   **Note:**  - This field is required when &#x60;items&#x60; is not specified.  - This field will be ignored when &#x60;items&#x60; is specified. | [optional] 
**payment_gateway_id** | **str** | ID of the payment gateway.   **Note:**  - This field is optional. The default value is the account&#39;s default payment gateway ID. If no payment gateway ID is found on the cusotmer account level, the default value will be the tenant&#39;s default payment gateway ID.  - This field will be ignored when &#x60;items&#x60; is specified. | [optional] 
**payment_method_id** | **str** | ID of the payment method.   **Note:**  - This field is optional. The default value is the account&#39;s default payment method ID.  - This field will be ignored when &#x60;items&#x60; is specified. | [optional] 
**payment_option** | [**List[PaymentSchedulePaymentOptionFields]**](PaymentSchedulePaymentOptionFields.md) | Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.    Here is an example:  &#x60;&#x60;&#x60;  \&quot;paymentOption\&quot;: [   {     \&quot;type\&quot;: \&quot;GatewayOptions\&quot;,     \&quot;detail\&quot;: {       \&quot;SecCode\&quot;:\&quot;WEB\&quot;     }   } ]  &#x60;&#x60;&#x60;   &#x60;paymentOption&#x60; of the payment schedule takes precedence over &#x60;paymentOption&#x60; of the payment schedule item.   To enable this field, submit a request at [Zuora Global Support](https://support.zuora.com/). This field is only available if &#x60;zuora-version&#x60; is set to &#x60;337.0&#x60; or later. | [optional] 
**payment_schedule_number** | **str** | You can use this field to specify the number of the payment schedule.  Only characters from the following sets are allowed: A-Z, a-z, 0-9, and &#x60;-&#x60;.   Payment numbers must start with a letter. In addition,&#x60;-&#x60; can only be used at most once and cannot be placed at the beginning or the end of the payment numbers. | [optional] 
**period** | **str** | The frequency for the payment collection since the &#x60;startDate&#x60;.   **Note:**  - Thie field is required when &#x60;items&#x60; is not specified.  - This field will be ignored when &#x60;items&#x60; is specified.  - If &#x60;startDate&#x60; is &#x60;30&#x60; or &#x60;31&#x60; and &#x60;period&#x60; is &#x60;Monthly&#x60;, when in February, payment schedule will use the last day of February for payment collection. | [optional] 
**prepayment** | **bool** | Indicates whether the payments created by the payment schedule will be used as reserved payments. This field will only be available if the prepaid cash drawdown permission is enabled. See [Prepaid Cash with Drawdown](https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Invoicing/JA_Advanced_Consumption_Billing/Prepaid_Cash_with_Drawdown) for more information. | [optional] 
**run_hour** | **int** | Specifies at which hour in the day in the tenant’s time zone when this payment will be collected. Available values: &#x60;[0,1,2,~,22,23]&#x60;.   **Note:**  - If the time difference between your tenant’s timezone and the timezone where Zuora servers are is not in full hours, for example, 2.5 hours, the payment schedule items will be triggered half hour later than your scheduled time.  - If the payment &#x60;runHour&#x60; and &#x60;scheduledDate&#x60; are backdated, the system will collect the payment when the next runHour occurs.  - This field is optional. The default value is &#x60;0&#x60;.  - This field will be ignored when &#x60;items&#x60; is specified. | [optional] 
**standalone** | **bool** | Indicate whether the payments created by the payment schedule are standalone payments or not. When setting to &#x60;true&#x60;, standalone payments will be created. When setting to &#x60;false&#x60;, you can either specify a billing document, or not specifying any billing documents. In the later case, unapplied payments will be created. If set to &#x60;null&#x60;, standalone payment will be created.   **Note**:   - This field is only available if the Standalone Payment is enabled. Do not include this field if Standalone Payment is not enabled.  - If Standalone Payment is enabled, default value is &#x60;true&#x60;. | [optional] 
**start_date** | **date** | The date for the first payment collection.  **Note:** - This field is required when &#x60;items&#x60; is not specified. - This field will be ignored when &#x60;items&#x60; is specified.  | [optional] 
**total_amount** | **float** | The total amount of that the payment schedule will collect. This field is only available for recurring payment schedules.    **Note**:  - When creating recurring payment schedules, there are 2 options to specify amounts:      - Specify &#x60;totalAmount&#x60; and &#x60;occurrences&#x60;, &#x60;amount&#x60; will be calculated.   - Specify &#x60;amount&#x60; and &#x60;occurrences&#x60;, &#x60;totalAmount&#x60; will be calculated.      You must specify either &#x60;totalAmount&#x60; or &#x60;amount&#x60;. Specifying both fields at the same time is not allowed. - If the Standalone Payments feature is enabled and &#x60;standalone&#x60; is set to &#x60;true&#x60; for the payment schedule, &#x60;totalAmount&#x60; will be ignored. | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_schedule_request import CreatePaymentScheduleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentScheduleRequest from a JSON string
create_payment_schedule_request_instance = CreatePaymentScheduleRequest.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentScheduleRequest.to_json())

# convert the object into a dict
create_payment_schedule_request_dict = create_payment_schedule_request_instance.to_dict()
# create an instance of CreatePaymentScheduleRequest from a dict
create_payment_schedule_request_from_dict = CreatePaymentScheduleRequest.from_dict(create_payment_schedule_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


