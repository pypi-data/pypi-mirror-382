# GetCreditMemoPartsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**parts** | [**List[CreditMemoPart]**](CreditMemoPart.md) | Container for credit memo parts.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_credit_memo_parts_response import GetCreditMemoPartsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCreditMemoPartsResponse from a JSON string
get_credit_memo_parts_response_instance = GetCreditMemoPartsResponse.from_json(json)
# print the JSON string representation of the object
print(GetCreditMemoPartsResponse.to_json())

# convert the object into a dict
get_credit_memo_parts_response_dict = get_credit_memo_parts_response_instance.to_dict()
# create an instance of GetCreditMemoPartsResponse from a dict
get_credit_memo_parts_response_from_dict = GetCreditMemoPartsResponse.from_dict(get_credit_memo_parts_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


