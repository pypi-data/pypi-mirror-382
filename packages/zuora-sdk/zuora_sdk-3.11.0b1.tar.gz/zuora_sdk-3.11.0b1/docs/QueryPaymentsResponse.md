# QueryPaymentsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPayment]**](ExpandedPayment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_payments_response import QueryPaymentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPaymentsResponse from a JSON string
query_payments_response_instance = QueryPaymentsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPaymentsResponse.to_json())

# convert the object into a dict
query_payments_response_dict = query_payments_response_instance.to_dict()
# create an instance of QueryPaymentsResponse from a dict
query_payments_response_from_dict = QueryPaymentsResponse.from_dict(query_payments_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


