# CreateBillingPreviewInvoiceItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_to_item_id** | **str** | The unique ID of the invoice item that the discount charge is applied to.  | [optional] 
**charge_amount** | **decimal.Decimal** | The amount of the charge. This amount doesn&#39;t include taxes regardless if the charge&#39;s tax mode is inclusive or exclusive. | [optional] 
**charge_date** | **str** | The date when the invoice item was created.  | [optional] 
**charge_description** | **str** | Description of the charge.  | [optional] 
**charge_id** | **str** | Id of the charge.  | [optional] 
**charge_name** | **str** | Name of the charge.  | [optional] 
**charge_number** | **str** | Number of the charge.  | [optional] 
**charge_type** | **str** | The type of charge.   Possible values are &#x60;OneTime&#x60;, &#x60;Recurring&#x60;, and &#x60;Usage&#x60;.  | [optional] 
**id** | **str** | Invoice item ID.  | [optional] 
**number_of_deliveries** | **decimal.Decimal** | The number of delivery for charge.  **Note**: This field is available only if you have the Delivery Pricing feature enabled.  | [optional] 
**processing_type** | **str** | Identifies the kind of charge.   Possible values: * charge * discount * prepayment * tax  | [optional] 
**product_name** | **str** | Name of the product associated with this item.  | [optional] 
**quantity** | **decimal.Decimal** | Quantity of this item, in the configured unit of measure for the charge.  | [optional] 
**service_end_date** | **date** | End date of the service period for this item, i.e., the last day of the service period, in &#x60;yyyy-mm-dd&#x60; format. | [optional] 
**service_start_date** | **date** | Start date of the service period for this item, in &#x60;yyyy-mm-dd&#x60; format. If the charge is a one-time fee, this is the date of that charge. | [optional] 
**subscription_id** | **str** | ID of the subscription associated with this item.  | [optional] 
**subscription_name** | **str** | Name of the subscription associated with this item.  | [optional] 
**subscription_number** | **str** | Number of the subscription associated with this item.  | [optional] 
**tax_amount** | **decimal.Decimal** | If you use [Zuora Tax](https://knowledgecenter.zuora.com/Billing/Taxes/A_Zuora_Tax) and the product rate plan charge associated with the invoice item is of [tax inclusive mode](https://knowledgecenter.zuora.com/Billing/Taxes/A_Zuora_Tax/D_Associate_tax_codes_with_product_charges_and_set_the_tax_mode), the value of this field is the amount of tax applied to the charge. Otherwise, the value of this field is &#x60;0&#x60;.  | [optional] 
**unit_of_measure** | **str** | Unit used to measure consumption.  | [optional] 

## Example

```python
from zuora_sdk.models.create_billing_preview_invoice_item import CreateBillingPreviewInvoiceItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBillingPreviewInvoiceItem from a JSON string
create_billing_preview_invoice_item_instance = CreateBillingPreviewInvoiceItem.from_json(json)
# print the JSON string representation of the object
print(CreateBillingPreviewInvoiceItem.to_json())

# convert the object into a dict
create_billing_preview_invoice_item_dict = create_billing_preview_invoice_item_instance.to_dict()
# create an instance of CreateBillingPreviewInvoiceItem from a dict
create_billing_preview_invoice_item_from_dict = CreateBillingPreviewInvoiceItem.from_dict(create_billing_preview_invoice_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


