# SubscriptionChangeLog

Represents the order information that will be returned in the GET call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subscription_number** | **str** | Subscription number. | [optional] 
**account_number** | **str** | Account number. | [optional] 
**invoice_owner_account_number** | **str** | Invoice owner account number of the subscription. | [optional] 
**currency** | **str** | The currency of the subscription. | [optional] 
**order_number** | **str** | The order number of the order which created this subscription. | [optional] 
**version** | **str** | The version of the subscription. | [optional] 
**changed_time** | **str** | The create time of the subscription. | [optional] 
**type** | **str** | The type of the subscription. | [optional] 
**external_subscription_id** | **str** | External subscription id. | [optional] 
**subscription_start_date** | **str** | Start date of the subscription. | [optional] 
**subscription_end_date** | **str** | End date of the subscription. | [optional] 
**term_start_date** | **str** | Term start date of the subscription. | [optional] 
**term_end_date** | **str** | Term end date of the subscription. | [optional] 
**rate_plans** | [**List[RatePlanChangeLog]**](RatePlanChangeLog.md) | Represents the rate plans in this subscription. | [optional] 
**fields** | [**List[ChangeLogField]**](ChangeLogField.md) | Represents the fields which the value is changed for this charge. | [optional] 

## Example

```python
from zuora_sdk.models.subscription_change_log import SubscriptionChangeLog

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionChangeLog from a JSON string
subscription_change_log_instance = SubscriptionChangeLog.from_json(json)
# print the JSON string representation of the object
print(SubscriptionChangeLog.to_json())

# convert the object into a dict
subscription_change_log_dict = subscription_change_log_instance.to_dict()
# create an instance of SubscriptionChangeLog from a dict
subscription_change_log_from_dict = SubscriptionChangeLog.from_dict(subscription_change_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


