# BillCycleType

Specifies how Zuora determines the day that each billing period begins on.    * `DefaultFromCustomer` - Each billing period begins on the bill cycle day of the account that owns the subscription.   * `SpecificDayofMonth` - Use the `billCycleDay` field to specify the day of the month that each billing period begins on.   * `SubscriptionStartDay` - Each billing period begins on the same day of the month as the start date of the subscription.   * `ChargeTriggerDay` - Each billing period begins on the same day of the month as the date when the charge becomes active.   * `SpecificDayofWeek` - Use the `weeklyBillCycleDay` field to specify the day of the week that each billing period begins on.   - If you set this field to `SpecificDayofMonth`, you must also specify the `billCycleDay` field.  - If you set this field to to `SpecificDayofWeek`, you must also specify the `weeklyBillCycleDay` field. 

## Enum

* `DEFAULTFROMCUSTOMER` (value: `'DefaultFromCustomer'`)

* `SPECIFICDAYOFMONTH` (value: `'SpecificDayofMonth'`)

* `SUBSCRIPTIONSTARTDAY` (value: `'SubscriptionStartDay'`)

* `CHARGETRIGGERDAY` (value: `'ChargeTriggerDay'`)

* `SPECIFICDAYOFWEEK` (value: `'SpecificDayofWeek'`)

* `TERMSTARTDAY` (value: `'TermStartDay'`)

* `TERMENDDAY` (value: `'TermEndDay'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


