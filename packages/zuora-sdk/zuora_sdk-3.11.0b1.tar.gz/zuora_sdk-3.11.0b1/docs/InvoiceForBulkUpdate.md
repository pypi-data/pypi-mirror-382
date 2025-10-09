# InvoiceForBulkUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_pay** | **bool** | Whether invoices are automatically picked up for processing in the corresponding payment run. By default, invoices are automatically picked up for processing in the corresponding payment run. | [optional] 
**comments** | **str** | Additional information related to the invoice that a Zuora user added to the invoice. | [optional] 
**due_date** | **date** | The date by which the payment for this invoice is due. | [optional] 
**invoice_date** | **date** | The new invoice date of the invoice. The new invoice date cannot fall in a closed accounting period. You can only specify &#x60;invoiceDate&#x60; or &#x60;dueDate&#x60; in one request. Otherwise, an error occurs. | [optional] 
**invoice_items** | [**List[UpdateInvoiceItem]**](UpdateInvoiceItem.md) | Container for invoice items. The maximum number of items is 1,000. | [optional] 
**template_id** | **str** | The ID of the invoice template. **Note**: This field requires Flexible Billing Attribute. | [optional] 
**transferred_to_accounting** | [**TransferredToAccountingStatus**](TransferredToAccountingStatus.md) |  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the invoice&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the invoice was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**id** | **str** | The ID of the invoice to be updated. | [optional] 

## Example

```python
from zuora_sdk.models.invoice_for_bulk_update import InvoiceForBulkUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceForBulkUpdate from a JSON string
invoice_for_bulk_update_instance = InvoiceForBulkUpdate.from_json(json)
# print the JSON string representation of the object
print(InvoiceForBulkUpdate.to_json())

# convert the object into a dict
invoice_for_bulk_update_dict = invoice_for_bulk_update_instance.to_dict()
# create an instance of InvoiceForBulkUpdate from a dict
invoice_for_bulk_update_from_dict = InvoiceForBulkUpdate.from_dict(invoice_for_bulk_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


