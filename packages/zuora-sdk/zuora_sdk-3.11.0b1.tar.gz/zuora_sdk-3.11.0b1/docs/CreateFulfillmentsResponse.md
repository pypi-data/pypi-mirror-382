# CreateFulfillmentsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**credit_memo_numbers** | **List[str]** | An array of the credit memo numbers generated in this request. The credit memo is only available if you have the Invoice Settlement feature enabled.  | [optional] 
**fulfillments** | [**List[CreateFulfillmentResponse]**](CreateFulfillmentResponse.md) |  | [optional] 
**invoice_numbers** | **List[str]** | An array of the invoice numbers generated in this request. Normally it includes one invoice number only.  | [optional] 
**paid_amount** | **float** | The total amount collected in this request.  | [optional] 
**payment_number** | **str** | The payment number collected in this request.  | [optional] 

## Example

```python
from zuora_sdk.models.create_fulfillments_response import CreateFulfillmentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFulfillmentsResponse from a JSON string
create_fulfillments_response_instance = CreateFulfillmentsResponse.from_json(json)
# print the JSON string representation of the object
print(CreateFulfillmentsResponse.to_json())

# convert the object into a dict
create_fulfillments_response_dict = create_fulfillments_response_instance.to_dict()
# create an instance of CreateFulfillmentsResponse from a dict
create_fulfillments_response_from_dict = CreateFulfillmentsResponse.from_dict(create_fulfillments_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


