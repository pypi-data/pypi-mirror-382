# CreateBatchQueryJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**batches** | [**List[CreateBatchQueryResponse]**](CreateBatchQueryResponse.md) | A JSON array object that contains a list of batch objects.  | [optional] 
**error_code** | **str** | The error code used to identify the failure reason. | [optional] 
**message** | **str** | The error message used to describe the failure reason detail. | [optional] 
**encrypted** | [**BatchQueryEncrypted**](BatchQueryEncrypted.md) |  | [optional] 
**format** | [**BatchQueryFormat**](BatchQueryFormat.md) |  | [optional] 
**id** | **str** | The job ID created for the AQuA API request. The job ID can be used for querying for the query status.   The ID exists only if the JSON request can be parsed and validated successfully. Otherwise, the job ID is null.  | [optional] 
**name** | **str** | The name of the job. 32 character limit.  | [optional] 
**notify_url** | **str** | If URL is provided, the AQuA job will call this &#x60;notifyUrl&#x60; once the job has completed. The value of &#x60;notifyUrl&#x60; needs to have &#x60;${JOBID}&#x60; and &#x60;${STATUS}&#x60; placeholders. These placeholders will be replaced by the actual job ID and status when returned in the response. Status will be &#x60;Completed&#x60; after the AQuA job is done.  If you submit an AQuA query with &#x60;notifyUrl&#x60; specified, the value of &#x60;notifyUrl&#x60; will be ignored if your organization has already &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/AB_Aggregate_Query_API/Callout_Notification_for_Completed_AQuA_Jobs\&quot; target&#x3D;\&quot;_blank\&quot;&gt;configured a callout notification through the Zuora user interface&lt;/a&gt;.             | [optional] 
**offset** | **float** | This field specifies the time offset for AQuA queries in stateful mode. It is an integer in the range 0 to 3,600 seconds.  For example, if you set this field to 600 seconds and you post a query in stateful mode at 2:00 AM, it will query against data created or updated between the completion time of the previous query and 1:50 AM.  The value of this field will override the value you configured in **Settings** &gt; **Administration** &gt; **AQuA API Stateful Mode Time Offset**.      | [optional] 
**partner** | **str** | The partner field indicates the unique ID of a data integration partner. The dropdown list of this field displays partner IDs for the past thirty days.  It must be used together with \&quot;project\&quot; field to uniquely identify a data integration target.  For example, if a continuous AQuA session is to retrieve data incrementally for a Salesforce.com Org 00170000011K3Ub, you can use partner as \&quot;Salesforce\&quot;, and \&quot;project\&quot; as \&quot;00170000011K3Ub.\&quot;   This field is required only if you are using AQuA in stateful mode. Otherwise, if you are using AQuA in stateless mode, partner field can be null.  **Note**: Zuora highly recommends you use the stateless mode instead of the stateful mode to extract bulk data. See &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/AB_Aggregate_Query_API/Bulk_data__extraction_from_Zuora_using_AQuA\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Bulk data extraction from Zuora using AQuA&lt;/a&gt; for best practices.  **Note**: Submit a request at &lt;a href&#x3D;\&quot;http://support.zuora.com\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt; to obtain a partner ID.  | [optional] 
**project** | **str** | The project field contains the unique ID of a data integration project for a particular partner. The dropdown list of this field displays project IDs for the past thirty days.  This field must be used together with partner field to uniquely identify a data integration target.   This field is required only if you are using AQuA in stateful mode. Otherwise, if you are using AQuA in stateless mode, partner field can be null.  | [optional] 
**status** | [**BatchQueryStatus**](BatchQueryStatus.md) |  | [optional] 
**localized_status** | [**BatchQueryStatus**](BatchQueryStatus.md) |  | [optional] 
**use_last_completed_job_queries** | **bool** | If this flag is set to &#x60;true&#x60;, then all the previous queries are merged with existing queries.  If the flag is set to &#x60;false&#x60;, then the previous queries are ignored, and only the new query is executed.  | [optional] 
**version** | **str** | The API version you want to use.   The supported versions are as follows:   - &#x60;1.1&#x60;. It supports both modes   - &#x60;1.0&#x60;. Default. It supports stateless modes only.  See &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/AB_Aggregate_Query_API/BA_Stateless_and_Stateful_Modes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Stateless and stateful modes&lt;/a&gt; for more information.  | [optional] 

## Example

```python
from zuora_sdk.models.create_batch_query_job_response import CreateBatchQueryJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBatchQueryJobResponse from a JSON string
create_batch_query_job_response_instance = CreateBatchQueryJobResponse.from_json(json)
# print the JSON string representation of the object
print(CreateBatchQueryJobResponse.to_json())

# convert the object into a dict
create_batch_query_job_response_dict = create_batch_query_job_response_instance.to_dict()
# create an instance of CreateBatchQueryJobResponse from a dict
create_batch_query_job_response_from_dict = CreateBatchQueryJobResponse.from_dict(create_batch_query_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


