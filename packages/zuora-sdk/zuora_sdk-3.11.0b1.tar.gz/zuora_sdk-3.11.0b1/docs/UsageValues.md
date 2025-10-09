# UsageValues


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task_count** | **int** | The amount of task runs that have been used.  | [optional] 

## Example

```python
from zuora_sdk.models.usage_values import UsageValues

# TODO update the JSON string below
json = "{}"
# create an instance of UsageValues from a JSON string
usage_values_instance = UsageValues.from_json(json)
# print the JSON string representation of the object
print(UsageValues.to_json())

# convert the object into a dict
usage_values_dict = usage_values_instance.to_dict()
# create an instance of UsageValues from a dict
usage_values_from_dict = UsageValues.from_dict(usage_values_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


