# CreditMemoItemFromInvoiceItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the credit memo item. | 
**comment** | **str** | Comments about the credit memo item. **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**description** | **str** | The description of the credit memo item. **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**finance_information** | [**CreditMemoItemFromInvoiceItemFinanceInformation**](CreditMemoItemFromInvoiceItemFinanceInformation.md) |  | [optional] 
**invoice_item_id** | **str** | The ID of the invoice item. | 
**quantity** | **float** | The number of units for the credit memo item. | [optional] 
**service_end_date** | **date** | The service end date of the credit memo item. | [optional] 
**service_start_date** | **date** | The service start date of the credit memo item. | [optional] 
**sku_name** | **str** | The name of the charge associated with the invoice. | 
**tax_items** | [**List[CreditMemoTaxItemFromInvoiceTaxItemRequest]**](CreditMemoTaxItemFromInvoiceTaxItemRequest.md) | Container for taxation items. | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**unit_of_measure** | **str** | The definable unit that you measure when determining charges. | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the credit memo item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_item_from_invoice_item import CreditMemoItemFromInvoiceItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoItemFromInvoiceItem from a JSON string
credit_memo_item_from_invoice_item_instance = CreditMemoItemFromInvoiceItem.from_json(json)
# print the JSON string representation of the object
print(CreditMemoItemFromInvoiceItem.to_json())

# convert the object into a dict
credit_memo_item_from_invoice_item_dict = credit_memo_item_from_invoice_item_instance.to_dict()
# create an instance of CreditMemoItemFromInvoiceItem from a dict
credit_memo_item_from_invoice_item_from_dict = CreditMemoItemFromInvoiceItem.from_dict(credit_memo_item_from_invoice_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


