# EndConditions

Specifies when a charge becomes inactive. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**end_date_condition** | [**EndDateCondition**](EndDateCondition.md) |  | [optional] 
**end_date_policy** | [**EndDatePolicy**](EndDatePolicy.md) |  | [optional] 
**specific_end_date** | **date** | Date in YYYY-MM-DD format. Only applicable if the value of the &#x60;endDateCondition&#x60; field is &#x60;Specific_End_Date&#x60;.  | [optional] 
**up_to_periods** | **int** | Duration of the charge in billing periods, days, weeks, months, or years, depending on the value of the &#x60;upToPeriodsType&#x60; field. Only applicable if the value of the &#x60;endDateCondition&#x60; field is &#x60;Fixed_Period&#x60;.  | [optional] 
**up_to_periods_type** | [**UpToPeriodsType**](UpToPeriodsType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.end_conditions import EndConditions

# TODO update the JSON string below
json = "{}"
# create an instance of EndConditions from a JSON string
end_conditions_instance = EndConditions.from_json(json)
# print the JSON string representation of the object
print(EndConditions.to_json())

# convert the object into a dict
end_conditions_dict = end_conditions_instance.to_dict()
# create an instance of EndConditions from a dict
end_conditions_from_dict = EndConditions.from_dict(end_conditions_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


