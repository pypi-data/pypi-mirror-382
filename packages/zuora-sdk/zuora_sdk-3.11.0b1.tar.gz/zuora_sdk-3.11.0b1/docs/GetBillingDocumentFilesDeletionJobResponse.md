# GetBillingDocumentFilesDeletionJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The unique ID of the billing document file deletion job.  | [optional] 
**status** | [**GetBillingDocumentFilesDeletionJobStatus**](GetBillingDocumentFilesDeletionJobStatus.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_billing_document_files_deletion_job_response import GetBillingDocumentFilesDeletionJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetBillingDocumentFilesDeletionJobResponse from a JSON string
get_billing_document_files_deletion_job_response_instance = GetBillingDocumentFilesDeletionJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetBillingDocumentFilesDeletionJobResponse.to_json())

# convert the object into a dict
get_billing_document_files_deletion_job_response_dict = get_billing_document_files_deletion_job_response_instance.to_dict()
# create an instance of GetBillingDocumentFilesDeletionJobResponse from a dict
get_billing_document_files_deletion_job_response_from_dict = GetBillingDocumentFilesDeletionJobResponse.from_dict(get_billing_document_files_deletion_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


