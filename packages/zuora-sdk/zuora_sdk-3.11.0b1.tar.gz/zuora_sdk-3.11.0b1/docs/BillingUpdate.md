# BillingUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing_period_alignment** | [**BillingPeriodAlignment**](BillingPeriodAlignment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.billing_update import BillingUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of BillingUpdate from a JSON string
billing_update_instance = BillingUpdate.from_json(json)
# print the JSON string representation of the object
print(BillingUpdate.to_json())

# convert the object into a dict
billing_update_dict = billing_update_instance.to_dict()
# create an instance of BillingUpdate from a dict
billing_update_from_dict = BillingUpdate.from_dict(billing_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


