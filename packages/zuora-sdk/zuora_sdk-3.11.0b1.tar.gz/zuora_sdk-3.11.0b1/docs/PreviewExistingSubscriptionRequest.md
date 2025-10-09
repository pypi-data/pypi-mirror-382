# PreviewExistingSubscriptionRequest

Preview the existing subscription by subscription ID or number. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**preview_start_date** | [**PreviewStartDate**](PreviewStartDate.md) |  | [optional] 
**preview_through_date** | [**PreviewThroughDate**](PreviewThroughDate.md) |  | 
**quantity_for_usage_charges** | [**List[QuantityForUsageCharges]**](QuantityForUsageCharges.md) | Container for usage charges.  | [optional] 

## Example

```python
from zuora_sdk.models.preview_existing_subscription_request import PreviewExistingSubscriptionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewExistingSubscriptionRequest from a JSON string
preview_existing_subscription_request_instance = PreviewExistingSubscriptionRequest.from_json(json)
# print the JSON string representation of the object
print(PreviewExistingSubscriptionRequest.to_json())

# convert the object into a dict
preview_existing_subscription_request_dict = preview_existing_subscription_request_instance.to_dict()
# create an instance of PreviewExistingSubscriptionRequest from a dict
preview_existing_subscription_request_from_dict = PreviewExistingSubscriptionRequest.from_dict(preview_existing_subscription_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


