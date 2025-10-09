# PaymentMethodUpdaterInstanceResponse

Container for PMU instances available on your tenant. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**days_to_update_before_bcd** | **int** | The days prior to the Bill Cycle Day to start PMU service.  | [optional] 
**id** | **str** | The ID of the PMU instance.  | [optional] 
**is_active** | **bool** | &#x60;true&#x60; indicates that this PMU instance is active.  | [optional] 
**is_default** | **bool** | &#x60;true&#x60; indicates that it is the default PMU instance.  | [optional] 
**is_test** | **str** | &#x60;true&#x60; indicates that this PMU instance is for testing.  | [optional] 
**process_associated_gw_only** | **bool** | &#x60;true&#x60; indicates that only the payment methods for customer accounts that meet either of the following conditions are included in the updates:   - The default payment gateway of the customer account is set to an instance of the same type as &#x60;updaterGatewayType&#x60;.   - The default payment gateway of the customer account is not configured, but the default payment gateway of the tenant is set to an instance of the same type as &#x60;updaterGatewayType&#x60;.  &#x60;false&#x60; indicates that information of all payment methods is submitted. | [optional] 
**process_autopay_default_pm_only** | **bool** | &#x60;true&#x60; indicates that only the default payment methods for customer accounts with the AutoPay setting enabled are included in the updates.    &#x60;false&#x60; indicates that data of all payment methods for all customer accounts is submitted, regardless of whether AutoPay is enabled for the customer account or not. | [optional] 
**process_mastercard** | **bool** | &#x60;true&#x60; indicates that Mastercard data processing is supported.  | [optional] 
**process_visa** | **bool** | &#x60;true&#x60; indicates that Visa data processing is supported.  | [optional] 
**updater_gateway_type** | **str** | The payment gateway type of the PMU instance.  | [optional] 
**updater_name** | **str** | The name of the PMU instance.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_updater_instance_response import PaymentMethodUpdaterInstanceResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodUpdaterInstanceResponse from a JSON string
payment_method_updater_instance_response_instance = PaymentMethodUpdaterInstanceResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodUpdaterInstanceResponse.to_json())

# convert the object into a dict
payment_method_updater_instance_response_dict = payment_method_updater_instance_response_instance.to_dict()
# create an instance of PaymentMethodUpdaterInstanceResponse from a dict
payment_method_updater_instance_response_from_dict = PaymentMethodUpdaterInstanceResponse.from_dict(payment_method_updater_instance_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


