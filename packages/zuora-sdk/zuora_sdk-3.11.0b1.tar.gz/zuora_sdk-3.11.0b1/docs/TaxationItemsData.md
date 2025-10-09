# TaxationItemsData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[InvoiceTaxationItem]**](InvoiceTaxationItem.md) | Container for the taxation items of the invoice item.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.taxation_items_data import TaxationItemsData

# TODO update the JSON string below
json = "{}"
# create an instance of TaxationItemsData from a JSON string
taxation_items_data_instance = TaxationItemsData.from_json(json)
# print the JSON string representation of the object
print(TaxationItemsData.to_json())

# convert the object into a dict
taxation_items_data_dict = taxation_items_data_instance.to_dict()
# create an instance of TaxationItemsData from a dict
taxation_items_data_from_dict = TaxationItemsData.from_dict(taxation_items_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


