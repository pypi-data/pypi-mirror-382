# GetSubscriptionProductFeature


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | SubscriptionProductFeature ID. | [optional] 
**description** | **str** | Feature description. | [optional] 
**feature_code** | **str** | Feature code, up to 255 characters long. | [optional] 
**name** | **str** | Feature name, up to 255 characters long. | [optional] 

## Example

```python
from zuora_sdk.models.get_subscription_product_feature import GetSubscriptionProductFeature

# TODO update the JSON string below
json = "{}"
# create an instance of GetSubscriptionProductFeature from a JSON string
get_subscription_product_feature_instance = GetSubscriptionProductFeature.from_json(json)
# print the JSON string representation of the object
print(GetSubscriptionProductFeature.to_json())

# convert the object into a dict
get_subscription_product_feature_dict = get_subscription_product_feature_instance.to_dict()
# create an instance of GetSubscriptionProductFeature from a dict
get_subscription_product_feature_from_dict = GetSubscriptionProductFeature.from_dict(get_subscription_product_feature_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


