# SubscriptionProductFeature


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | SubscriptionProductFeature ID. | [optional] 
**description** | **str** | Feature description. | [optional] 
**feature_code** | **str** | Feature code, up to 255 characters long. | [optional] 
**name** | **str** | Feature name, up to 255 characters long. | [optional] 

## Example

```python
from zuora_sdk.models.subscription_product_feature import SubscriptionProductFeature

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionProductFeature from a JSON string
subscription_product_feature_instance = SubscriptionProductFeature.from_json(json)
# print the JSON string representation of the object
print(SubscriptionProductFeature.to_json())

# convert the object into a dict
subscription_product_feature_dict = subscription_product_feature_instance.to_dict()
# create an instance of SubscriptionProductFeature from a dict
subscription_product_feature_from_dict = SubscriptionProductFeature.from_dict(subscription_product_feature_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


