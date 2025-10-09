# EndDateConditionProductRatePlanChargeRest

Defines when the charge ends after the charge trigger date.  **Values**:    - `SubscriptionEnd`: The charge ends on the subscription end date after a specified period based on the trigger date of the charge.    - `FixedPeriod`: The charge ends after a specified period based on the trigger date of the charge. If you set this field to `FixedPeriod`, you must specify the length of the period and a period type by defining the `UpToPeriods` and `UpToPeriodsType` fields.     **Note**: If the subscription ends before the charge end date, the charge ends when the subscription ends. But if the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge will end on the charge end date. 

## Enum

* `SUBSCRIPTIONEND` (value: `'SubscriptionEnd'`)

* `FIXEDPERIOD` (value: `'FixedPeriod'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


