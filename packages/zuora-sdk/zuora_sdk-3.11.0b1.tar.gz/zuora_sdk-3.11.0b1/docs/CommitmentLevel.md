# CommitmentLevel

**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  Valid for the Charge with Function of `Prepayment` or `CommitmentTrueUp`. The level in which the funds are applicable for the usage drawdown charges during drawdown. * `RATEPLAN` - only usage charges of same rate plan can be drawn down. * `SUBSCRIPTION` - only usage charges of same subscription can be drawn down. * `ACCOUNT` - any usage charges in the same account (subscription owner) can be drawn down. 

## Enum

* `RATEPLAN` (value: `'RATEPLAN'`)

* `SUBSCRIPTION` (value: `'SUBSCRIPTION'`)

* `ACCOUNT` (value: `'ACCOUNT'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


