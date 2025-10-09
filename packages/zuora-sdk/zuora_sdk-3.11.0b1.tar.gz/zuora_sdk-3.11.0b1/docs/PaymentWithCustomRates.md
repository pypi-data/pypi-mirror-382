# PaymentWithCustomRates


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**currency** | **str** | The currency code for either Reporting or Home currency.   **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;224.0&#x60; or later. | 
**custom_fx_rate** | **decimal.Decimal** | The Custom FX conversion rate between Home/Reporting and Transactional currency items.   **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;224.0&#x60; or later. | 
**rate_date** | **str** | The date on which a particular currency rate is fixed or obtained on.   **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;224.0&#x60; or later. | [optional] 

## Example

```python
from zuora_sdk.models.payment_with_custom_rates import PaymentWithCustomRates

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentWithCustomRates from a JSON string
payment_with_custom_rates_instance = PaymentWithCustomRates.from_json(json)
# print the JSON string representation of the object
print(PaymentWithCustomRates.to_json())

# convert the object into a dict
payment_with_custom_rates_dict = payment_with_custom_rates_instance.to_dict()
# create an instance of PaymentWithCustomRates from a dict
payment_with_custom_rates_from_dict = PaymentWithCustomRates.from_dict(payment_with_custom_rates_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


