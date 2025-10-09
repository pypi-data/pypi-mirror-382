# SubscriptionData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields.  | [optional] 
**invoice_separately** | **bool** | Specifies whether the subscription appears on a separate invoice when Zuora generates invoices. | [optional] 
**notes** | **str** | Notes about the subscription. These notes are only visible to Zuora users.  | [optional] 
**rate_plans** | [**List[RatePlan]**](RatePlan.md) |  | [optional] 
**start_date** | **date** |  | [optional] 
**subscription_number** | **str** | Subscription number of the subscription to create, for example, A-S00000001.   If you do not set this field, Zuora will generate a subscription number. | [optional] 
**terms** | [**TermInfo**](TermInfo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.subscription_data import SubscriptionData

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionData from a JSON string
subscription_data_instance = SubscriptionData.from_json(json)
# print the JSON string representation of the object
print(SubscriptionData.to_json())

# convert the object into a dict
subscription_data_dict = subscription_data_instance.to_dict()
# create an instance of SubscriptionData from a dict
subscription_data_from_dict = SubscriptionData.from_dict(subscription_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


