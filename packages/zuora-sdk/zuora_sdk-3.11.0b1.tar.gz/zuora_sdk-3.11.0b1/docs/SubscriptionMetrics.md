# SubscriptionMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subscription_number** | **str** | The number for the subscription. | [optional] 
**contracted_mrr** | **float** | Monthly recurring revenue of the subscription. | [optional] 
**contracted_net_mrr** | **float** | Monthly recurring revenue of the subscription rate plan inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts. | [optional] 
**as_of_day_gross_mrr** | **float** | Monthly recurring revenue of the subscription rate plan exclusive of any discounts applicable as of specified day. | [optional] 
**as_of_day_net_mrr** | **float** | Monthly recurring revenue of the subscription rate plan inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts as of specified day. | [optional] 
**total_contracted_value** | **float** | Total contract value of the subscription. | [optional] 
**net_total_contracted_value** | **float** | Total contract value of the subscription rate plan inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts. | [optional] 

## Example

```python
from zuora_sdk.models.subscription_metrics import SubscriptionMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionMetrics from a JSON string
subscription_metrics_instance = SubscriptionMetrics.from_json(json)
# print the JSON string representation of the object
print(SubscriptionMetrics.to_json())

# convert the object into a dict
subscription_metrics_dict = subscription_metrics_instance.to_dict()
# create an instance of SubscriptionMetrics from a dict
subscription_metrics_from_dict = SubscriptionMetrics.from_dict(subscription_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


