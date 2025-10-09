# CreateOrderResponseWriteOff


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount written off from the invoice balance. | [optional] 
**failed_reason** | **str** | The reason of write-off failure. | [optional] 
**invoice_number** | **str** | The number of the invoice that is written off. For example, &#x60;INV00051208&#x60;. | [optional] 
**status** | [**CreateOrderResponseWriteOffStatus**](CreateOrderResponseWriteOffStatus.md) |  | [optional] 
**write_off_credit_memo_number** | **str** | The number of the credit memo that is written off. | [optional] 

## Example

```python
from zuora_sdk.models.create_order_response_write_off import CreateOrderResponseWriteOff

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResponseWriteOff from a JSON string
create_order_response_write_off_instance = CreateOrderResponseWriteOff.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResponseWriteOff.to_json())

# convert the object into a dict
create_order_response_write_off_dict = create_order_response_write_off_instance.to_dict()
# create an instance of CreateOrderResponseWriteOff from a dict
create_order_response_write_off_from_dict = CreateOrderResponseWriteOff.from_dict(create_order_response_write_off_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


