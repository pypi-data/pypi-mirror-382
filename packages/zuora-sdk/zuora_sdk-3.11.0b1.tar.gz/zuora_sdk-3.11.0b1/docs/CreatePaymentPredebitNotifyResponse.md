# CreatePaymentPredebitNotifyResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_id** | **str** | The ID of the invoice for which the pre-debit notification is triggered. | [optional] 
**payment_method_id** | **str** | The id of the associated payment method. | [optional] 
**gateway_id** | **str** | The id of the associated payment gateway. | [optional] 
**gateway_type** | **str** | The gateway type used in this operation. Example - Adyen. | [optional] 
**gateway_version** | **str** | The version number of the gateway used. | [optional] 
**notification_reference_id** | **str** | The shopperNotificationReference value. | [optional] 
**second_notification_reference_id** | **str** | The additional second reference ID returned from the gateway. | [optional] 
**third_notification_reference_id** | **str** | The additional third reference ID returned from the gateway. | [optional] 
**extra_parameters** | **str** | The extra optional parameter returned from the gateway. | [optional] 
**success** | **bool** | Indicates whether the call succeeded. | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_predebit_notify_response import CreatePaymentPredebitNotifyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentPredebitNotifyResponse from a JSON string
create_payment_predebit_notify_response_instance = CreatePaymentPredebitNotifyResponse.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentPredebitNotifyResponse.to_json())

# convert the object into a dict
create_payment_predebit_notify_response_dict = create_payment_predebit_notify_response_instance.to_dict()
# create an instance of CreatePaymentPredebitNotifyResponse from a dict
create_payment_predebit_notify_response_from_dict = CreatePaymentPredebitNotifyResponse.from_dict(create_payment_predebit_notify_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


