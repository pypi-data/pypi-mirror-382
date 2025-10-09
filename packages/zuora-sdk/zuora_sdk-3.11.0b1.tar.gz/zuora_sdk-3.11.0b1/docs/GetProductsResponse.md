# GetProductsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**products** | [**List[Product]**](Product.md) | Container for one or more products:  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.get_products_response import GetProductsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetProductsResponse from a JSON string
get_products_response_instance = GetProductsResponse.from_json(json)
# print the JSON string representation of the object
print(GetProductsResponse.to_json())

# convert the object into a dict
get_products_response_dict = get_products_response_instance.to_dict()
# create an instance of GetProductsResponse from a dict
get_products_response_from_dict = GetProductsResponse.from_dict(get_products_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


