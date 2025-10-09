# GetAccountPMAccountHolderInfo

The account holder information. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_holder_name** | **str** | The full name of the account holder.  | [optional] 
**address_line1** | **str** | The first line of the address for the account holder.  | [optional] 
**address_line2** | **str** | The second line of the address for the account holder.   | [optional] 
**city** | **str** | The city where the account holder stays.   | [optional] 
**country** | **str** | The country where the account holder stays.  When creating a payment method through a translated UI or Payment Page, a country name in a translated language might be selected. Regardless of the country texts selected when creating the payment method, only the country name listed in [Country Names and Their ISO Standard 2- and 3-Digit Codes](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Country%2C_State%2C_and_Province_Codes/A_Country_Names_and_Their_ISO_Codes) returns in this field. Internationalization is not supported for the API field value.  | [optional] 
**email** | **str** | The email address of the account holder.  | [optional] 
**phone** | **str** | The phone number of the account holder.  | [optional] 
**state** | **str** | The state where the account holder stays.  | [optional] 
**zip_code** | **str** | The zip code for the address of the account holder.  | [optional] 

## Example

```python
from zuora_sdk.models.get_account_pm_account_holder_info import GetAccountPMAccountHolderInfo

# TODO update the JSON string below
json = "{}"
# create an instance of GetAccountPMAccountHolderInfo from a JSON string
get_account_pm_account_holder_info_instance = GetAccountPMAccountHolderInfo.from_json(json)
# print the JSON string representation of the object
print(GetAccountPMAccountHolderInfo.to_json())

# convert the object into a dict
get_account_pm_account_holder_info_dict = get_account_pm_account_holder_info_instance.to_dict()
# create an instance of GetAccountPMAccountHolderInfo from a dict
get_account_pm_account_holder_info_from_dict = GetAccountPMAccountHolderInfo.from_dict(get_account_pm_account_holder_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


