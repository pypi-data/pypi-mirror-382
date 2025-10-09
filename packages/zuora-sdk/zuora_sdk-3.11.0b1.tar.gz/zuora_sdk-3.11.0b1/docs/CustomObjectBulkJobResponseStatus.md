# CustomObjectBulkJobResponseStatus

The status of the bulk job:  - `accepted` - The job has been accepted and is ready to process. - `pending` - The job is waiting for your input. You can use [Upload a file for a custom object bulk job](https://www.zuora.com/developer/api-references/api/operation/Post_UploadFileForCustomObjectBulkJob) to upload a file so that the job can start creating records. - `in_progress` - The job is processing. - `completed` - The job has completed. - `failed` - The job was unable to complete. You can use [List all errors for a custom object bulk job](https://www.zuora.com/developer/api-references/api/operation/Get_CustomObjectBulkJobErrors) to list the errors. - `cancelled` - The job was cancelled by the server. 

## Enum

* `ACCEPTED` (value: `'accepted'`)

* `PENDING` (value: `'pending'`)

* `IN_PROGRESS` (value: `'in_progress'`)

* `COMPLETED` (value: `'completed'`)

* `FAILED` (value: `'failed'`)

* `CANCELLED` (value: `'cancelled'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


