# TriggerDate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**TriggerDateName**](TriggerDateName.md) |  | [optional] 
**trigger_date** | **date** | Trigger date in YYYY-MM-DD format.  | [optional] 

## Example

```python
from zuora_sdk.models.trigger_date import TriggerDate

# TODO update the JSON string below
json = "{}"
# create an instance of TriggerDate from a JSON string
trigger_date_instance = TriggerDate.from_json(json)
# print the JSON string representation of the object
print(TriggerDate.to_json())

# convert the object into a dict
trigger_date_dict = trigger_date_instance.to_dict()
# create an instance of TriggerDate from a dict
trigger_date_from_dict = TriggerDate.from_dict(trigger_date_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


