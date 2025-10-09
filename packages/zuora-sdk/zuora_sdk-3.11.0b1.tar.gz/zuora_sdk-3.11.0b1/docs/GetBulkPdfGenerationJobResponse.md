# GetBulkPdfGenerationJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **str** | Unique Id for the Triggered Job | [optional] 
**job_name** | **str** | Name of the Job provided during the POST request of the Job | [optional] 
**status** | [**BulkPDFGenerationJobStatus**](BulkPDFGenerationJobStatus.md) |  | [optional] 
**step_status** | [**BulkPDFGenerationStepStatus**](BulkPDFGenerationStepStatus.md) |  | [optional] 
**file_urls** | **List[str]** | Collection of S3 Pre-Signed URL(s) that can be downloaded | [optional] 
**failed_documents** | [**List[DocumentIdList]**](DocumentIdList.md) | Array of Objects where each object contains billing document type and their ids which failed to execute | [optional] 
**skipped_documents** | [**List[DocumentIdList]**](DocumentIdList.md) | Array of Objects where each object contains billing document type and their ids which failed to execute | [optional] 
**created_on** | **str** | Job Created Time | [optional] 
**created_by** | **str** | Id of the user who created the job | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_bulk_pdf_generation_job_response import GetBulkPdfGenerationJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetBulkPdfGenerationJobResponse from a JSON string
get_bulk_pdf_generation_job_response_instance = GetBulkPdfGenerationJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetBulkPdfGenerationJobResponse.to_json())

# convert the object into a dict
get_bulk_pdf_generation_job_response_dict = get_bulk_pdf_generation_job_response_instance.to_dict()
# create an instance of GetBulkPdfGenerationJobResponse from a dict
get_bulk_pdf_generation_job_response_from_dict = GetBulkPdfGenerationJobResponse.from_dict(get_bulk_pdf_generation_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


