# TaxationItemsDataResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**data** | [**List[InvoiceTaxationItem]**](InvoiceTaxationItem.md) | Container for the taxation items of the invoice item.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.taxation_items_data_response import TaxationItemsDataResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TaxationItemsDataResponse from a JSON string
taxation_items_data_response_instance = TaxationItemsDataResponse.from_json(json)
# print the JSON string representation of the object
print(TaxationItemsDataResponse.to_json())

# convert the object into a dict
taxation_items_data_response_dict = taxation_items_data_response_instance.to_dict()
# create an instance of TaxationItemsDataResponse from a dict
taxation_items_data_response_from_dict = TaxationItemsDataResponse.from_dict(taxation_items_data_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


