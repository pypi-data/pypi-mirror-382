# PaymentEntityPrefix

Container for the prefix and starting number of payments. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prefix** | **str** | The prefix of payments.  | [optional] 
**start_number** | **int** | The starting number of payments.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_entity_prefix import PaymentEntityPrefix

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentEntityPrefix from a JSON string
payment_entity_prefix_instance = PaymentEntityPrefix.from_json(json)
# print the JSON string representation of the object
print(PaymentEntityPrefix.to_json())

# convert the object into a dict
payment_entity_prefix_dict = payment_entity_prefix_instance.to_dict()
# create an instance of PaymentEntityPrefix from a dict
payment_entity_prefix_from_dict = PaymentEntityPrefix.from_dict(payment_entity_prefix_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


