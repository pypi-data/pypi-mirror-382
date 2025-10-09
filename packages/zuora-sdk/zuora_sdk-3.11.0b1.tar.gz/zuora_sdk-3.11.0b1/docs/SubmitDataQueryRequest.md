# SubmitDataQueryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column_separator** | **str** | The column separator. Only applicable if the &#x60;outputFormat&#x60; is &#x60;DSV&#x60;.  | [optional] 
**compression** | [**SubmitDataQueryRequestCompression**](SubmitDataQueryRequestCompression.md) |  | 
**encryption_key** | **bytearray** | Base-64 encoded public key of an RSA key-pair.   Note that Data Query only supports 1024-bit RSA keys.  If you set this field, Zuora encrypts the query results using the provided public key. You must use the corresponding private key to decrypt the query results.  | [optional] 
**output** | [**SubmitDataQueryRequestOutput**](SubmitDataQueryRequestOutput.md) |  | 
**output_format** | [**SubmitDataQueryRequestOutputFormat**](SubmitDataQueryRequestOutputFormat.md) |  | 
**query** | **str** | The query to perform. See [SQL Queries in Data Query](https://knowledgecenter.zuora.com/DC_Developers/BA_Data_Query/BA_SQL_Queries_in_Data_Query) for more information.  | 
**read_deleted** | **bool** | Indicates whether the query will retrieve only the deleted record. If &#x60;readDeleted&#x60; is set to &#x60;false&#x60; or it is not included in the request body, the query will retrieve only the non-deleted records. If it is set to &#x60;true&#x60;, only the deleted records will be retrieved.  If you select the &#x60;deleted&#x60; column in the &#x60;query&#x60; field, both non-deleted and deleted records will be retrieved regardless of the value in the &#x60;readDeleted&#x60; field.  Note that Data Query is subject to Zuora Data Retention Policy. The retention period of deleted data is 30 days. You can only retrieve deleted data for 30 days through Data Query.  | [optional] [default to False]
**source_data** | [**SubmitDataQueryRequestSourceData**](SubmitDataQueryRequestSourceData.md) |  | [optional] 
**use_index_join** | **bool** | Indicates whether to use Index Join. Index join is useful when you have a specific reference value in your WHERE clause to index another large table by. See [Use Index Join](https://knowledgecenter.zuora.com/DC_Developers/BA_Data_Query/Best_practices_of_Data_Query#Use_Index_Join) for more information. | [optional] 
**warehouse_size** | [**SubmitDataQueryRequestWarehouseSize**](SubmitDataQueryRequestWarehouseSize.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.submit_data_query_request import SubmitDataQueryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitDataQueryRequest from a JSON string
submit_data_query_request_instance = SubmitDataQueryRequest.from_json(json)
# print the JSON string representation of the object
print(SubmitDataQueryRequest.to_json())

# convert the object into a dict
submit_data_query_request_dict = submit_data_query_request_instance.to_dict()
# create an instance of SubmitDataQueryRequest from a dict
submit_data_query_request_from_dict = SubmitDataQueryRequest.from_dict(submit_data_query_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


