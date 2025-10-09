# GetSubscriptionsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**subscriptions** | [**List[GetSubscriptionResponse]**](GetSubscriptionResponse.md) | Array of subscriptions.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_subscriptions_response import GetSubscriptionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetSubscriptionsResponse from a JSON string
get_subscriptions_response_instance = GetSubscriptionsResponse.from_json(json)
# print the JSON string representation of the object
print(GetSubscriptionsResponse.to_json())

# convert the object into a dict
get_subscriptions_response_dict = get_subscriptions_response_instance.to_dict()
# create an instance of GetSubscriptionsResponse from a dict
get_subscriptions_response_from_dict = GetSubscriptionsResponse.from_dict(get_subscriptions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


