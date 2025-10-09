# GetApiVolumeSummaryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ApiVolumeSummaryRecord]**](ApiVolumeSummaryRecord.md) | List of API volume summary records. The records are grouped and ordered by API path name and http method.       | [optional] 

## Example

```python
from zuora_sdk.models.get_api_volume_summary_response import GetApiVolumeSummaryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetApiVolumeSummaryResponse from a JSON string
get_api_volume_summary_response_instance = GetApiVolumeSummaryResponse.from_json(json)
# print the JSON string representation of the object
print(GetApiVolumeSummaryResponse.to_json())

# convert the object into a dict
get_api_volume_summary_response_dict = get_api_volume_summary_response_instance.to_dict()
# create an instance of GetApiVolumeSummaryResponse from a dict
get_api_volume_summary_response_from_dict = GetApiVolumeSummaryResponse.from_dict(get_api_volume_summary_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


