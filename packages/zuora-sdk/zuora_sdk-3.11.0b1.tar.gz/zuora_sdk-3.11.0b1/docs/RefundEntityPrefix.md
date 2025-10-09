# RefundEntityPrefix

Container for the prefix and starting number of refunds. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prefix** | **str** | The prefix of refunds.  | [optional] 
**start_number** | **int** | The starting number of refunds.  | [optional] 

## Example

```python
from zuora_sdk.models.refund_entity_prefix import RefundEntityPrefix

# TODO update the JSON string below
json = "{}"
# create an instance of RefundEntityPrefix from a JSON string
refund_entity_prefix_instance = RefundEntityPrefix.from_json(json)
# print the JSON string representation of the object
print(RefundEntityPrefix.to_json())

# convert the object into a dict
refund_entity_prefix_dict = refund_entity_prefix_instance.to_dict()
# create an instance of RefundEntityPrefix from a dict
refund_entity_prefix_from_dict = RefundEntityPrefix.from_dict(refund_entity_prefix_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


