# OrderStatus

The status of the order. If the order contains any `Pending Activation` or `Pending Acceptance` subscription, the order status will be `Pending`; If the order is in draft status, the order status will be `Draft`; otherwise the order status is `Completed`.  **Note**: You cannot retrieve the detailed information about draft orders or scheduled orders through the \"List orders of a subscription owner\" and  \"List orders of an invoice owner\" operations.  Draft: The order is in draft status. - `Draft`: The order is in draft status. - `Pending`: The order is in pending status. - `Completed`: The order is in completed status. - `Scheduled`: The order is in scheduled status and it is only valid if the Scheduled Orders feature is enabled. - `Executing`: The scheduled order is executed by a scheduler and it is only valid if the Scheduled Orders feature is enabled. - `Failed`: The scheduled order has failed.  **Note**: The Scheduled Orders feature is in the Early Adopter phase. We are actively soliciting feedback from a small set of early adopters before releasing it as generally available. If you want to join this early adopter program, submit a request at <a href=\"https://support.zuora.com/hc/en-us\" target=\"_blank\">Zuora Global Support</a>. 

## Enum

* `DRAFT` (value: `'Draft'`)

* `PENDING` (value: `'Pending'`)

* `COMPLETED` (value: `'Completed'`)

* `CANCELLED` (value: `'Cancelled'`)

* `SCHEDULED` (value: `'Scheduled'`)

* `EXECUTING` (value: `'Executing'`)

* `FAILED` (value: `'Failed'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


