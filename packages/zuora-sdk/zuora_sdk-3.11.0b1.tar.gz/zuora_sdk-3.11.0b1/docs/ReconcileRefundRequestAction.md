# ReconcileRefundRequestAction

The action of the refund reconciliation.   - `settle`: Sets Gateway State to \"Settled\" and returns the refund object as response.   - `reject`: Sets Gateway State to \"FailedToSettle\" and handle the event according to the settings configured in the Gateway Reconciliation Configuration in Payments Settings through Zuora UI. See [Configure how to handle refund rejected events](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/M_Payment_Gateways/Gateway_Reconciliation#Configure_how_to_handle_refund_rejected_events) for details. 

## Enum

* `SETTLE` (value: `'settle'`)

* `REJECT` (value: `'reject'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


