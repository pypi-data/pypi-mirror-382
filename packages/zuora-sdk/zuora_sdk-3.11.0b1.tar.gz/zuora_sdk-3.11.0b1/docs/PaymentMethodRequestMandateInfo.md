# PaymentMethodRequestMandateInfo

The mandate information for the Credit Card, Credit Card Reference Transaction, ACH, or Bank Transfer payment method.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mandate_id** | **str** | The mandate ID.   When creating an ACH payment method, if you need to pass in tokenized information, use the &#x60;mandateId&#x60; instead of &#x60;tokenId&#x60; field. | [optional] 
**mandate_reason** | **str** | The reason of the mandate from the gateway side.  | [optional] 
**mandate_status** | **str** | The status of the mandate from the gateway side.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_request_mandate_info import PaymentMethodRequestMandateInfo

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodRequestMandateInfo from a JSON string
payment_method_request_mandate_info_instance = PaymentMethodRequestMandateInfo.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodRequestMandateInfo.to_json())

# convert the object into a dict
payment_method_request_mandate_info_dict = payment_method_request_mandate_info_instance.to_dict()
# create an instance of PaymentMethodRequestMandateInfo from a dict
payment_method_request_mandate_info_from_dict = PaymentMethodRequestMandateInfo.from_dict(payment_method_request_mandate_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


