# CreateBillingDocumentFilesDeletionJobRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_ids** | **List[str]** | Container for the IDs of the accounts that you want to create the billing document files deletion job for.   **Note**: When creating jobs to delete billing document PDF files, you must specify either set of &#x60;accountIds&#x60; or &#x60;accountKeys&#x60; in the request body. | [optional] 
**account_keys** | **List[str]** | Container for the IDs and/or numbers of the accounts that you want to create the billing document files deletion job for.   **Note**: When creating jobs to delete billing document PDF files, you must specify either set of &#x60;accountIds&#x60; or &#x60;accountKeys&#x60; in the request body. | [optional] 

## Example

```python
from zuora_sdk.models.create_billing_document_files_deletion_job_request import CreateBillingDocumentFilesDeletionJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBillingDocumentFilesDeletionJobRequest from a JSON string
create_billing_document_files_deletion_job_request_instance = CreateBillingDocumentFilesDeletionJobRequest.from_json(json)
# print the JSON string representation of the object
print(CreateBillingDocumentFilesDeletionJobRequest.to_json())

# convert the object into a dict
create_billing_document_files_deletion_job_request_dict = create_billing_document_files_deletion_job_request_instance.to_dict()
# create an instance of CreateBillingDocumentFilesDeletionJobRequest from a dict
create_billing_document_files_deletion_job_request_from_dict = CreateBillingDocumentFilesDeletionJobRequest.from_dict(create_billing_document_files_deletion_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


