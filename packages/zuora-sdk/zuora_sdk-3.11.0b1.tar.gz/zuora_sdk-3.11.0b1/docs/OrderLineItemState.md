# OrderLineItemState

The state of the Order Line Item (OLI). See [State transitions for an order, order line item, and fulfillment](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items/AB_Order_Line_Item_States_and_Order_States) for more information.  To generate invoice for an OLI, you must set this field to `SentToBilling` and set the `billTargetDate` field .  You can update this field for a sales or return OLI only when the OLI is in the `Executing` or 'Booked' or `SentToBilling`state (when the `itemState` field is set as `Executing` or `SentToBilling`). 

## Enum

* `EXECUTING` (value: `'Executing'`)

* `BOOKED` (value: `'Booked'`)

* `SENTTOBILLING` (value: `'SentToBilling'`)

* `COMPLETE` (value: `'Complete'`)

* `CANCELED` (value: `'Canceled'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


