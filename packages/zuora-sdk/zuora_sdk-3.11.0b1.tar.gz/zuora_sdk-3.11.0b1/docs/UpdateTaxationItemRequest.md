# UpdateTaxationItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exempt_amount** | **float** | The calculated tax amount excluded due to the exemption.  | [optional] 
**finance_information** | [**UpdateTaxationItemForFinanceInformation**](UpdateTaxationItemForFinanceInformation.md) |  | [optional] 
**jurisdiction** | **str** | The jurisdiction that applies the tax or VAT. This value is typically a state, province, county, or city.  | [optional] 
**location_code** | **str** | The identifier for the location based on the value of the &#x60;taxCode&#x60; field.   | [optional] 
**name** | **str** | The name of the taxation item to be updated.  | [optional] 
**tax_amount** | **float** | The amount of the tax applied to the credit or debit memo.  | [optional] 
**applicable_tax_un_rounded** | **float** | The unrounded amount of the tax.  | [optional] 
**country** | **str** | The field which contains country code.  | [optional] 
**tax_code** | **str** | The tax code identifies which tax rules and tax rates to apply to a specific credit or debit memo.  | [optional] 
**tax_code_description** | **str** | The description of the tax code.  | [optional] 
**tax_date** | **date** | The date when the tax is applied to the credit or debit memo.  | [optional] 
**tax_rate** | **float** | The tax rate applied to the credit or debit memo.  | [optional] 
**tax_rate_description** | **str** | The description of the tax rate.   | [optional] 
**tax_rate_type** | [**TaxRateType**](TaxRateType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_taxation_item_request import UpdateTaxationItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateTaxationItemRequest from a JSON string
update_taxation_item_request_instance = UpdateTaxationItemRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateTaxationItemRequest.to_json())

# convert the object into a dict
update_taxation_item_request_dict = update_taxation_item_request_instance.to_dict()
# create an instance of UpdateTaxationItemRequest from a dict
update_taxation_item_request_from_dict = UpdateTaxationItemRequest.from_dict(update_taxation_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


