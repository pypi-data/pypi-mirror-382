# ExpandedRamp


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**number** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**subscription_numbers** | **str** |  | [optional] 
**charge_numbers** | **str** |  | [optional] 
**order_id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**gross_tcb** | **float** |  | [optional] 
**net_tcb** | **float** |  | [optional] 
**discount_tcb** | **float** |  | [optional] 
**gross_tcv** | **float** |  | [optional] 
**net_tcv** | **float** |  | [optional] 
**discount_tcv** | **float** |  | [optional] 
**metrics_processing_status** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_ramp import ExpandedRamp

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRamp from a JSON string
expanded_ramp_instance = ExpandedRamp.from_json(json)
# print the JSON string representation of the object
print(ExpandedRamp.to_json())

# convert the object into a dict
expanded_ramp_dict = expanded_ramp_instance.to_dict()
# create an instance of ExpandedRamp from a dict
expanded_ramp_from_dict = ExpandedRamp.from_dict(expanded_ramp_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


