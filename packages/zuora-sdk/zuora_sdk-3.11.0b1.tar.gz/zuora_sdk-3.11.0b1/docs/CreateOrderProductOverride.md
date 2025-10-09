# CreateOrderProductOverride


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rate_plan_overrides** | [**List[CreateOrderProductRatePlanOverride]**](CreateOrderProductRatePlanOverride.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_order_product_override import CreateOrderProductOverride

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderProductOverride from a JSON string
create_order_product_override_instance = CreateOrderProductOverride.from_json(json)
# print the JSON string representation of the object
print(CreateOrderProductOverride.to_json())

# convert the object into a dict
create_order_product_override_dict = create_order_product_override_instance.to_dict()
# create an instance of CreateOrderProductOverride from a dict
create_order_product_override_from_dict = CreateOrderProductOverride.from_dict(create_order_product_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


