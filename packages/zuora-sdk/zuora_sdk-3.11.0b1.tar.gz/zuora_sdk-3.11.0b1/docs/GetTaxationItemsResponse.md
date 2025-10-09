# GetTaxationItemsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 
**taxation_items** | [**List[TaxationItem]**](TaxationItem.md) | Container for taxation items.  | [optional] 

## Example

```python
from zuora_sdk.models.get_taxation_items_response import GetTaxationItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetTaxationItemsResponse from a JSON string
get_taxation_items_response_instance = GetTaxationItemsResponse.from_json(json)
# print the JSON string representation of the object
print(GetTaxationItemsResponse.to_json())

# convert the object into a dict
get_taxation_items_response_dict = get_taxation_items_response_instance.to_dict()
# create an instance of GetTaxationItemsResponse from a dict
get_taxation_items_response_from_dict = GetTaxationItemsResponse.from_dict(get_taxation_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


