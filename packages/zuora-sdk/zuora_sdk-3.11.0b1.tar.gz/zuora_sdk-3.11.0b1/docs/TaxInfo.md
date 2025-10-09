# TaxInfo

Information about the tax exempt status of a customer account.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**company_code** | **str** | Unique code that identifies a company account in Avalara. Use this field to calculate taxes based on origin and sold-to addresses in Avalara.  **Note:** This feature is in Limited Availability. If you wish to have access to the feature, submit a request at [Zuora Global Support](https://support.zuora.com).a | [optional] 
**exempt_entity_use_code** | **str** | A unique entity use code to apply exemptions in Avalara AvaTax.   This account-level field is required only when you choose Avalara as your tax engine. See [Exempt Transactions](https://developer.avalara.com/avatax/handling-tax-exempt-customers/)for more details. | [optional] 
**exempt_certificate_id** | **str** | ID of the customer tax exemption certificate. Applicable if you use Zuora Tax or Connect tax engines. | [optional] 
**exempt_certificate_type** | **str** | Type of tax exemption certificate that the customer holds. Applicable if you use Zuora Tax or Connect tax engines. | [optional] 
**exempt_description** | **str** | Description of the tax exemption certificate that the customer holds. Applicable if you use Zuora Tax or Connect tax engines. | [optional] 
**exempt_effective_date** | **date** | Date when the customer tax exemption starts, in YYYY-MM-DD format. Applicable if you use Zuora Tax or Connect tax engines. | [optional] 
**exempt_expiration_date** | **date** | Date when the customer tax exemption expires, in YYYY-MM-DD format. Applicable if you use Zuora Tax or Connect tax engines. | [optional] 
**exempt_issuing_jurisdiction** | **str** | Jurisdiction in which the customer tax exemption certificate was issued. | [optional] 
**exempt_status** | [**TaxExemptStatus**](TaxExemptStatus.md) |  | [optional] [default to TaxExemptStatus.NO]
**vatid** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.tax_info import TaxInfo

# TODO update the JSON string below
json = "{}"
# create an instance of TaxInfo from a JSON string
tax_info_instance = TaxInfo.from_json(json)
# print the JSON string representation of the object
print(TaxInfo.to_json())

# convert the object into a dict
tax_info_dict = tax_info_instance.to_dict()
# create an instance of TaxInfo from a dict
tax_info_from_dict = TaxInfo.from_dict(tax_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


