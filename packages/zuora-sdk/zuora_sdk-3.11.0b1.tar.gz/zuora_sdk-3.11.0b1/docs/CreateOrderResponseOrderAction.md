# CreateOrderResponseOrderAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The Id of the order action processed in the order. | [optional] 
**type** | [**OrderActionType**](OrderActionType.md) |  | [optional] 
**order_metrics** | [**List[CreateOrderResponseOrderMetric]**](CreateOrderResponseOrderMetric.md) | subscription order metrics | [optional] 

## Example

```python
from zuora_sdk.models.create_order_response_order_action import CreateOrderResponseOrderAction

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResponseOrderAction from a JSON string
create_order_response_order_action_instance = CreateOrderResponseOrderAction.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResponseOrderAction.to_json())

# convert the object into a dict
create_order_response_order_action_dict = create_order_response_order_action_instance.to_dict()
# create an instance of CreateOrderResponseOrderAction from a dict
create_order_response_order_action_from_dict = CreateOrderResponseOrderAction.from_dict(create_order_response_order_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


