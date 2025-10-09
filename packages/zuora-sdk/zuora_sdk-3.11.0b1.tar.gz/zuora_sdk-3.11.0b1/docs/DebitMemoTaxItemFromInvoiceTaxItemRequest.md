# DebitMemoTaxItemFromInvoiceTaxItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the debit memo taxation item.  | [optional] 
**finance_information** | [**DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation**](DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation.md) |  | [optional] 
**jurisdiction** | **str** | The jurisdiction that applies the tax or VAT. This value is typically a state, province, county, or city.  | [optional] 
**location_code** | **str** | The identifier for the location based on the value of the &#x60;taxCode&#x60; field.  | [optional] 
**source_tax_item_id** | **str** | The ID of the source taxation item.  | [optional] 
**tax_code** | **str** | The tax code identifies which tax rules and tax rates to apply to a specific debit memo.  | [optional] 
**tax_code_description** | **str** | The description of the tax code.  | [optional] 
**tax_date** | **date** | The date that the tax is applied to the debit memo, in &#x60;yyyy-mm-dd&#x60; format.  | [optional] 
**tax_exempt_amount** | **float** | The calculated tax amount excluded due to the exemption.  | [optional] 
**tax_name** | **str** | The name of taxation.  | [optional] 
**tax_rate** | **float** | The tax rate applied to the debit memo.  | [optional] 
**tax_rate_description** | **str** | The description of the tax rate.  | [optional] 
**tax_rate_type** | [**TaxRateType**](TaxRateType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_tax_item_from_invoice_tax_item_request import DebitMemoTaxItemFromInvoiceTaxItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoTaxItemFromInvoiceTaxItemRequest from a JSON string
debit_memo_tax_item_from_invoice_tax_item_request_instance = DebitMemoTaxItemFromInvoiceTaxItemRequest.from_json(json)
# print the JSON string representation of the object
print(DebitMemoTaxItemFromInvoiceTaxItemRequest.to_json())

# convert the object into a dict
debit_memo_tax_item_from_invoice_tax_item_request_dict = debit_memo_tax_item_from_invoice_tax_item_request_instance.to_dict()
# create an instance of DebitMemoTaxItemFromInvoiceTaxItemRequest from a dict
debit_memo_tax_item_from_invoice_tax_item_request_from_dict = DebitMemoTaxItemFromInvoiceTaxItemRequest.from_dict(debit_memo_tax_item_from_invoice_tax_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


