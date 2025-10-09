# SignUpTaxInfo

Information about the tax exempt status of a customer account. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**vatid** | **str** | EU Value Added Tax ID.  **Note:** This feature is in Limited Availability. If you wish to have access to the feature, submit a request at [Zuora Global Support](https://support.zuora.com).  | [optional] 
**company_code** | **str** | Unique code that identifies a company account in Avalara. Use this field to calculate taxes based on origin and sold-to addresses in Avalara.  **Note:** This feature is in Limited Availability. If you wish to have access to the feature, submit a request at [Zuora Global Support](https://support.zuora.com).  | [optional] 
**exempt_certificate_id** | **str** | ID of the customer tax exemption certificate. Applicable if you use Zuora Tax or Connect tax engines.  | [optional] 
**exempt_certificate_type** | **str** | Type of tax exemption certificate that the customer holds. Applicable if you use Zuora Tax or Connect tax engines.  | [optional] 
**exempt_description** | **str** | Description of the tax exemption certificate that the customer holds. Applicable if you use Zuora Tax or Connect tax engines.  | [optional] 
**exempt_effective_date** | **date** | Date when the customer tax exemption starts, in YYYY-MM-DD format. Applicable if you use Zuora Tax or Connect tax engines.  | [optional] 
**exempt_expiration_date** | **date** | Date when the customer tax exemption expires, in YYYY-MM-DD format. Applicable if you use Zuora Tax or Connect tax engines.  | [optional] 
**exempt_issuing_jurisdiction** | **str** | Jurisdiction in which the customer tax exemption certificate was issued.  | [optional] 
**exempt_status** | [**SignUpTaxInfoExemptStatus**](SignUpTaxInfoExemptStatus.md) |  | [optional] [default to SignUpTaxInfoExemptStatus.NO]

## Example

```python
from zuora_sdk.models.sign_up_tax_info import SignUpTaxInfo

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpTaxInfo from a JSON string
sign_up_tax_info_instance = SignUpTaxInfo.from_json(json)
# print the JSON string representation of the object
print(SignUpTaxInfo.to_json())

# convert the object into a dict
sign_up_tax_info_dict = sign_up_tax_info_instance.to_dict()
# create an instance of SignUpTaxInfo from a dict
sign_up_tax_info_from_dict = SignUpTaxInfo.from_dict(sign_up_tax_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


