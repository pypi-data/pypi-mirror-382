# GetWorkflowResponseStatus

The status of the workflow:   - Queued: The workflow is in queue for being processed.   - Processing: The workflow is in process.   - Stopping: The workflow is being stopped through Zuora UI.   - Stopped: The workflow is stopped through Zuora UI.   - Finished: The workflow is finished. When a workflow is finished, it might have tasks pending for retry or delay. Pending tasks do not block the onfinish branch of the workflow, but they block the oncomplete branch of the iterate.  

## Enum

* `QUEUED` (value: `'Queued'`)

* `PROCESSING` (value: `'Processing'`)

* `STOPPING` (value: `'Stopping'`)

* `STOPPED` (value: `'Stopped'`)

* `FINISHED` (value: `'Finished'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


