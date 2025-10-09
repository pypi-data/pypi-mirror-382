# GetCustomExchangeRatesDataType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_date** | [**ListOfExchangeRates**](ListOfExchangeRates.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_custom_exchange_rates_data_type import GetCustomExchangeRatesDataType

# TODO update the JSON string below
json = "{}"
# create an instance of GetCustomExchangeRatesDataType from a JSON string
get_custom_exchange_rates_data_type_instance = GetCustomExchangeRatesDataType.from_json(json)
# print the JSON string representation of the object
print(GetCustomExchangeRatesDataType.to_json())

# convert the object into a dict
get_custom_exchange_rates_data_type_dict = get_custom_exchange_rates_data_type_instance.to_dict()
# create an instance of GetCustomExchangeRatesDataType from a dict
get_custom_exchange_rates_data_type_from_dict = GetCustomExchangeRatesDataType.from_dict(get_custom_exchange_rates_data_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


