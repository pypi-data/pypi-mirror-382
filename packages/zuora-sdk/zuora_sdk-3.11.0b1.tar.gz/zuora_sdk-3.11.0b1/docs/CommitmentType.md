# CommitmentType

**Note**: This field is only available if you have the [Unbilled Usage](https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_for_usage_or_prepaid_products/Advanced_Consumption_Billing/Unbilled_Usage) feature enabled.     The type of commitment. A prepaid charge can be UNIT or CURRENCY. And a min commitment(in-arrears) charge can only be CURRENCY type. For topup(recurring/one-time) charges, this field indicates what type of funds are created.  * If UNIT it will create a fund with given prepaidUom. * If CURRENCY it will create a fund with the currency amount calculated in list price. For drawdown(usage) charges, this field indicates what type of funds are drawdown from that created from topup charges.

## Enum

* `UNIT` (value: `'UNIT'`)

* `CURRENCY` (value: `'CURRENCY'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


