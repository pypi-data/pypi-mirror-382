# CreateOrderSubscription


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Subscription object.  | [optional] 
**order_actions** | [**List[CreateOrderAction]**](CreateOrderAction.md) | The actions to be applied to the subscription. Order actions will be stored with the sequence when it was provided in the request. | [optional] 
**quote** | [**QuoteObjectFields**](QuoteObjectFields.md) |  | [optional] 
**ramp** | [**CreateRamp**](CreateRamp.md) |  | [optional] 
**notes** | **str** | A string of up to 65,535 characters.  | [optional] 
**subscription_number** | **str** | Leave this empty to represent new subscription creation. Specify a subscription number to update an existing subscription. | [optional] 

## Example

```python
from zuora_sdk.models.create_order_subscription import CreateOrderSubscription

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderSubscription from a JSON string
create_order_subscription_instance = CreateOrderSubscription.from_json(json)
# print the JSON string representation of the object
print(CreateOrderSubscription.to_json())

# convert the object into a dict
create_order_subscription_dict = create_order_subscription_instance.to_dict()
# create an instance of CreateOrderSubscription from a dict
create_order_subscription_from_dict = CreateOrderSubscription.from_dict(create_order_subscription_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


