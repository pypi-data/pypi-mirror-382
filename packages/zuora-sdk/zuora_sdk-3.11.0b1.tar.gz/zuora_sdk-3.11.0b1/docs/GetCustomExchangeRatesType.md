# GetCustomExchangeRatesType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**inverse** | **bool** | - If &#x60;true&#x60;, the exchange rate in the response is an inverse exchange rate.  - If &#x60;false&#x60;, the exchange rate in the response is not an inverse exchange rate.  The value is determined by the **Use inverse rate** checkbox in your Zuora Finance Manage Currency Conversion settings. | [optional] 
**rate_set_name** | **str** | The name of the rate set configured in the Finance Manage Currency Conversion settings for Multi-Org feature. | [optional] 
**rates** | [**List[GetCustomExchangeRatesDataType]**](GetCustomExchangeRatesDataType.md) | Container for exchange rate data. Contains a set of fields that provide exchange rate data for each day between the specified &#x60;startDate&#x60; and &#x60;endDate&#x60; (inclusive).  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_custom_exchange_rates_type import GetCustomExchangeRatesType

# TODO update the JSON string below
json = "{}"
# create an instance of GetCustomExchangeRatesType from a JSON string
get_custom_exchange_rates_type_instance = GetCustomExchangeRatesType.from_json(json)
# print the JSON string representation of the object
print(GetCustomExchangeRatesType.to_json())

# convert the object into a dict
get_custom_exchange_rates_type_dict = get_custom_exchange_rates_type_instance.to_dict()
# create an instance of GetCustomExchangeRatesType from a dict
get_custom_exchange_rates_type_from_dict = GetCustomExchangeRatesType.from_dict(get_custom_exchange_rates_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


