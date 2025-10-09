# GetCreditMemoItemPartsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**item_parts** | [**List[CreditMemoItemPart]**](CreditMemoItemPart.md) | Container for credit memo part items.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_credit_memo_item_parts_response import GetCreditMemoItemPartsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCreditMemoItemPartsResponse from a JSON string
get_credit_memo_item_parts_response_instance = GetCreditMemoItemPartsResponse.from_json(json)
# print the JSON string representation of the object
print(GetCreditMemoItemPartsResponse.to_json())

# convert the object into a dict
get_credit_memo_item_parts_response_dict = get_credit_memo_item_parts_response_instance.to_dict()
# create an instance of GetCreditMemoItemPartsResponse from a dict
get_credit_memo_item_parts_response_from_dict = GetCreditMemoItemPartsResponse.from_dict(get_credit_memo_item_parts_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


