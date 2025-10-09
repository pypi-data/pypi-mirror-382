# ProductFeature


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Feature ID.  | [optional] 
**name** | **str** | Feature name, up to 255 characters long.  | [optional] 
**code** | **str** | Feature code, up to 255 characters long.  | [optional] 
**status** | **str** |  | [optional] 
**description** | **str** | Feature description.  | [optional] 

## Example

```python
from zuora_sdk.models.product_feature import ProductFeature

# TODO update the JSON string below
json = "{}"
# create an instance of ProductFeature from a JSON string
product_feature_instance = ProductFeature.from_json(json)
# print the JSON string representation of the object
print(ProductFeature.to_json())

# convert the object into a dict
product_feature_dict = product_feature_instance.to_dict()
# create an instance of ProductFeature from a dict
product_feature_from_dict = ProductFeature.from_dict(product_feature_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


