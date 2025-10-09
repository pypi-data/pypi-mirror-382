# DebitMemoItemFromInvoiceItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the debit memo item. | 
**comment** | **str** | Comments about the debit memo item. **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**description** | **str** | The description of the debit memo item. **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**finance_information** | [**DebitMemoItemFromInvoiceItemFinanceInformation**](DebitMemoItemFromInvoiceItemFinanceInformation.md) |  | [optional] 
**invoice_item_id** | **str** | The ID of the invoice item. | [optional] 
**quantity** | **float** | The number of units for the debit memo item. | [optional] 
**service_end_date** | **date** | The service end date of the debit memo item. | [optional] 
**service_start_date** | **date** | The service start date of the debit memo item.   | [optional] 
**sku_name** | **str** | The name of the charge associated with the invoice. | 
**tax_items** | [**List[DebitMemoTaxItemFromInvoiceTaxItemRequest]**](DebitMemoTaxItemFromInvoiceTaxItemRequest.md) | Container for taxation items. | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**unit_of_measure** | **str** | The definable unit that you measure when determining charges. | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the debit memo item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_item_from_invoice_item_request import DebitMemoItemFromInvoiceItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoItemFromInvoiceItemRequest from a JSON string
debit_memo_item_from_invoice_item_request_instance = DebitMemoItemFromInvoiceItemRequest.from_json(json)
# print the JSON string representation of the object
print(DebitMemoItemFromInvoiceItemRequest.to_json())

# convert the object into a dict
debit_memo_item_from_invoice_item_request_dict = debit_memo_item_from_invoice_item_request_instance.to_dict()
# create an instance of DebitMemoItemFromInvoiceItemRequest from a dict
debit_memo_item_from_invoice_item_request_from_dict = DebitMemoItemFromInvoiceItemRequest.from_dict(debit_memo_item_from_invoice_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


