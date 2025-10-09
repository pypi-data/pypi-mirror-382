# CreatePaymentMethodUpdaterBatchResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The ID of the running process when the exception occurs. This field is available only if the &#x60;success&#x60; field is &#x60;false&#x60;. | [optional] 
**reasons** | [**List[CreatePaymentMethodUpdaterBatchResponseReasons]**](CreatePaymentMethodUpdaterBatchResponseReasons.md) | The container of the error code and message. This field is available only if the &#x60;success&#x60; field is &#x60;false&#x60;. | [optional] 
**request_id** | **str** | The ID of the request. This field is available only if the &#x60;success&#x60; field is &#x60;false&#x60; | [optional] 
**success** | **bool** | Indicates whether the request to create a PMU batch is sent successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_updater_batch_response import CreatePaymentMethodUpdaterBatchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodUpdaterBatchResponse from a JSON string
create_payment_method_updater_batch_response_instance = CreatePaymentMethodUpdaterBatchResponse.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodUpdaterBatchResponse.to_json())

# convert the object into a dict
create_payment_method_updater_batch_response_dict = create_payment_method_updater_batch_response_instance.to_dict()
# create an instance of CreatePaymentMethodUpdaterBatchResponse from a dict
create_payment_method_updater_batch_response_from_dict = CreatePaymentMethodUpdaterBatchResponse.from_dict(create_payment_method_updater_batch_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


