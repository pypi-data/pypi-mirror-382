# DeleteBatchQueryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**batch_id** | **str** | A 32-character ID of the query batch.  | [optional] 
**batch_type** | [**BatchQueryBatchType**](BatchQueryBatchType.md) |  | [optional] 
**file_id** | **str** | The ID of the query results file.  Use Get Results Files to download the query results file. The query results file is formatted as requested in the batch job. Supported formats are CSV, GZIP, and ZIP.  | [optional] 
**message** | **str** | The error message.  | [optional] 
**name** | **str** | Name of the query supplied in the request.  | [optional] 
**query** | **str** | The requested query string.  | [optional] 
**record_count** | **float** | The number of records included in the query output file.  | [optional] 
**segments** | **List[str]** | Array of IDs of query results files. Replaces fileId for full data loads in stateful mode if &lt;a href &#x3D; \&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/AB_Aggregate_Query_API/G_File_Segmentation\&quot; target&#x3D;\&quot;_blank\&quot;&gt;File Segmentation&lt;/a&gt; is enabled.  Use Get Results Files to download each query results file. Each query results file contains at most 500,000 records and is formatted as requested in the batch job. Supported formats are CSV, GZIP, and ZIP.  | [optional] 
**status** | [**BatchQueryStatus**](BatchQueryStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.delete_batch_query_response import DeleteBatchQueryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteBatchQueryResponse from a JSON string
delete_batch_query_response_instance = DeleteBatchQueryResponse.from_json(json)
# print the JSON string representation of the object
print(DeleteBatchQueryResponse.to_json())

# convert the object into a dict
delete_batch_query_response_dict = delete_batch_query_response_instance.to_dict()
# create an instance of DeleteBatchQueryResponse from a dict
delete_batch_query_response_from_dict = DeleteBatchQueryResponse.from_dict(delete_batch_query_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


