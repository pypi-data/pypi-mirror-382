# PreviewOptionsPreviewThruType

The options on how the preview through date is calculated. Available for preview only.  - If you set this field to `SpecificDate`, you must specify a specific date in the `specificPreviewThruDate` field. If you also set `billTargetDate` in the `orderLineItems` field, order line items whose `billTargetDate` is no later than `specificPreviewThruDate` are returned.  - If you set this field to `NumberOfPeriods`, you must use the `previewNumberOfPeriods` field to specify how many periods you want to preview. In case the order only contains an order line item but not contains a subscription, if you also set `billTargetDate` in the `orderLineItems` field, order line items whose `billTargetDate` is no later than today are returned.  - The `TermEnd` option is invalid when any subscription included in this order is evergreen. In case the order only contains an order line item but not contains a subscription, if you set this field to `TermEnd` and set `billTargetDate` in the `orderLineItems` field, order line items whose `billTargetDate` is no later than today are returned. 

## Enum

* `SPECIFICDATE` (value: `'SpecificDate'`)

* `TERMEND` (value: `'TermEnd'`)

* `NUMBEROFPERIODS` (value: `'NumberOfPeriods'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


