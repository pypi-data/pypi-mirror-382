# PaymentMethodRequestProcessingOptions

The processing options for the payment method.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**check_duplicated** | **bool** | the flag indicates if need to do the duplication check | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_request_processing_options import PaymentMethodRequestProcessingOptions

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodRequestProcessingOptions from a JSON string
payment_method_request_processing_options_instance = PaymentMethodRequestProcessingOptions.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodRequestProcessingOptions.to_json())

# convert the object into a dict
payment_method_request_processing_options_dict = payment_method_request_processing_options_instance.to_dict()
# create an instance of PaymentMethodRequestProcessingOptions from a dict
payment_method_request_processing_options_from_dict = PaymentMethodRequestProcessingOptions.from_dict(payment_method_request_processing_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


