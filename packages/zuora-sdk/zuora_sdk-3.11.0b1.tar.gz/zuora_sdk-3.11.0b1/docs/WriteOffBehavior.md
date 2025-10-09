# WriteOffBehavior

The financial information of the credit memo items generated to write off the invoice balance.    **Note:**    - All the credit memo items that are used to write off the invoice will be applied with the same financial information.   - Credit memo items generated from the unconsumed services of the canceled subscription will not be applied with the finance information specified here.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**finance_information** | [**WriteOffBehaviorFinanceInformation**](WriteOffBehaviorFinanceInformation.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.write_off_behavior import WriteOffBehavior

# TODO update the JSON string below
json = "{}"
# create an instance of WriteOffBehavior from a JSON string
write_off_behavior_instance = WriteOffBehavior.from_json(json)
# print the JSON string representation of the object
print(WriteOffBehavior.to_json())

# convert the object into a dict
write_off_behavior_dict = write_off_behavior_instance.to_dict()
# create an instance of WriteOffBehavior from a dict
write_off_behavior_from_dict = WriteOffBehavior.from_dict(write_off_behavior_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


