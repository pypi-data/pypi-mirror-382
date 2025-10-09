# BillingAdjustmentExclusion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_numbers** | **List[str]** | The charge numbers to be excluded from adjustment on the specified delivery date. | [optional] 
**delivery_date** | **date** | The date on which the adjustment has to be excluded, in &#x60;yyyy-mm-dd&#x60; format. | [optional] 

## Example

```python
from zuora_sdk.models.billing_adjustment_exclusion import BillingAdjustmentExclusion

# TODO update the JSON string below
json = "{}"
# create an instance of BillingAdjustmentExclusion from a JSON string
billing_adjustment_exclusion_instance = BillingAdjustmentExclusion.from_json(json)
# print the JSON string representation of the object
print(BillingAdjustmentExclusion.to_json())

# convert the object into a dict
billing_adjustment_exclusion_dict = billing_adjustment_exclusion_instance.to_dict()
# create an instance of BillingAdjustmentExclusion from a dict
billing_adjustment_exclusion_from_dict = BillingAdjustmentExclusion.from_dict(billing_adjustment_exclusion_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


