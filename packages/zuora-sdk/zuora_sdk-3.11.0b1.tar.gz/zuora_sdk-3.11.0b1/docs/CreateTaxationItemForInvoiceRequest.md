# CreateTaxationItemForInvoiceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exempt_amount** | **decimal.Decimal** | The calculated tax amount excluded due to the exemption.  | [optional] 
**finance_information** | [**TaxItemsFinanceInformation**](TaxItemsFinanceInformation.md) |  | [optional] 
**invoice_item_id** | **str** | The ID of the invoice associated with the taxation item.  | 
**jurisdiction** | **str** | The jurisdiction that applies the tax or VAT. This value is typically a state, province, county, or city.  | 
**location_code** | **str** | The identifier for the location based on the value of the &#x60;taxCode&#x60; field.  | [optional] 
**name** | **str** | The name of taxation.  | 
**tax_amount** | **decimal.Decimal** | The amount of the taxation item in the invoice item.  | 
**applicable_tax_un_rounded** | **decimal.Decimal** | The unrounded amount of the tax.  | [optional] 
**country** | **str** | The field which contains country code.  | [optional] 
**tax_code** | **str** | The tax code identifies which tax rules and tax rates to apply to a specific invoice item.  | [optional] 
**tax_code_description** | **str** | The description of the tax code.  | [optional] 
**tax_date** | **date** | The date that the tax is applied to the invoice item, in &#x60;yyyy-mm-dd&#x60; format.  | 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**tax_rate** | **decimal.Decimal** | The tax rate applied to the invoice item.  | 
**tax_rate_description** | **str** | The description of the tax rate.  | [optional] 
**tax_rate_type** | [**TaxRateType**](TaxRateType.md) |  | 

## Example

```python
from zuora_sdk.models.create_taxation_item_for_invoice_request import CreateTaxationItemForInvoiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTaxationItemForInvoiceRequest from a JSON string
create_taxation_item_for_invoice_request_instance = CreateTaxationItemForInvoiceRequest.from_json(json)
# print the JSON string representation of the object
print(CreateTaxationItemForInvoiceRequest.to_json())

# convert the object into a dict
create_taxation_item_for_invoice_request_dict = create_taxation_item_for_invoice_request_instance.to_dict()
# create an instance of CreateTaxationItemForInvoiceRequest from a dict
create_taxation_item_for_invoice_request_from_dict = CreateTaxationItemForInvoiceRequest.from_dict(create_taxation_item_for_invoice_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


