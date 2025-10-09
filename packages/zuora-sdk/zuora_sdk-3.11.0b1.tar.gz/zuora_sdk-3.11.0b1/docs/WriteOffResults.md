# WriteOffResults

Container for the write-off information of credit memo and apply information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error_message** | **str** | The error message about write off failed. | [optional] 
**transactions** | [**List[WriteOffResultTransaction]**](WriteOffResultTransaction.md) | The credit memo apply information. | [optional] 

## Example

```python
from zuora_sdk.models.write_off_results import WriteOffResults

# TODO update the JSON string below
json = "{}"
# create an instance of WriteOffResults from a JSON string
write_off_results_instance = WriteOffResults.from_json(json)
# print the JSON string representation of the object
print(WriteOffResults.to_json())

# convert the object into a dict
write_off_results_dict = write_off_results_instance.to_dict()
# create an instance of WriteOffResults from a dict
write_off_results_from_dict = WriteOffResults.from_dict(write_off_results_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


