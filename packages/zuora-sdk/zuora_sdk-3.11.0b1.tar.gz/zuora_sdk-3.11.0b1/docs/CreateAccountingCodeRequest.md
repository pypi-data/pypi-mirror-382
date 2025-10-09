# CreateAccountingCodeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gl_account_name** | **str** | Name of the account in your general ledger.   Field only available if you have Zuora Finance enabled. Maximum of 255 characters. | [optional] 
**gl_account_number** | **str** | Account number in your general ledger.   Field only available if you have Zuora Finance enabled. Maximum of 255 characters. | [optional] 
**name** | **str** | Name of the accounting code.  Accounting code name must be unique. Maximum of 100 characters.  | 
**notes** | **str** | Maximum of 2,000 characters.  | [optional] 
**type** | [**AccountingCodeType**](AccountingCodeType.md) |  | 
**segment_constant_values** | **Dict[str, object]** | Segment constant values. Field only available if you have GL Segmentation 2.0 enabled. | [optional] 

## Example

```python
from zuora_sdk.models.create_accounting_code_request import CreateAccountingCodeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAccountingCodeRequest from a JSON string
create_accounting_code_request_instance = CreateAccountingCodeRequest.from_json(json)
# print the JSON string representation of the object
print(CreateAccountingCodeRequest.to_json())

# convert the object into a dict
create_accounting_code_request_dict = create_accounting_code_request_instance.to_dict()
# create an instance of CreateAccountingCodeRequest from a dict
create_accounting_code_request_from_dict = CreateAccountingCodeRequest.from_dict(create_accounting_code_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


