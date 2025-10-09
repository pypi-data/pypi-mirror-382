# CreateOrderResponseRefunds


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**number** | **str** | The refund number. For example, &#x60;R-00009564&#x60;. | [optional] 
**refund_invoice_numbers** | **List[str]** | An array of the refunded invoice numbers generated in this order request. | [optional] 
**status** | [**CreateOrderResponseRefundStatus**](CreateOrderResponseRefundStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_order_response_refunds import CreateOrderResponseRefunds

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResponseRefunds from a JSON string
create_order_response_refunds_instance = CreateOrderResponseRefunds.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResponseRefunds.to_json())

# convert the object into a dict
create_order_response_refunds_dict = create_order_response_refunds_instance.to_dict()
# create an instance of CreateOrderResponseRefunds from a dict
create_order_response_refunds_from_dict = CreateOrderResponseRefunds.from_dict(create_order_response_refunds_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


