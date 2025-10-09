# CreatePaymentSchedulesResponse

Container of the payment schedules that are created. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_schedules** | [**List[CreatePaymentSchedulesResponseItems]**](CreatePaymentSchedulesResponseItems.md) | Container for payment parts.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_schedules_response import CreatePaymentSchedulesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentSchedulesResponse from a JSON string
create_payment_schedules_response_instance = CreatePaymentSchedulesResponse.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentSchedulesResponse.to_json())

# convert the object into a dict
create_payment_schedules_response_dict = create_payment_schedules_response_instance.to_dict()
# create an instance of CreatePaymentSchedulesResponse from a dict
create_payment_schedules_response_from_dict = CreatePaymentSchedulesResponse.from_dict(create_payment_schedules_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


