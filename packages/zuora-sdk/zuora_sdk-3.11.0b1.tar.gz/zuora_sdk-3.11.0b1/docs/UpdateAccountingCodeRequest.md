# UpdateAccountingCodeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gl_account_name** | **str** | Name of the account in your general ledger.   Field only available if you have Zuora Finance enabled. Maximum of 255 characters. | [optional] 
**gl_account_number** | **str** | Account number in your general ledger.   Field only available if you have Zuora Finance enabled. Maximum of 255 characters. | [optional] 
**name** | **str** | Name of the accounting code.  Accounting code name must be unique. Maximum of 100 characters.  | [optional] 
**notes** | **str** | Maximum of 2,000 characters.  | [optional] 
**type** | [**AccountingCodeType**](AccountingCodeType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_accounting_code_request import UpdateAccountingCodeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateAccountingCodeRequest from a JSON string
update_accounting_code_request_instance = UpdateAccountingCodeRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateAccountingCodeRequest.to_json())

# convert the object into a dict
update_accounting_code_request_dict = update_accounting_code_request_instance.to_dict()
# create an instance of UpdateAccountingCodeRequest from a dict
update_accounting_code_request_from_dict = UpdateAccountingCodeRequest.from_dict(update_accounting_code_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


