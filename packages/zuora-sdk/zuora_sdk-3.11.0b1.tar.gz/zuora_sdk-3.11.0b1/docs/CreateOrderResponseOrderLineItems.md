# CreateOrderResponseOrderLineItems


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The sytem generated Id for the Order Line Item. | [optional] 
**item_number** | **str** | The number for the Order Line Item. | [optional] 

## Example

```python
from zuora_sdk.models.create_order_response_order_line_items import CreateOrderResponseOrderLineItems

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResponseOrderLineItems from a JSON string
create_order_response_order_line_items_instance = CreateOrderResponseOrderLineItems.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResponseOrderLineItems.to_json())

# convert the object into a dict
create_order_response_order_line_items_dict = create_order_response_order_line_items_instance.to_dict()
# create an instance of CreateOrderResponseOrderLineItems from a dict
create_order_response_order_line_items_from_dict = CreateOrderResponseOrderLineItems.from_dict(create_order_response_order_line_items_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


