# PreviewOrderSubscriptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Subscription object.  | [optional] 
**order_actions** | [**List[PreviewOrderOrderAction]**](PreviewOrderOrderAction.md) | The actions to be applied to the subscription. Order actions will be stored with the sequence when it was provided in the request. | [optional] 
**quote** | [**QuoteObjectFields**](QuoteObjectFields.md) |  | [optional] 
**ramp** | [**CreateRamp**](CreateRamp.md) |  | [optional] 
**subscription_number** | **str** | Leave this field empty to represent new subscription creation, or specify a subscription number to update an existing subscription. | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_subscriptions import PreviewOrderSubscriptions

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderSubscriptions from a JSON string
preview_order_subscriptions_instance = PreviewOrderSubscriptions.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderSubscriptions.to_json())

# convert the object into a dict
preview_order_subscriptions_dict = preview_order_subscriptions_instance.to_dict()
# create an instance of PreviewOrderSubscriptions from a dict
preview_order_subscriptions_from_dict = PreviewOrderSubscriptions.from_dict(preview_order_subscriptions_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


