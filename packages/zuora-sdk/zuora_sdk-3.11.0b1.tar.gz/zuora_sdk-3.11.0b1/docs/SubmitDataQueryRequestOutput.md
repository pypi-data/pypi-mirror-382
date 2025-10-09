# SubmitDataQueryRequestOutput

Additional information about the query results. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target** | [**SubmitDataQueryRequestOutputTarget**](SubmitDataQueryRequestOutputTarget.md) |  | 

## Example

```python
from zuora_sdk.models.submit_data_query_request_output import SubmitDataQueryRequestOutput

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitDataQueryRequestOutput from a JSON string
submit_data_query_request_output_instance = SubmitDataQueryRequestOutput.from_json(json)
# print the JSON string representation of the object
print(SubmitDataQueryRequestOutput.to_json())

# convert the object into a dict
submit_data_query_request_output_dict = submit_data_query_request_output_instance.to_dict()
# create an instance of SubmitDataQueryRequestOutput from a dict
submit_data_query_request_output_from_dict = SubmitDataQueryRequestOutput.from_dict(submit_data_query_request_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


