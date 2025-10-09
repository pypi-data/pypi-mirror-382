# StartDatePolicy

Start date policy of the discount charge to become active when the **Apply to billing period partially** checkbox is selected from the product catalog UI or the `applyToBillingPeriodPartially` field is set as true from the \"CRUD: Create a product rate plan charge\" operation. If the value of this field is `SpecificDate`, use the `specificTriggerDate` field to specify the date when the charge becomes active. If the value of this field is `FixedPeriodAfterApplyToChargeStartDate`, the charge is active for a predefined duration based on the value of the `upToPeriodsType` and `upToPeriods` fields. 

## Enum

* `ALIGNTOAPPLYTOCHARGE` (value: `'AlignToApplyToCharge'`)

* `SPECIFICDATE` (value: `'SpecificDate'`)

* `ENDOFLASTINVOICEPERIODOFAPPLYTOCHARGE` (value: `'EndOfLastInvoicePeriodOfApplyToCharge'`)

* `FIXEDPERIODAFTERAPPLYTOCHARGESTARTDATE` (value: `'FixedPeriodAfterApplyToChargeStartDate'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


