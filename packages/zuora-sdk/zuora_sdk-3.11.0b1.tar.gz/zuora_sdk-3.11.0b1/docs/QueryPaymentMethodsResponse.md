# QueryPaymentMethodsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPaymentMethod]**](ExpandedPaymentMethod.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_payment_methods_response import QueryPaymentMethodsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPaymentMethodsResponse from a JSON string
query_payment_methods_response_instance = QueryPaymentMethodsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPaymentMethodsResponse.to_json())

# convert the object into a dict
query_payment_methods_response_dict = query_payment_methods_response_instance.to_dict()
# create an instance of QueryPaymentMethodsResponse from a dict
query_payment_methods_response_from_dict = QueryPaymentMethodsResponse.from_dict(query_payment_methods_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


