# InvoiceItemPreviewResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**additional_info** | [**InvoiceItemPreviewResultAdditionalInfo**](InvoiceItemPreviewResultAdditionalInfo.md) |  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**applied_to_charge_number** | **str** | Available when the chargeNumber of the charge that discount applies to was specified in the request or when the order is amending an existing subscription. | [optional] 
**charge_description** | **str** |  | [optional] 
**charge_name** | **str** |  | [optional] 
**charge_number** | **str** | Available when the chargeNumber was specified in the request or when the order is amending an existing subscription. | [optional] 
**order_line_item_number** | **str** | A sequential number auto-assigned for each of order line items in a order, used as an index, for example, \&quot;1\&quot;. | [optional] 
**processing_type** | [**InvoiceItemPreviewResultProcessingType**](InvoiceItemPreviewResultProcessingType.md) |  | [optional] 
**product_name** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**service_end_date** | **date** |  | [optional] 
**service_start_date** | **date** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**tax_amount** | **float** |  | [optional] 
**taxation_items** | [**List[InvoiceItemPreviewResultTaxationItems]**](InvoiceItemPreviewResultTaxationItems.md) | List of taxation items.  **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;309.0&#x60; or later.  | [optional] 
**unit_price** | **float** | The per-unit price of the invoice item.  | [optional] 

## Example

```python
from zuora_sdk.models.invoice_item_preview_result import InvoiceItemPreviewResult

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceItemPreviewResult from a JSON string
invoice_item_preview_result_instance = InvoiceItemPreviewResult.from_json(json)
# print the JSON string representation of the object
print(InvoiceItemPreviewResult.to_json())

# convert the object into a dict
invoice_item_preview_result_dict = invoice_item_preview_result_instance.to_dict()
# create an instance of InvoiceItemPreviewResult from a dict
invoice_item_preview_result_from_dict = InvoiceItemPreviewResult.from_dict(invoice_item_preview_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


