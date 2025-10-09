# OrderLineItemInlineDiscountType

This field is used to specify the inline discount type. You can update this field only for a sales OLI and only when the sales OLI is in the `Executing` state (when the `itemState` field is set as `Executing`).  Use this field to specify the inline discount type, which can be `Percentage`, `FixedAmount`, or `None`. The default value is `Percentage`.  Use this field together with the `inlineDiscountPerUnit` field to specify inline discounts for order line items. The inline discount is applied to the list price of an order line item.   Once you set the `inlineDiscountType`, `inlineDiscountPerUnit`, and `listPricePerUnit` fields, the system will automatically generate the `amountPerUnit` field. You shall not set the `amountPerUnit` field by yourself. 

## Enum

* `PERCENTAGE` (value: `'Percentage'`)

* `FIXEDAMOUNT` (value: `'FixedAmount'`)

* `NONE` (value: `'None'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


