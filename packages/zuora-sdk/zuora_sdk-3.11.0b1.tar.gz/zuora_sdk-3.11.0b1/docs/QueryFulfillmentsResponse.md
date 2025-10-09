# QueryFulfillmentsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedFulfillment]**](ExpandedFulfillment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_fulfillments_response import QueryFulfillmentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryFulfillmentsResponse from a JSON string
query_fulfillments_response_instance = QueryFulfillmentsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryFulfillmentsResponse.to_json())

# convert the object into a dict
query_fulfillments_response_dict = query_fulfillments_response_instance.to_dict()
# create an instance of QueryFulfillmentsResponse from a dict
query_fulfillments_response_from_dict = QueryFulfillmentsResponse.from_dict(query_fulfillments_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


