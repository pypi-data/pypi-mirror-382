# BillingPeriodAlignment

Specifies how Zuora determines when to start new billing periods. You can use this field to align the billing periods of different charges.  * `AlignToCharge` - Zuora starts a new billing period on the first billing day that falls on or after the date when the charge becomes active. * `AlignToSubscriptionStart` - Zuora starts a new billing period on the first billing day that falls on or after the start date of the subscription. * `AlignToTermStart` - For each term of the subscription, Zuora starts a new billing period on the first billing day that falls on or after the start date of the term.  See the `billCycleType` field for information about how Zuora determines the billing day. **Note:** `AlignToTermEnd` is only available for prepayment charges by default. To enable this value for non-prepaid recurring charges, contact <a href=\"http://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a>. 

## Enum

* `ALIGNTOCHARGE` (value: `'AlignToCharge'`)

* `ALIGNTOSUBSCRIPTIONSTART` (value: `'AlignToSubscriptionStart'`)

* `ALIGNTOTERMSTART` (value: `'AlignToTermStart'`)

* `ALIGNTOTERMEND` (value: `'AlignToTermEnd'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


