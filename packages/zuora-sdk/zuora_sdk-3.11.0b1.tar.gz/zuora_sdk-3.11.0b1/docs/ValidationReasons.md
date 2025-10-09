# ValidationReasons


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**field_name** | **str** | The name of the invalid field | [optional] 
**title** | **str** | A description why that field is invalid | [optional] 

## Example

```python
from zuora_sdk.models.validation_reasons import ValidationReasons

# TODO update the JSON string below
json = "{}"
# create an instance of ValidationReasons from a JSON string
validation_reasons_instance = ValidationReasons.from_json(json)
# print the JSON string representation of the object
print(ValidationReasons.to_json())

# convert the object into a dict
validation_reasons_dict = validation_reasons_instance.to_dict()
# create an instance of ValidationReasons from a dict
validation_reasons_from_dict = ValidationReasons.from_dict(validation_reasons_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


