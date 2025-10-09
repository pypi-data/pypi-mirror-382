# CreatePaymentMethodUpdaterBatchResponseReasons


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | Error code.  | [optional] 
**message** | **str** | Error message.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_updater_batch_response_reasons import CreatePaymentMethodUpdaterBatchResponseReasons

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodUpdaterBatchResponseReasons from a JSON string
create_payment_method_updater_batch_response_reasons_instance = CreatePaymentMethodUpdaterBatchResponseReasons.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodUpdaterBatchResponseReasons.to_json())

# convert the object into a dict
create_payment_method_updater_batch_response_reasons_dict = create_payment_method_updater_batch_response_reasons_instance.to_dict()
# create an instance of CreatePaymentMethodUpdaterBatchResponseReasons from a dict
create_payment_method_updater_batch_response_reasons_from_dict = CreatePaymentMethodUpdaterBatchResponseReasons.from_dict(create_payment_method_updater_batch_response_reasons_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


