# DeleteSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Returns &#x60;true&#x60; if the request is processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.delete_subscription_response import DeleteSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteSubscriptionResponse from a JSON string
delete_subscription_response_instance = DeleteSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(DeleteSubscriptionResponse.to_json())

# convert the object into a dict
delete_subscription_response_dict = delete_subscription_response_instance.to_dict()
# create an instance of DeleteSubscriptionResponse from a dict
delete_subscription_response_from_dict = DeleteSubscriptionResponse.from_dict(delete_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


