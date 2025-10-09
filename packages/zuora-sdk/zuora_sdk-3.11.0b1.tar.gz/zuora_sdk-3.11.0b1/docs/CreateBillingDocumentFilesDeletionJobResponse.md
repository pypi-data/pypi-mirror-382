# CreateBillingDocumentFilesDeletionJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The unique ID of the billing document file deletion job.  | [optional] 
**status** | [**CreateBillingDocumentFilesDeletionJobStatus**](CreateBillingDocumentFilesDeletionJobStatus.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.create_billing_document_files_deletion_job_response import CreateBillingDocumentFilesDeletionJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBillingDocumentFilesDeletionJobResponse from a JSON string
create_billing_document_files_deletion_job_response_instance = CreateBillingDocumentFilesDeletionJobResponse.from_json(json)
# print the JSON string representation of the object
print(CreateBillingDocumentFilesDeletionJobResponse.to_json())

# convert the object into a dict
create_billing_document_files_deletion_job_response_dict = create_billing_document_files_deletion_job_response_instance.to_dict()
# create an instance of CreateBillingDocumentFilesDeletionJobResponse from a dict
create_billing_document_files_deletion_job_response_from_dict = CreateBillingDocumentFilesDeletionJobResponse.from_dict(create_billing_document_files_deletion_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


