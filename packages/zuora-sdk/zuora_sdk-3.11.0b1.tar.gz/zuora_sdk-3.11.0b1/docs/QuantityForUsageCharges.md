# QuantityForUsageCharges


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_id** | **str** | The ID of the subscription charge.  | [optional] 
**quantity** | **float** | The quantity of the subscription charge.  | [optional] 

## Example

```python
from zuora_sdk.models.quantity_for_usage_charges import QuantityForUsageCharges

# TODO update the JSON string below
json = "{}"
# create an instance of QuantityForUsageCharges from a JSON string
quantity_for_usage_charges_instance = QuantityForUsageCharges.from_json(json)
# print the JSON string representation of the object
print(QuantityForUsageCharges.to_json())

# convert the object into a dict
quantity_for_usage_charges_dict = quantity_for_usage_charges_instance.to_dict()
# create an instance of QuantityForUsageCharges from a dict
quantity_for_usage_charges_from_dict = QuantityForUsageCharges.from_dict(quantity_for_usage_charges_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


