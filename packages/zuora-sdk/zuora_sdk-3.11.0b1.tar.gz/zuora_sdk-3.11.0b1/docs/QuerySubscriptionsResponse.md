# QuerySubscriptionsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedSubscription]**](ExpandedSubscription.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_subscriptions_response import QuerySubscriptionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QuerySubscriptionsResponse from a JSON string
query_subscriptions_response_instance = QuerySubscriptionsResponse.from_json(json)
# print the JSON string representation of the object
print(QuerySubscriptionsResponse.to_json())

# convert the object into a dict
query_subscriptions_response_dict = query_subscriptions_response_instance.to_dict()
# create an instance of QuerySubscriptionsResponse from a dict
query_subscriptions_response_from_dict = QuerySubscriptionsResponse.from_dict(query_subscriptions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


