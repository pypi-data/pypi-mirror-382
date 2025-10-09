# CreateInvoiceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the invoice&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the invoice was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**account_id** | **str** | The ID of the account associated with the invoice.   You must specify either &#x60;accountNumber&#x60; or &#x60;accountId&#x60; for a customer account. If both of them are specified, they must refer to the same customer account.  | [optional] 
**account_number** | **str** | The Number of the account associated with the invoice. You must specify either &#x60;accountNumber&#x60; or &#x60;accountId&#x60; for a customer account. If both of them are specified, they must refer to the same customer account. | [optional] 
**auto_pay** | **bool** | Whether invoices are automatically picked up for processing in the corresponding payment run. | [optional] [default to False]
**comments** | **str** | Comments about the invoice. | [optional] 
**custom_rates** | [**List[CustomRates]**](CustomRates.md) | It contains Home currency and Reporting currency custom rates currencies. The maximum number of items is 2 (you can pass the Home currency item or Reporting currency item or both).        **Note**: The API custom rate feature is permission controlled.  | [optional] 
**due_date** | **date** | The date by which the payment for this invoice is due, in &#x60;yyyy-mm-dd&#x60; format.  | [optional] 
**invoice_date** | **date** | The date that appears on the invoice being created, in &#x60;yyyy-mm-dd&#x60; format. The value cannot fall in a closed accounting period. | 
**invoice_items** | [**List[CreateInvoiceItem]**](CreateInvoiceItem.md) | Container for invoice items. The maximum number of invoice items is 1,000. | 
**invoice_number** | **str** | A customized invoice number with the following format requirements: - Max length: 32 characters - Acceptable characters: a-z,A-Z,0-9,-,_,  The value must be unique in the system, otherwise it may cause issues with bill runs and subscribe/amend. Check out [things to note and troubleshooting steps](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/IA_Invoices/Unified_Invoicing/Import_external_invoices_as_standalone_invoices?#Customizing_invoice_number).   | [optional] 
**status** | [**BillingDocumentStatus**](BillingDocumentStatus.md) |  | [optional] 
**bill_to_contact_id** | **str** | The ID of the bill-to contact associated with the invoice. | [optional] 
**payment_term** | **str** | The name of payment term associated with the invoice. | [optional] 
**sequence_set** | **str** | The ID or name of the sequence set associated with the invoice. | [optional] 
**communication_profile_id** | **str** | The ID of the communication profile associated with the invoice. | [optional] 
**sold_to_contact_id** | **str** | The ID of the sold-to contact associated with the invoice. | [optional] 
**bill_to_contact** | [**CreateAccountContact**](CreateAccountContact.md) |  | [optional] 
**sold_to_contact** | [**CreateAccountContact**](CreateAccountContact.md) |  | [optional] 
**sold_to_same_as_bill_to** | **bool** | Whether the sold-to contact and bill-to contact are the same entity.   The created invoice has the same bill-to contact and sold-to contact entity only when all the following conditions are met in the request body:  - This field is set to &#x60;true&#x60;.  - A bill-to contact is specified. - No sold-to contact is specified. | [optional] 
**template_id** | **str** | The ID of the invoice template. **Note**: This field requires Flexible Billing Attribute. | [optional] 
**transferred_to_accounting** | [**TransferredToAccountingStatus**](TransferredToAccountingStatus.md) |  | [optional] 
**ship_to_contact_id** | **str** | The ID of the ship-to contact associated with the invoice. | [optional] 
**ship_to_contact** | [**CreateAccountContact**](CreateAccountContact.md) |  | [optional] 
**ship_to_same_as_bill_to** | **bool** | Whether the ship-to contact and bill-to contact are the same entity.   The created invoice has the same bill-to contact and ship-to contact entity only when all the following conditions are met in the request body:  - This field is set to &#x60;true&#x60;.  - A bill-to contact is specified. - No ship-to contact is specified. | [optional] 

## Example

```python
from zuora_sdk.models.create_invoice_request import CreateInvoiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateInvoiceRequest from a JSON string
create_invoice_request_instance = CreateInvoiceRequest.from_json(json)
# print the JSON string representation of the object
print(CreateInvoiceRequest.to_json())

# convert the object into a dict
create_invoice_request_dict = create_invoice_request_instance.to_dict()
# create an instance of CreateInvoiceRequest from a dict
create_invoice_request_from_dict = CreateInvoiceRequest.from_dict(create_invoice_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


