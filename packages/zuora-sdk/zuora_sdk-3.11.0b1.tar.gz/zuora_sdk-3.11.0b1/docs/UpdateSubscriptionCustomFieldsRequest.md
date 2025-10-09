# UpdateSubscriptionCustomFieldsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Subscription object.  | [optional] 
**rate_plans** | [**List[UpdateSubscriptionRatePlanCustomFields]**](UpdateSubscriptionRatePlanCustomFields.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_subscription_custom_fields_request import UpdateSubscriptionCustomFieldsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateSubscriptionCustomFieldsRequest from a JSON string
update_subscription_custom_fields_request_instance = UpdateSubscriptionCustomFieldsRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateSubscriptionCustomFieldsRequest.to_json())

# convert the object into a dict
update_subscription_custom_fields_request_dict = update_subscription_custom_fields_request_instance.to_dict()
# create an instance of UpdateSubscriptionCustomFieldsRequest from a dict
update_subscription_custom_fields_request_from_dict = UpdateSubscriptionCustomFieldsRequest.from_dict(update_subscription_custom_fields_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


