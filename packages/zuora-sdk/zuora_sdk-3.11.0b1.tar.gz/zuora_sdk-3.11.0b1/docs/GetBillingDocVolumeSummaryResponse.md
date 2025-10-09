# GetBillingDocVolumeSummaryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[BillingDocVolumeSummaryRecord]**](BillingDocVolumeSummaryRecord.md) | List of billing documents summary, including total generated invoices and credit memos, also a total number of accounts that failed to process. | [optional] 

## Example

```python
from zuora_sdk.models.get_billing_doc_volume_summary_response import GetBillingDocVolumeSummaryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetBillingDocVolumeSummaryResponse from a JSON string
get_billing_doc_volume_summary_response_instance = GetBillingDocVolumeSummaryResponse.from_json(json)
# print the JSON string representation of the object
print(GetBillingDocVolumeSummaryResponse.to_json())

# convert the object into a dict
get_billing_doc_volume_summary_response_dict = get_billing_doc_volume_summary_response_instance.to_dict()
# create an instance of GetBillingDocVolumeSummaryResponse from a dict
get_billing_doc_volume_summary_response_from_dict = GetBillingDocVolumeSummaryResponse.from_dict(get_billing_doc_volume_summary_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


