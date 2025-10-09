# GetCreditMemoItemTaxationItems

Container for the taxation items of the credit memo item.    **Note**: This field is only available if you set the `zuora-version` request header to `239.0` or later.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[GetCreditMemoTaxationItemResponse]**](GetCreditMemoTaxationItemResponse.md) | List of taxation items.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.get_credit_memo_item_taxation_items import GetCreditMemoItemTaxationItems

# TODO update the JSON string below
json = "{}"
# create an instance of GetCreditMemoItemTaxationItems from a JSON string
get_credit_memo_item_taxation_items_instance = GetCreditMemoItemTaxationItems.from_json(json)
# print the JSON string representation of the object
print(GetCreditMemoItemTaxationItems.to_json())

# convert the object into a dict
get_credit_memo_item_taxation_items_dict = get_credit_memo_item_taxation_items_instance.to_dict()
# create an instance of GetCreditMemoItemTaxationItems from a dict
get_credit_memo_item_taxation_items_from_dict = GetCreditMemoItemTaxationItems.from_dict(get_credit_memo_item_taxation_items_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


