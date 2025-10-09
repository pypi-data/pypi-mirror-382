# ListOfExchangeRates

Container for exchange rate information on a given date. The field name is the date in `yyyy-mm-dd` format, for example, 2016-01-15.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**currency** | **str** | The exchange rate on the **providerExchangeRateDate**. The field name is the ISO currency code of the currency, for example, &#x60;EUR&#x60;.   There may be more than one currency returned for a given **providerExchangeRateDate**. If the rate for a certain currency is not available on the **providerExchangeRateDate**, the currency is not returned in the response. | [optional] 
**provider_exchange_rate_date** | **date** | The date of the exchange rate used. The date is in &#x60;yyyy-mm-dd&#x60; format.   Corresponds to the value specified in the Provider Exchange Rate Date column in the Import Foreign Exchange Rates template when you uploaded the rates through the Mass Updater. | [optional] 

## Example

```python
from zuora_sdk.models.list_of_exchange_rates import ListOfExchangeRates

# TODO update the JSON string below
json = "{}"
# create an instance of ListOfExchangeRates from a JSON string
list_of_exchange_rates_instance = ListOfExchangeRates.from_json(json)
# print the JSON string representation of the object
print(ListOfExchangeRates.to_json())

# convert the object into a dict
list_of_exchange_rates_dict = list_of_exchange_rates_instance.to_dict()
# create an instance of ListOfExchangeRates from a dict
list_of_exchange_rates_from_dict = ListOfExchangeRates.from_dict(list_of_exchange_rates_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


