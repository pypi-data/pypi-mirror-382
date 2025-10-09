# PaymentVolumeSummaryRecord

A volume summary record. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **int** | The count of failed payments of above &#x60;paymentGatewayType&#x60; and &#x60;paymentMethodType&#x60;. | [optional] 
**payment_gateway_type** | **str** | The payment gateway type.  | [optional] 
**payment_method_type** | **str** | The payment method type.  | [optional] 
**success** | **int** | The count of successful payments of above &#x60;paymentGatewayType&#x60; and &#x60;paymentMethodType&#x60;. | [optional] 
**total** | **int** | The count of total payments of above &#x60;paymentGatewayType&#x60; and &#x60;paymentMethodType&#x60;.       | [optional] 

## Example

```python
from zuora_sdk.models.payment_volume_summary_record import PaymentVolumeSummaryRecord

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentVolumeSummaryRecord from a JSON string
payment_volume_summary_record_instance = PaymentVolumeSummaryRecord.from_json(json)
# print the JSON string representation of the object
print(PaymentVolumeSummaryRecord.to_json())

# convert the object into a dict
payment_volume_summary_record_dict = payment_volume_summary_record_instance.to_dict()
# create an instance of PaymentVolumeSummaryRecord from a dict
payment_volume_summary_record_from_dict = PaymentVolumeSummaryRecord.from_dict(payment_volume_summary_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


