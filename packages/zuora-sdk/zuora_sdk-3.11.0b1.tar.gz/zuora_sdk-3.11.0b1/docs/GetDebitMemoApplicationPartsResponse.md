# GetDebitMemoApplicationPartsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_parts** | [**List[GetDebitMemoApplicationPart]**](GetDebitMemoApplicationPart.md) | Container for application parts.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_debit_memo_application_parts_response import GetDebitMemoApplicationPartsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDebitMemoApplicationPartsResponse from a JSON string
get_debit_memo_application_parts_response_instance = GetDebitMemoApplicationPartsResponse.from_json(json)
# print the JSON string representation of the object
print(GetDebitMemoApplicationPartsResponse.to_json())

# convert the object into a dict
get_debit_memo_application_parts_response_dict = get_debit_memo_application_parts_response_instance.to_dict()
# create an instance of GetDebitMemoApplicationPartsResponse from a dict
get_debit_memo_application_parts_response_from_dict = GetDebitMemoApplicationPartsResponse.from_dict(get_debit_memo_application_parts_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


