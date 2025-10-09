# ValidationErrors


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reasons** | [**List[ValidationReasons]**](ValidationReasons.md) | The list of reasons that the request was unsuccessful | [optional] 
**success** | **bool** | Returns &#x60;false&#x60; if the request was not successful. | [optional] 

## Example

```python
from zuora_sdk.models.validation_errors import ValidationErrors

# TODO update the JSON string below
json = "{}"
# create an instance of ValidationErrors from a JSON string
validation_errors_instance = ValidationErrors.from_json(json)
# print the JSON string representation of the object
print(ValidationErrors.to_json())

# convert the object into a dict
validation_errors_dict = validation_errors_instance.to_dict()
# create an instance of ValidationErrors from a dict
validation_errors_from_dict = ValidationErrors.from_dict(validation_errors_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


