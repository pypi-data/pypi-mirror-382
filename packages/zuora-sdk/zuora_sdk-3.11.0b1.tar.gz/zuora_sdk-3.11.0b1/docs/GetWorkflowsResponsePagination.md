# GetWorkflowsResponsePagination

An object containing pagination information for the list of workflows returned by the api

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | A string containing the URL where the next page of data can be retrieved.  | [optional] 
**page** | **int** | An integer denoting the current page number.  | [optional] 
**page_length** | **int** | An integer denoting the number of workflows in this response. The maximum value is 50. | [optional] 

## Example

```python
from zuora_sdk.models.get_workflows_response_pagination import GetWorkflowsResponsePagination

# TODO update the JSON string below
json = "{}"
# create an instance of GetWorkflowsResponsePagination from a JSON string
get_workflows_response_pagination_instance = GetWorkflowsResponsePagination.from_json(json)
# print the JSON string representation of the object
print(GetWorkflowsResponsePagination.to_json())

# convert the object into a dict
get_workflows_response_pagination_dict = get_workflows_response_pagination_instance.to_dict()
# create an instance of GetWorkflowsResponsePagination from a dict
get_workflows_response_pagination_from_dict = GetWorkflowsResponsePagination.from_dict(get_workflows_response_pagination_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


