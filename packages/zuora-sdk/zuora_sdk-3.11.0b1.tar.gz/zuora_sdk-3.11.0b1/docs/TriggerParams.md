# TriggerParams

Specifies when a charge becomes active. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**specific_trigger_date** | **date** | Date in YYYY-MM-DD format. Only applicable if the value of the &#x60;triggerEvent&#x60; field is &#x60;SpecificDate&#x60;.   While this field is applicable, if this field is not set, your &#x60;CreateSubscription&#x60; order action creates a &#x60;Pending&#x60; order and a &#x60;Pending Acceptance&#x60; subscription. If at the same time the service activation date is required and not set, a &#x60;Pending Activation&#x60; subscription is created.  nWhile this field is applicable, if this field is not set, the following order actions create a &#x60;Pending&#x60; order but do not impact the subscription status. **Note**: This feature is in **Limited Availability**. If you want to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/).  * AddProduct  * UpdateProduct  * RemoveProduct  * RenewSubscription  * TermsAndConditions  | [optional] 
**trigger_event** | [**TriggerEvent**](TriggerEvent.md) |  | [optional] 
**start_date_policy** | [**StartDatePolicy**](StartDatePolicy.md) |  | [optional] 
**periods_after_charge_start** | **int** | Duration of the discount charge in days, weeks, months, or years, depending on the value of the &#x60;startPeriodsType&#x60; field. Only applicable if the value of the &#x60;startDatePolicy&#x60; field is &#x60;FixedPeriodAfterApplyToChargeStartDate&#x60;. **Note**: You must enable the [Enhanced Discounts](https://knowledgecenter.zuora.com/Zuora_Billing/Build_products_and_prices/Basic_concepts_and_terms/B_Charge_Models/D_Manage_Enhanced_Discount) feature to access this field.  | [optional] 
**start_periods_type** | [**StartPeriodsType**](StartPeriodsType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.trigger_params import TriggerParams

# TODO update the JSON string below
json = "{}"
# create an instance of TriggerParams from a JSON string
trigger_params_instance = TriggerParams.from_json(json)
# print the JSON string representation of the object
print(TriggerParams.to_json())

# convert the object into a dict
trigger_params_dict = trigger_params_instance.to_dict()
# create an instance of TriggerParams from a dict
trigger_params_from_dict = TriggerParams.from_dict(trigger_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


