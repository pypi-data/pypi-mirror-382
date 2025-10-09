# PreviewStartDate

The start date of the preview. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**preview_start_date_policy** | [**PreviewStartDatePolicy**](PreviewStartDatePolicy.md) |  | [optional] 
**specific_date** | **str** | The specific date for the preview start date. Required if &#x60;previewStartDatePolicy&#x60; is &#x60;specificDate&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.preview_start_date import PreviewStartDate

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewStartDate from a JSON string
preview_start_date_instance = PreviewStartDate.from_json(json)
# print the JSON string representation of the object
print(PreviewStartDate.to_json())

# convert the object into a dict
preview_start_date_dict = preview_start_date_instance.to_dict()
# create an instance of PreviewStartDate from a dict
preview_start_date_from_dict = PreviewStartDate.from_dict(preview_start_date_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


