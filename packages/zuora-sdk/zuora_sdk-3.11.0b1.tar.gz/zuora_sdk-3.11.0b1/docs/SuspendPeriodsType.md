# SuspendPeriodsType

This field is applicable only when the `suspendPolicy` field is set to `FixedPeriodsFromToday`. It must be used together with the `suspendPeriods` field.  The period type used to specify when a subscription suspension takes effect. The subscription suspension will take place after the specified time frame (`suspendPeriods` multiplied by `suspendPeriodsType`) from today's date.  

## Enum

* `DAY` (value: `'Day'`)

* `WEEK` (value: `'Week'`)

* `MONTH` (value: `'Month'`)

* `YEAR` (value: `'Year'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


