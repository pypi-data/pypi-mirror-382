# WriteOffOptions

Container for the write-off information to create credit memo.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** | Comments about the credit memo which is created as a result of the write off. | [optional] 
**memo_date** | **str** | The date when the credit memo takes effect. | [optional] 
**reason_code** | **str** | A code identifying the reason for the credit memo. | [optional] 
**tax_auto_calculation** | **bool** | Whether to automatically calculate taxes in the credit memo. | [optional] 

## Example

```python
from zuora_sdk.models.write_off_options import WriteOffOptions

# TODO update the JSON string below
json = "{}"
# create an instance of WriteOffOptions from a JSON string
write_off_options_instance = WriteOffOptions.from_json(json)
# print the JSON string representation of the object
print(WriteOffOptions.to_json())

# convert the object into a dict
write_off_options_dict = write_off_options_instance.to_dict()
# create an instance of WriteOffOptions from a dict
write_off_options_from_dict = WriteOffOptions.from_dict(write_off_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


