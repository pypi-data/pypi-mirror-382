# PaymentMethodUpdaterInstancesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Indicates whether the call is successful. | [optional] 
**updaters** | [**List[PaymentMethodUpdaterInstanceResponse]**](PaymentMethodUpdaterInstanceResponse.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_updater_instances_response import PaymentMethodUpdaterInstancesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodUpdaterInstancesResponse from a JSON string
payment_method_updater_instances_response_instance = PaymentMethodUpdaterInstancesResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodUpdaterInstancesResponse.to_json())

# convert the object into a dict
payment_method_updater_instances_response_dict = payment_method_updater_instances_response_instance.to_dict()
# create an instance of PaymentMethodUpdaterInstancesResponse from a dict
payment_method_updater_instances_response_from_dict = PaymentMethodUpdaterInstancesResponse.from_dict(payment_method_updater_instances_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


