# MitTransactionSource

Payment transaction source used to differentiate the transaction source in Stored Credential Transaction framework.   - `C_Unscheduled`: Cardholder-initiated transaction (CIT) that does not occur on scheduled or regularly occurring dates.   - `M_Recurring`: Merchant-initiated transaction (MIT) that occurs at regular intervals.   - `M_Unscheduled`: Merchant-initiated transaction (MIT) that does not occur on scheduled or regularly occurring dates.   - `M_MOTO`: Mail Order Telephone Order (MOTO) payment transaction. This option is only available for credit card payments on Stripe v2. See [Overview of Stripe payment gateway integration](https://knowledgecenter.zuora.com/Zuora_Collect/Payment_gateway_integrations/Supported_payment_gateways/Stripe_Payment_Gateway/A_Overview_of_Stripe_payment_gateway_integration) for more information. 

## Enum

* `C_UNSCHEDULED` (value: `'C_Unscheduled'`)

* `M_RECURRING` (value: `'M_Recurring'`)

* `M_UNSCHEDULED` (value: `'M_Unscheduled'`)

* `M_MOTO` (value: `'M_MOTO'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


