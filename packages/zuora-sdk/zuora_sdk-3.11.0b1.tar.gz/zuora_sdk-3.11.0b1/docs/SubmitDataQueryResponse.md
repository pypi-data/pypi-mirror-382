# SubmitDataQueryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**DataQueryJob**](DataQueryJob.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.submit_data_query_response import SubmitDataQueryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitDataQueryResponse from a JSON string
submit_data_query_response_instance = SubmitDataQueryResponse.from_json(json)
# print the JSON string representation of the object
print(SubmitDataQueryResponse.to_json())

# convert the object into a dict
submit_data_query_response_dict = submit_data_query_response_instance.to_dict()
# create an instance of SubmitDataQueryResponse from a dict
submit_data_query_response_from_dict = SubmitDataQueryResponse.from_dict(submit_data_query_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


