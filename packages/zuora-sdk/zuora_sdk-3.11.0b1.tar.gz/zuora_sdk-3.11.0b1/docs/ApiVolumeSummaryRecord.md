# ApiVolumeSummaryRecord

A volume summary record. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api** | **str** | The API path name.  | [optional] 
**error** | **int** | The count of failed API requests of above &#x60;api&#x60; and &#x60;httpMethod&#x60;.  | [optional] 
**http_method** | **str** | The http method.  | [optional] 
**success** | **int** | The count of successful API requests of above &#x60;api&#x60; and &#x60;httpMethod&#x60;.  | [optional] 
**total** | **int** | The count of total API requests of above &#x60;api&#x60; and &#x60;httpMethod&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.api_volume_summary_record import ApiVolumeSummaryRecord

# TODO update the JSON string below
json = "{}"
# create an instance of ApiVolumeSummaryRecord from a JSON string
api_volume_summary_record_instance = ApiVolumeSummaryRecord.from_json(json)
# print the JSON string representation of the object
print(ApiVolumeSummaryRecord.to_json())

# convert the object into a dict
api_volume_summary_record_dict = api_volume_summary_record_instance.to_dict()
# create an instance of ApiVolumeSummaryRecord from a dict
api_volume_summary_record_from_dict = ApiVolumeSummaryRecord.from_dict(api_volume_summary_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


