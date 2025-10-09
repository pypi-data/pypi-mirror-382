# BulkPdfGenerationJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**job_id** | **str** | Unique Id for the Job Triggered.  | [optional] 
**invalid_ids** | **List[str]** | Collection of Ids that are not valid.    Id is considered to be invalid if,      * Billing Document Id doesn&#39;t exist in the database for the corresponding Billing Document Type   * generateMissingPDF property is false in the Job Request and Valid PDF doesn&#39;t exist for the Billing Document Id  | [optional] 

## Example

```python
from zuora_sdk.models.bulk_pdf_generation_job_response import BulkPdfGenerationJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkPdfGenerationJobResponse from a JSON string
bulk_pdf_generation_job_response_instance = BulkPdfGenerationJobResponse.from_json(json)
# print the JSON string representation of the object
print(BulkPdfGenerationJobResponse.to_json())

# convert the object into a dict
bulk_pdf_generation_job_response_dict = bulk_pdf_generation_job_response_instance.to_dict()
# create an instance of BulkPdfGenerationJobResponse from a dict
bulk_pdf_generation_job_response_from_dict = BulkPdfGenerationJobResponse.from_dict(bulk_pdf_generation_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


