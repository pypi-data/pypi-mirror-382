# ChargeMetrics

Container for charge metrics. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dmrr** | **float** | Change in monthly recurring revenue.  | [optional] 
**dtcv** | **float** | Change in total contract value.  | [optional] 
**mrr** | **float** | Monthly recurring revenue.  | [optional] 
**number** | **str** | The charge number of the subscription. Only available for update subscription. | [optional] 
**origin_rate_plan_id** | **str** | The origin rate plan ID. Only available for update subscription.  | [optional] 
**original_id** | **str** | The original rate plan charge ID. Only available for update subscription.  | [optional] 
**product_rate_plan_charge_id** | **str** | The product rate plan charge ID.  | [optional] 
**product_rate_plan_id** | **str** | The product rate plan ID.  | [optional] 
**tcv** | **float** | Total contract value.  | [optional] 

## Example

```python
from zuora_sdk.models.charge_metrics import ChargeMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of ChargeMetrics from a JSON string
charge_metrics_instance = ChargeMetrics.from_json(json)
# print the JSON string representation of the object
print(ChargeMetrics.to_json())

# convert the object into a dict
charge_metrics_dict = charge_metrics_instance.to_dict()
# create an instance of ChargeMetrics from a dict
charge_metrics_from_dict = ChargeMetrics.from_dict(charge_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


