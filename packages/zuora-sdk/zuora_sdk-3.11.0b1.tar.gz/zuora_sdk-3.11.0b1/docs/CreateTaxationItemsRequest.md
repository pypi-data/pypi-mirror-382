# CreateTaxationItemsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**taxation_items** | [**List[CreateTaxationItemForInvoiceRequest]**](CreateTaxationItemForInvoiceRequest.md) | Container for taxation items.  | 

## Example

```python
from zuora_sdk.models.create_taxation_items_request import CreateTaxationItemsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTaxationItemsRequest from a JSON string
create_taxation_items_request_instance = CreateTaxationItemsRequest.from_json(json)
# print the JSON string representation of the object
print(CreateTaxationItemsRequest.to_json())

# convert the object into a dict
create_taxation_items_request_dict = create_taxation_items_request_instance.to_dict()
# create an instance of CreateTaxationItemsRequest from a dict
create_taxation_items_request_from_dict = CreateTaxationItemsRequest.from_dict(create_taxation_items_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


