# CreditMemoItemFromWriteOffInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** | Comments about the credit memo item.  | [optional] 
**finance_information** | [**CreditMemoItemFromInvoiceItemFinanceInformation**](CreditMemoItemFromInvoiceItemFinanceInformation.md) |  | [optional] 
**invoice_item_id** | **str** | The ID of the invoice item.  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**service_end_date** | **date** | The service end date of the credit memo item.   | [optional] 
**service_start_date** | **date** | The service start date of the credit memo item.   | [optional] 
**sku_name** | **str** | The name of the charge associated with the invoice.  | [optional] 
**unit_of_measure** | **str** | The definable unit that you measure when determining charges.  | [optional] 
**taxation_items** | [**List[CreditMemoTaxationItemFromWriteOffInvoice]**](CreditMemoTaxationItemFromWriteOffInvoice.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_item_from_write_off_invoice import CreditMemoItemFromWriteOffInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoItemFromWriteOffInvoice from a JSON string
credit_memo_item_from_write_off_invoice_instance = CreditMemoItemFromWriteOffInvoice.from_json(json)
# print the JSON string representation of the object
print(CreditMemoItemFromWriteOffInvoice.to_json())

# convert the object into a dict
credit_memo_item_from_write_off_invoice_dict = credit_memo_item_from_write_off_invoice_instance.to_dict()
# create an instance of CreditMemoItemFromWriteOffInvoice from a dict
credit_memo_item_from_write_off_invoice_from_dict = CreditMemoItemFromWriteOffInvoice.from_dict(credit_memo_item_from_write_off_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


