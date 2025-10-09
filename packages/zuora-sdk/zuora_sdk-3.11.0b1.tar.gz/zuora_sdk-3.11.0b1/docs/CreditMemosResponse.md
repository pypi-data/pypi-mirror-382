# CreditMemosResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**creditmemos** | [**List[CreditMemo]**](CreditMemo.md) | Container for credit memos.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.credit_memos_response import CreditMemosResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemosResponse from a JSON string
credit_memos_response_instance = CreditMemosResponse.from_json(json)
# print the JSON string representation of the object
print(CreditMemosResponse.to_json())

# convert the object into a dict
credit_memos_response_dict = credit_memos_response_instance.to_dict()
# create an instance of CreditMemosResponse from a dict
credit_memos_response_from_dict = CreditMemosResponse.from_dict(credit_memos_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


