# UpdateInvoiceResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the invoice&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the invoice was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**account_id** | **str** | The ID of the customer account associated with the invoice. | [optional] 
**amount** | **float** | The total amount of the invoice. | [optional] 
**auto_pay** | **bool** | Whether invoices are automatically picked up for processing in the corresponding payment run.   | [optional] 
**balance** | **float** | The balance of the invoice. | [optional] 
**cancelled_by_id** | **str** | The ID of the Zuora user who cancelled the invoice. | [optional] 
**cancelled_on** | **str** | The date and time when the invoice was cancelled, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**comment** | **str** | Comments about the invoice. | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the invoice. | [optional] 
**created_date** | **str** | The date and time when the invoice was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**credit_balance_adjustment_amount** | **float** | **Note:** This filed is only available if you have the Credit Balance feature enabled and the Invoice Settlement feature disabled. The currency amount of the adjustment applied to the customer&#39;s credit balance. | [optional] 
**currency** | **str** | A currency defined in the web-based UI administrative settings. | [optional] 
**discount** | **float** | The discount of the invoice. | [optional] 
**due_date** | **date** | The date by which the payment for this invoice is due.   | [optional] 
**id** | **str** | The unique ID of the invoice. | [optional] 
**invoice_date** | **date** | The date on which to generate the invoice. | [optional] 
**number** | **str** | The unique identification number of the invoice. | [optional] 
**posted_by_id** | **str** | The ID of the Zuora user who posted the invoice. | [optional] 
**posted_on** | **str** | The date and time when the invoice was posted, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format.   | [optional] 
**status** | [**BillingDocumentStatus**](BillingDocumentStatus.md) |  | [optional] 
**target_date** | **date** | The target date for the invoice, in &#x60;yyyy-mm-dd&#x60; format. For example, 2017-07-20.   | [optional] 
**tax_amount** | **float** | The amount of taxation. | [optional] 
**template_id** | **str** | The ID of the invoice template. | [optional] 
**total_tax_exempt_amount** | **float** | The calculated tax amount excluded due to the exemption. | [optional] 
**transferred_to_accounting** | [**TransferredToAccountingStatus**](TransferredToAccountingStatus.md) |  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the invoice. | [optional] 
**updated_date** | **str** | The date and time when the invoice was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 

## Example

```python
from zuora_sdk.models.update_invoice_response import UpdateInvoiceResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateInvoiceResponse from a JSON string
update_invoice_response_instance = UpdateInvoiceResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateInvoiceResponse.to_json())

# convert the object into a dict
update_invoice_response_dict = update_invoice_response_instance.to_dict()
# create an instance of UpdateInvoiceResponse from a dict
update_invoice_response_from_dict = UpdateInvoiceResponse.from_dict(update_invoice_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


