# GetAccountingCodesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_codes** | [**List[AccountingCodeItemResponse]**](AccountingCodeItemResponse.md) | An array of all the accounting codes in your chart of accounts. Each accounting code has the following fields. | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_accounting_codes_response import GetAccountingCodesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAccountingCodesResponse from a JSON string
get_accounting_codes_response_instance = GetAccountingCodesResponse.from_json(json)
# print the JSON string representation of the object
print(GetAccountingCodesResponse.to_json())

# convert the object into a dict
get_accounting_codes_response_dict = get_accounting_codes_response_instance.to_dict()
# create an instance of GetAccountingCodesResponse from a dict
get_accounting_codes_response_from_dict = GetAccountingCodesResponse.from_dict(get_accounting_codes_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


