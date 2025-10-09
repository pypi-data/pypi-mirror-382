# GetTaxationItemsOfCreditMemoItemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[GetCreditMemoTaxItemResponse]**](GetCreditMemoTaxItemResponse.md) | Container for the taxation items of the credit memo item.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_taxation_items_of_credit_memo_item_response import GetTaxationItemsOfCreditMemoItemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetTaxationItemsOfCreditMemoItemResponse from a JSON string
get_taxation_items_of_credit_memo_item_response_instance = GetTaxationItemsOfCreditMemoItemResponse.from_json(json)
# print the JSON string representation of the object
print(GetTaxationItemsOfCreditMemoItemResponse.to_json())

# convert the object into a dict
get_taxation_items_of_credit_memo_item_response_dict = get_taxation_items_of_credit_memo_item_response_instance.to_dict()
# create an instance of GetTaxationItemsOfCreditMemoItemResponse from a dict
get_taxation_items_of_credit_memo_item_response_from_dict = GetTaxationItemsOfCreditMemoItemResponse.from_dict(get_taxation_items_of_credit_memo_item_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


