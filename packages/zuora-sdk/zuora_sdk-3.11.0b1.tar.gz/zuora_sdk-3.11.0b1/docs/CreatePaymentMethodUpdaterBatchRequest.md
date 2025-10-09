# CreatePaymentMethodUpdaterBatchRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing_cycle_day** | **int** | The billing cycle day. The allowed value is an integer in the range of 1 - 31.   The payment methods from accounts where the billing cycle day is the specified value in this field will be included in the updates. | 
**updater_account_id** | **str** | The ID (UUID) of the PMU account. This field must be a string of 32 characters consisting of digits and letters a - f. | 

## Example

```python
from zuora_sdk.models.create_payment_method_updater_batch_request import CreatePaymentMethodUpdaterBatchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodUpdaterBatchRequest from a JSON string
create_payment_method_updater_batch_request_instance = CreatePaymentMethodUpdaterBatchRequest.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodUpdaterBatchRequest.to_json())

# convert the object into a dict
create_payment_method_updater_batch_request_dict = create_payment_method_updater_batch_request_instance.to_dict()
# create an instance of CreatePaymentMethodUpdaterBatchRequest from a dict
create_payment_method_updater_batch_request_from_dict = CreatePaymentMethodUpdaterBatchRequest.from_dict(create_payment_method_updater_batch_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


