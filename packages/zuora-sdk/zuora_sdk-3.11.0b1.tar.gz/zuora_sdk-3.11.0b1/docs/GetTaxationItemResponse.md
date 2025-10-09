# GetTaxationItemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by_id** | **str** | The ID of the Zuora user who created the taxation item. | [optional] 
**created_date** | **str** | The date and time when the taxation item was created in the Zuora system, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**exempt_amount** | **float** | The calculated tax amount excluded due to the exemption. | [optional] 
**finance_information** | [**TaxationItemFinanceInformation**](TaxationItemFinanceInformation.md) |  | [optional] 
**id** | **str** | The ID of the taxation item. | [optional] 
**invoice_item_id** | **str** | The ID of the invoice associated with the taxation item. | [optional] 
**jurisdiction** | **str** | The jurisdiction that applies the tax or VAT. This value is typically a state, province, county, or city. | [optional] 
**location_code** | **str** | The identifier for the location based on the value of the &#x60;taxCode&#x60; field. | [optional] 
**memo_item_id** | **str** | The identifier for the memo item which is related to this tax item | [optional] 
**name** | **str** | The name of the taxation item. | [optional] 
**source_tax_item_id** | **str** | The identifier for which tax item the credit memo/debit memo was given to | [optional] 
**tax_amount** | **float** | The amount of the tax applied to the invoice. | [optional] 
**applicable_tax_un_rounded** | **float** | The unrounded amount of the tax. | [optional] 
**country** | **str** | The field which contains country code. | [optional] 
**tax_code** | **str** | The tax code identifies which tax rules and tax rates to apply to a specific invoice. | [optional] 
**tax_code_description** | **str** | The description of the tax code. | [optional] 
**tax_date** | **date** | The date when the tax is applied to the invoice. | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**tax_rate** | **float** | The tax rate applied to the invoice. | [optional] 
**tax_rate_description** | **str** | The description of the tax rate. | [optional] 
**tax_rate_type** | [**TaxRateType**](TaxRateType.md) |  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the taxation item. | [optional] 
**updated_date** | **str** | The date and time when the taxation item was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_taxation_item_response import GetTaxationItemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetTaxationItemResponse from a JSON string
get_taxation_item_response_instance = GetTaxationItemResponse.from_json(json)
# print the JSON string representation of the object
print(GetTaxationItemResponse.to_json())

# convert the object into a dict
get_taxation_item_response_dict = get_taxation_item_response_instance.to_dict()
# create an instance of GetTaxationItemResponse from a dict
get_taxation_item_response_from_dict = GetTaxationItemResponse.from_dict(get_taxation_item_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


