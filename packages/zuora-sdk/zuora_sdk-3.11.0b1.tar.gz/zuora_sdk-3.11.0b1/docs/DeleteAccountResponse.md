# DeleteAccountResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | The ID of the deleted account. | [optional] 
**job_id** | **str** | The ID of the job that handles the account deletion operation.   You can specify the value of this field as the value of the &#x60;jobId&#x60; path parameter in the [Retrieve an operation job](https://www.zuora.com/developer/api-references/api/operation/Get_OperationJob/) API operation to query job information.  | [optional] 
**job_status** | [**OperationJobStatus**](OperationJobStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.delete_account_response import DeleteAccountResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteAccountResponse from a JSON string
delete_account_response_instance = DeleteAccountResponse.from_json(json)
# print the JSON string representation of the object
print(DeleteAccountResponse.to_json())

# convert the object into a dict
delete_account_response_dict = delete_account_response_instance.to_dict()
# create an instance of DeleteAccountResponse from a dict
delete_account_response_from_dict = DeleteAccountResponse.from_dict(delete_account_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


