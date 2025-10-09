# CreateBatchQueryJobRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**date_time_utc** | **bool** | When using WSDL 69 and later you can ensure that the exported output of dateTime records are rendered according to ISO-8601 generic UTC form by setting &#x60;dateTimeUtc&#x60; to &#x60;true&#x60;.  When &#x60;dateTimeUtc&#x60; is set to &#x60;true&#x60;, exports of dateTime data types will be rendered in the following generic format: &#x60;YYYY-MM-DDThh:mm:ss-hhmm&#x60; or &#x60;YYYY-MM-DDThh:mm:ss+hhmm&#x60;.  **Note**: Regardless of what batchType query is used (&#x60;zoql&#x60; or &#x60;zoqlexport&#x60;), the query response output for datetime data types can be standardized by setting dateTimeUtc to &#x60;true&#x60;. When &#x60;true&#x60;, the results will display datetime types with the format: YYYY-MM-DDThh:mm:ss+/-hhmm.  | [optional] 
**format** | [**BatchQueryFormat**](BatchQueryFormat.md) |  | [optional] 
**name** | **str** | The name of the job. 32 character limit.  | [optional] 
**notify_url** | **str** | If URL is provided, the AQuA job will call this &#x60;notifyUrl&#x60; once the job has completed. The value of &#x60;notifyUrl&#x60; needs to have &#x60;${JOBID}&#x60; and &#x60;${STATUS}&#x60; placeholders. These placeholders will be replaced by the actual job ID and status when returned in the response. Status will be &#x60;Completed&#x60; after the AQuA job is done.  If you submit an AQuA query with &#x60;notifyUrl&#x60; specified, the value of &#x60;notifyUrl&#x60; will be ignored if your organization has already &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/AB_Aggregate_Query_API/Callout_Notification_for_Completed_AQuA_Jobs\&quot; target&#x3D;\&quot;_blank\&quot;&gt;configured a callout notification through the Zuora user interface&lt;/a&gt;.   | [optional] 
**null_replacement** | **str** | The string used to represent null values in the query results. If you do not set this parameter, null values are represented by the empty string in the query results.  | [optional] 
**offset** | **float** | This field specifies the time offset for AQuA queries in stateful mode. It is an integer in the range 0 to 3,600 seconds.  For example, if you set this field to 600 seconds and you post a query in stateful mode at 2:00 AM, it will query against data created or updated between the completion time of the previous query and 1:50 AM.  The value of this field will override the value you configured in **Settings** &gt; **Administration** &gt; **AQuA API Stateful Mode Time Offset**.          | [optional] 
**partner** | **str** | The partner field indicates the unique ID of a data integration partner. The dropdown list of this field displays partner IDs for the past thirty days. It must be used together with \&quot;project\&quot; field to uniquely identify a data integration target.  For example, if a continuous AQuA session is to retrieve data incrementally for a Salesforce.com Org 00170000011K3Ub, you can use partner as \&quot;Salesforce\&quot;, and \&quot;project\&quot; as \&quot;00170000011K3Ub.\&quot;  This field is required only if you are using AQuA in stateful mode. Otherwise, if you are using AQuA in stateless mode, partner field can be null.  **Note**: Zuora highly recommends you use the stateless mode instead of the stateful mode to extract bulk data. See &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/AB_Aggregate_Query_API/Bulk_data__extraction_from_Zuora_using_AQuA\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Bulk data extraction from Zuora using AQuA&lt;/a&gt; for best practices. **Note**: Submit a request at &lt;a href&#x3D;\&quot;http://support.zuora.com\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt; to obtain a partner ID.  | [optional] 
**project** | **str** | The project field contains the unique ID of a data integration project for a particular partner. The dropdown list of this field displays project IDs for the past thirty days.  This field must be used together with partner field to uniquely identify a data integration target.   This field is required only if you are using AQuA in stateful mode. Otherwise, if you are using AQuA in stateless mode, partner field can be null.  | [optional] 
**queries** | [**List[CreateBatchQueryRequest]**](CreateBatchQueryRequest.md) | A JSON array object that contains a list of batch objects.  | [optional] 
**use_query_labels** | **bool** | When this optional flag is set to &#x60;true&#x60; the request will use object and field API names for the CSV header output instead of the field labels. Data integration projects should set &#x60;useQueryLabels&#x60; to &#x60;true&#x60; so that API names remain the same.  By default &#x60;useQueryLabels&#x60; is &#x60;false&#x60;, so that output CSV headers display the more user-friendly object and field labels.   | [optional] 
**version** | **str** | The API version you want to use.   The supported versions are as follows:   - &#x60;1.1&#x60;. It supports both modes   - &#x60;1.0&#x60;. Default. It supports stateless modes only.  See &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/AB_Aggregate_Query_API/BA_Stateless_and_Stateful_Modes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Stateless and stateful modes&lt;/a&gt; for more information.  | [optional] 

## Example

```python
from zuora_sdk.models.create_batch_query_job_request import CreateBatchQueryJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBatchQueryJobRequest from a JSON string
create_batch_query_job_request_instance = CreateBatchQueryJobRequest.from_json(json)
# print the JSON string representation of the object
print(CreateBatchQueryJobRequest.to_json())

# convert the object into a dict
create_batch_query_job_request_dict = create_batch_query_job_request_instance.to_dict()
# create an instance of CreateBatchQueryJobRequest from a dict
create_batch_query_job_request_from_dict = CreateBatchQueryJobRequest.from_dict(create_batch_query_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


