# AccountingCodeItemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category** | [**AccountingCodeCategory**](AccountingCodeCategory.md) |  | [optional] 
**created_by** | **str** | The ID of the user who created the accounting code.  | [optional] 
**created_on** | **str** | Date and time when the accounting code was created.  | [optional] 
**gl_account_name** | **str** | Name of the account in your general ledger.  Field only available if you have Zuora Finance enabled.  | [optional] 
**gl_account_number** | **str** | Account number in your general ledger.  Field only available if you have Zuora Finance enabled.  | [optional] 
**id** | **str** | ID of the accounting code.  | [optional] 
**name** | **str** | Name of the accounting code.  | [optional] 
**notes** | **str** | Any optional notes for the accounting code.  | [optional] 
**status** | [**AccountingCodeStatus**](AccountingCodeStatus.md) |  | [optional] 
**type** | [**AccountingCodeType**](AccountingCodeType.md) |  | [optional] 
**updated_by** | **str** | The ID of the user who last updated the accounting code.  | [optional] 
**updated_on** | **str** | Date and time when the accounting code was last updated.  | [optional] 

## Example

```python
from zuora_sdk.models.accounting_code_item_response import AccountingCodeItemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AccountingCodeItemResponse from a JSON string
accounting_code_item_response_instance = AccountingCodeItemResponse.from_json(json)
# print the JSON string representation of the object
print(AccountingCodeItemResponse.to_json())

# convert the object into a dict
accounting_code_item_response_dict = accounting_code_item_response_instance.to_dict()
# create an instance of AccountingCodeItemResponse from a dict
accounting_code_item_response_from_dict = AccountingCodeItemResponse.from_dict(accounting_code_item_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


