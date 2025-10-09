# PreviewExistingSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**invoices** | [**List[PreviewExistingSubscriptionResultInvoices]**](PreviewExistingSubscriptionResultInvoices.md) | Container for invoices. | [optional] 
**credit_memos** | [**List[PreviewExistingSubscriptionResultCreditMemos]**](PreviewExistingSubscriptionResultCreditMemos.md) | Container for credit memos. This field is only available if you have the Invoice Settlement feature enabled. | [optional] 

## Example

```python
from zuora_sdk.models.preview_existing_subscription_response import PreviewExistingSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewExistingSubscriptionResponse from a JSON string
preview_existing_subscription_response_instance = PreviewExistingSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(PreviewExistingSubscriptionResponse.to_json())

# convert the object into a dict
preview_existing_subscription_response_dict = preview_existing_subscription_response_instance.to_dict()
# create an instance of PreviewExistingSubscriptionResponse from a dict
preview_existing_subscription_response_from_dict = PreviewExistingSubscriptionResponse.from_dict(preview_existing_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


