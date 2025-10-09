# QueryProductsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedProduct]**](ExpandedProduct.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_products_response import QueryProductsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryProductsResponse from a JSON string
query_products_response_instance = QueryProductsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryProductsResponse.to_json())

# convert the object into a dict
query_products_response_dict = query_products_response_instance.to_dict()
# create an instance of QueryProductsResponse from a dict
query_products_response_from_dict = QueryProductsResponse.from_dict(query_products_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


