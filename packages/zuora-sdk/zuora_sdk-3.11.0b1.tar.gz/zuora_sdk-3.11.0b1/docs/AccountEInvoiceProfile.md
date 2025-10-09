# AccountEInvoiceProfile


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | enabled  | [optional] 
**business_name** | **str** | businessName.  | [optional] 
**business_number** | **str** | businessNumber.  | [optional] 
**business_number_scheme_id** | **str** | businessNumberSchemeId.  | [optional] 
**endpoint_id** | **str** | endpointId.  | [optional] 
**endpoint_scheme_id** | **str** | endpointSchemeId.  | [optional] 
**tax_register_number** | **str** | taxRegisterNumber.  | [optional] 
**business_category** | **str** | A field to identify the business category on the Account Einvoice Profile.  | [optional] 

## Example

```python
from zuora_sdk.models.account_e_invoice_profile import AccountEInvoiceProfile

# TODO update the JSON string below
json = "{}"
# create an instance of AccountEInvoiceProfile from a JSON string
account_e_invoice_profile_instance = AccountEInvoiceProfile.from_json(json)
# print the JSON string representation of the object
print(AccountEInvoiceProfile.to_json())

# convert the object into a dict
account_e_invoice_profile_dict = account_e_invoice_profile_instance.to_dict()
# create an instance of AccountEInvoiceProfile from a dict
account_e_invoice_profile_from_dict = AccountEInvoiceProfile.from_dict(account_e_invoice_profile_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


