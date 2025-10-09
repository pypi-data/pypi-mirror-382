# BulkPdfGenerationJobRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents** | [**List[DocumentIdList]**](DocumentIdList.md) | Array that contains the collection of Objects where each object contains billing document type and their ids  | 
**file_name** | **str** | Prefix part of output file name(s).  Eg:    if fileName is \&quot;all-invoices-posted-jan-2024\&quot; then fileURL(s) contains this name as a prefix followed by suffix _{number}  | 
**name** | **str** | Name of the Job  | [optional] 
**index_file_format** | [**IndexFileFormat**](IndexFileFormat.md) |  | 
**generate_missing_pdf** | **bool** | Flag which controls the behaviour of whether to generate the PDF(s) for the billing documents that doesn&#39;t have one    - setting it to true indicates service would go through the provided document id list and then find those billing documents that doesn&#39;t have PDF generated   and generate them all at once and then proceed to the zipping process    - setting it to false indicates service would go through the provided document id list and find those billing documents that doesn&#39;t have PDF generated and   mark them as Invalid and would skip them from zipping it. Ids marked invalid would be part of the response  Default value is false  | [optional] 
**persist_index_file** | **bool** | Flag which controls whether to generated metadata/index file should be present in the final output file or not.     - setting it to true will generate the metadata/index file and store them along with other PDF files in the final zip file(s).    - setting it to false doesn&#39;t generate the metadata/index file and do not store them in the final zip file(s)  Default value is true  | [optional] 
**ignore_archived_files** | **bool** | Flag which controls whether to skip the archived files or not.     - setting it to true will skip the archived PDF files from including it in the output file. Documents whose Id(s) are in archived status will be displayed in skippedDocuments field of the GET by Job Id API response    - setting it to false will throw error when the job encounters any archived PDF file(s) in the provided document id list.    Default value is false  | [optional] 

## Example

```python
from zuora_sdk.models.bulk_pdf_generation_job_request import BulkPdfGenerationJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkPdfGenerationJobRequest from a JSON string
bulk_pdf_generation_job_request_instance = BulkPdfGenerationJobRequest.from_json(json)
# print the JSON string representation of the object
print(BulkPdfGenerationJobRequest.to_json())

# convert the object into a dict
bulk_pdf_generation_job_request_dict = bulk_pdf_generation_job_request_instance.to_dict()
# create an instance of BulkPdfGenerationJobRequest from a dict
bulk_pdf_generation_job_request_from_dict = BulkPdfGenerationJobRequest.from_dict(bulk_pdf_generation_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


