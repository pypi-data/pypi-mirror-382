# PreviewChargeMetricsTax


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**discount** | **float** | Total tax amount of all discount charges which are applied to one specific recurring charge. This value is calculated from the rating results for the latest subscription version in the order. | [optional] 
**discount_delta** | **float** | Delta discount TAX value between the base and the latest subscription version in the order for the specific recurring charge. | [optional] 
**regular** | **float** |  | [optional] 
**regular_delta** | **float** | Delta tax value between the base and the latest subscription version in the order. | [optional] 

## Example

```python
from zuora_sdk.models.preview_charge_metrics_tax import PreviewChargeMetricsTax

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewChargeMetricsTax from a JSON string
preview_charge_metrics_tax_instance = PreviewChargeMetricsTax.from_json(json)
# print the JSON string representation of the object
print(PreviewChargeMetricsTax.to_json())

# convert the object into a dict
preview_charge_metrics_tax_dict = preview_charge_metrics_tax_instance.to_dict()
# create an instance of PreviewChargeMetricsTax from a dict
preview_charge_metrics_tax_from_dict = PreviewChargeMetricsTax.from_dict(preview_charge_metrics_tax_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


