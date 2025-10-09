# EndDateCondition

Condition for the charge to become inactive.  If the value of this field is `Fixed_Period`, the charge is active for a predefined duration based on the value of the `upToPeriodsType` and `upToPeriods` fields.  If the value of this field is `Specific_End_Date`, use the `specificEndDate` field to specify the date when then charge becomes inactive. 

## Enum

* `SUBSCRIPTION_END` (value: `'Subscription_End'`)

* `FIXED_PERIOD` (value: `'Fixed_Period'`)

* `SPECIFIC_END_DATE` (value: `'Specific_End_Date'`)

* `ONE_TIME` (value: `'One_Time'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


