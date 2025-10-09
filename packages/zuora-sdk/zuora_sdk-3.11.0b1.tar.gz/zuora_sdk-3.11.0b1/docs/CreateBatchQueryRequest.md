# CreateBatchQueryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_version** | **str** | The API version for the query. If an API version is not specified, the latest version is used by default. Using the latest WSDL version is most useful for reporting use cases. For integration purposes, specify the WSDL version to ensure consistent query behavior, that is, what is supported and included in the response returned by the API.  **Note**: As of API version 69 and later, Zuora changed the format of certain fields. See &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/G_SOAP_API/AB_Getting_started_with_the__SOAP_API/C_Date_Field_Changes_in_the_SOAP_API\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Date Field Changes in the SOAP API&lt;/a&gt; for more information and a list of affected fields.  | [optional] 
**convert_to_currencies** | **str** | The currencies that you want to convert transaction amounts into. You can specify any number of currencies. Specify the currencies using their &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Quick_References/Country%2C_State%2C_and_Province_Codes/D_Currencies_and_Their_3-Letter_Codes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;ISO currency codes&lt;/a&gt; and separate each currency with a comma, for example, \&quot;EUR,GBP,JPY\&quot;.  See &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Collect/Zuora_Finance/D_Finance_Settings/F_Foreign_Currency_Conversion/Foreign_Currency_Conversion_for_Data_Source_Exports#Creating_the_Data_Source_Export_Using_the_AQuA_API\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Convert Transaction Amounts Into Any Currency&lt;/a&gt; for more information and examples.  To use this field, you must have &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Collect/Zuora_Finance/D_Finance_Settings/F_Foreign_Currency_Conversion\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Foreign Currency Conversion&lt;/a&gt; enabled and you must be using API version 78 or later.  | [optional] 
**deleted** | [**DeletedRecord**](DeletedRecord.md) |  | [optional] 
**name** | **str** | The query name that can uniquely identify the query in this API request.  | [optional] 
**query** | **str** | A valid ZOQL query or Export ZOQL query statement.  | [optional] 
**type** | [**BatchQueryType**](BatchQueryType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_batch_query_request import CreateBatchQueryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBatchQueryRequest from a JSON string
create_batch_query_request_instance = CreateBatchQueryRequest.from_json(json)
# print the JSON string representation of the object
print(CreateBatchQueryRequest.to_json())

# convert the object into a dict
create_batch_query_request_dict = create_batch_query_request_instance.to_dict()
# create an instance of CreateBatchQueryRequest from a dict
create_batch_query_request_from_dict = CreateBatchQueryRequest.from_dict(create_batch_query_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


