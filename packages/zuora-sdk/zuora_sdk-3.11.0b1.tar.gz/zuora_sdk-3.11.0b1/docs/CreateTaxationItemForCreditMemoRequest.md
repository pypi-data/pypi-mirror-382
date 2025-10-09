# CreateTaxationItemForCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exempt_amount** | **float** | The calculated tax amount excluded due to the exemption.  | [optional] 
**finance_information** | [**CreateTaxationItemForCreditMemoFinanceInformation**](CreateTaxationItemForCreditMemoFinanceInformation.md) |  | [optional] 
**jurisdiction** | **str** | The jurisdiction that applies the tax or VAT. This value is typically a state, province, county, or city.  | 
**location_code** | **str** | The identifier for the location based on the value of the &#x60;taxCode&#x60; field.  | [optional] 
**memo_item_id** | **str** | The ID of the credit memo that the taxation item is created for.  | [optional] 
**name** | **str** | The name of the taxation item.  | 
**source_tax_item_id** | **str** | The ID of the taxation item of the invoice, which the credit memo is created from.   If you want to use this REST API to create taxation items for a credit memo created from an invoice, the taxation items of the invoice must be created or imported through the SOAP API call.  **Note:**    - This field is only used if the credit memo is created from an invoice.    - If you do not contain this field in the request body, Zuora will automatically set a value for the &#x60;sourceTaxItemId&#x60; field based on the tax location code, tax jurisdiction, and tax rate.  | [optional] 
**tax_amount** | **float** | The amount of the tax applied to the credit memo.  | 
**applicable_tax_un_rounded** | **float** | The unrounded amount of the tax.  | [optional] 
**country** | **str** | The field which contains country code.  | [optional] 
**tax_code** | **str** | The tax code identifies which tax rules and tax rates to apply to a specific credit memo.  | [optional] 
**tax_code_description** | **str** | The description of the tax code.  | [optional] 
**tax_date** | **date** | The date when the tax is applied to the credit memo.  | [optional] 
**tax_rate** | **float** | The tax rate applied to the credit memo.  | 
**tax_rate_description** | **str** | The description of the tax rate.  | [optional] 
**tax_rate_type** | [**TaxRateType**](TaxRateType.md) |  | 

## Example

```python
from zuora_sdk.models.create_taxation_item_for_credit_memo_request import CreateTaxationItemForCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTaxationItemForCreditMemoRequest from a JSON string
create_taxation_item_for_credit_memo_request_instance = CreateTaxationItemForCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(CreateTaxationItemForCreditMemoRequest.to_json())

# convert the object into a dict
create_taxation_item_for_credit_memo_request_dict = create_taxation_item_for_credit_memo_request_instance.to_dict()
# create an instance of CreateTaxationItemForCreditMemoRequest from a dict
create_taxation_item_for_credit_memo_request_from_dict = CreateTaxationItemForCreditMemoRequest.from_dict(create_taxation_item_for_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


