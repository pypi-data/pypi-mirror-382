# GetAccountingCodeResponse


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
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**type** | [**AccountingCodeType**](AccountingCodeType.md) |  | [optional] 
**segment_constant_values** | **Dict[str, object]** | Segment constant values. Field only available if you have GL Segmentation 2.0 enabled. | [optional] 
**updated_by** | **str** | The ID of the user who last updated the accounting code.  | [optional] 
**updated_on** | **str** | Date and time when the accounting code was last updated.  | [optional] 

## Example

```python
from zuora_sdk.models.get_accounting_code_response import GetAccountingCodeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAccountingCodeResponse from a JSON string
get_accounting_code_response_instance = GetAccountingCodeResponse.from_json(json)
# print the JSON string representation of the object
print(GetAccountingCodeResponse.to_json())

# convert the object into a dict
get_accounting_code_response_dict = get_accounting_code_response_instance.to_dict()
# create an instance of GetAccountingCodeResponse from a dict
get_accounting_code_response_from_dict = GetAccountingCodeResponse.from_dict(get_accounting_code_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


