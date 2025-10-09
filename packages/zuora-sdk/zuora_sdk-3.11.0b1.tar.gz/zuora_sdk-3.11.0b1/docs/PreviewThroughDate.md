# PreviewThroughDate

The preview through date. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**preview_thru_date_policy** | [**PreviewThruDatePolicy**](PreviewThruDatePolicy.md) |  | [optional] 
**next_billing_periods** | **float** | The number of billing periods to preview. Required if &#x60;previewThruDatePolicy&#x60; is &#x60;nextBillingPeriods&#x60;.  | [optional] 
**specific_date** | **str** | The specific date for the preview start date. Required if &#x60;previewThruDatePolicy&#x60; is &#x60;specificDate&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.preview_through_date import PreviewThroughDate

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewThroughDate from a JSON string
preview_through_date_instance = PreviewThroughDate.from_json(json)
# print the JSON string representation of the object
print(PreviewThroughDate.to_json())

# convert the object into a dict
preview_through_date_dict = preview_through_date_instance.to_dict()
# create an instance of PreviewThroughDate from a dict
preview_through_date_from_dict = PreviewThroughDate.from_dict(preview_through_date_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


