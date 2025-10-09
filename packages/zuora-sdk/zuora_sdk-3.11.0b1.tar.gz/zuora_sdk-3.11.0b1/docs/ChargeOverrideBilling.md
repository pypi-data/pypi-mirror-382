# ChargeOverrideBilling

Billing information about the charge. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bill_cycle_day** | **int** | Day of the month that each billing period begins on. Only applicable if the value of the &#x60;billCycleType&#x60; field is &#x60;SpecificDayofMonth&#x60;.  | [optional] 
**bill_cycle_type** | [**BillCycleType**](BillCycleType.md) |  | [optional] 
**billing_period** | [**BillingPeriod**](BillingPeriod.md) |  | [optional] 
**billing_period_alignment** | [**BillingPeriodAlignment**](BillingPeriodAlignment.md) |  | [optional] 
**billing_timing** | [**BillingTiming**](BillingTiming.md) |  | [optional] 
**specific_billing_period** | **int** | Duration of each billing period in months or weeks, depending on the value of the &#x60;billingPeriod&#x60; field. Only applicable if the value of the &#x60;billingPeriod&#x60; field is &#x60;Specific_Months&#x60; or &#x60;Specific_Weeks&#x60;.  | [optional] 
**weekly_bill_cycle_day** | [**WeeklyBillCycleDay**](WeeklyBillCycleDay.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.charge_override_billing import ChargeOverrideBilling

# TODO update the JSON string below
json = "{}"
# create an instance of ChargeOverrideBilling from a JSON string
charge_override_billing_instance = ChargeOverrideBilling.from_json(json)
# print the JSON string representation of the object
print(ChargeOverrideBilling.to_json())

# convert the object into a dict
charge_override_billing_dict = charge_override_billing_instance.to_dict()
# create an instance of ChargeOverrideBilling from a dict
charge_override_billing_from_dict = ChargeOverrideBilling.from_dict(charge_override_billing_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


