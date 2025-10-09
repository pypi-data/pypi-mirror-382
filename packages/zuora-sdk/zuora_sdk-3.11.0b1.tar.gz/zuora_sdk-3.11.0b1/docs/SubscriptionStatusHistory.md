# SubscriptionStatusHistory


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**end_date** | **date** | The effective end date of the status history. | [optional] 
**start_date** | **date** | The effective start date of the status history. | [optional] 
**status** | **str** | The status of the subscription.  Values are:  * &#x60;Pending Activation&#x60; * &#x60;Pending Acceptance&#x60; * &#x60;Active&#x60; * &#x60;Cancelled&#x60; * &#x60;Suspended&#x60; * &#x60;OutOfTerm&#x60;  | [optional] 

## Example

```python
from zuora_sdk.models.subscription_status_history import SubscriptionStatusHistory

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionStatusHistory from a JSON string
subscription_status_history_instance = SubscriptionStatusHistory.from_json(json)
# print the JSON string representation of the object
print(SubscriptionStatusHistory.to_json())

# convert the object into a dict
subscription_status_history_dict = subscription_status_history_instance.to_dict()
# create an instance of SubscriptionStatusHistory from a dict
subscription_status_history_from_dict = SubscriptionStatusHistory.from_dict(subscription_status_history_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


