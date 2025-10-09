# CreateTaxationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exempt_amount** | **float** | The calculated tax amount excluded due to the exemption. | [optional] 
**jurisdiction** | **str** | The jurisdiction that applies the tax or VAT. This value is typically a state, province, county, or city. | [optional] 
**location_code** | **str** | The identifier for the location based on the value of the &#x60;taxCode&#x60; field. | [optional] 
**name** | **str** | The name of taxation. | 
**tax_amount** | **float** | The amount of the taxation item in the invoice item. | 
**tax_code** | **str** | The tax code identifies which tax rules and tax rates to apply to a specific invoice item. | 
**tax_code_description** | **str** | The description of the tax code. | [optional] 
**tax_date** | **date** | The date that the tax is applied to the invoice item, in &#x60;yyyy-mm-dd&#x60; format. | 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | 
**tax_rate** | **decimal.Decimal** | The tax rate applied to the invoice item. | 
**tax_rate_description** | **str** | The description of the tax rate. | [optional] 
**tax_rate_type** | [**TaxRateType**](TaxRateType.md) |  | 

## Example

```python
from zuora_sdk.models.create_taxation_item import CreateTaxationItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTaxationItem from a JSON string
create_taxation_item_instance = CreateTaxationItem.from_json(json)
# print the JSON string representation of the object
print(CreateTaxationItem.to_json())

# convert the object into a dict
create_taxation_item_dict = create_taxation_item_instance.to_dict()
# create an instance of CreateTaxationItem from a dict
create_taxation_item_from_dict = CreateTaxationItem.from_dict(create_taxation_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


