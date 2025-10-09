# SubscriptionObjectNSFields

Container for Subscription fields provided by the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the subscription&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**project__ns** | **str** | The NetSuite project that the subscription was created from. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sales_order__ns** | **str** | The NetSuite sales order than the subscription was created from. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the subscription was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 

## Example

```python
from zuora_sdk.models.subscription_object_ns_fields import SubscriptionObjectNSFields

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionObjectNSFields from a JSON string
subscription_object_ns_fields_instance = SubscriptionObjectNSFields.from_json(json)
# print the JSON string representation of the object
print(SubscriptionObjectNSFields.to_json())

# convert the object into a dict
subscription_object_ns_fields_dict = subscription_object_ns_fields_instance.to_dict()
# create an instance of SubscriptionObjectNSFields from a dict
subscription_object_ns_fields_from_dict = SubscriptionObjectNSFields.from_dict(subscription_object_ns_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


