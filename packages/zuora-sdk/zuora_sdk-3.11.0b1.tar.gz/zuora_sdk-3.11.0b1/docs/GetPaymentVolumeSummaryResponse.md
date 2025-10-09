# GetPaymentVolumeSummaryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[PaymentVolumeSummaryRecord]**](PaymentVolumeSummaryRecord.md) | List of electronic payments summary.  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_volume_summary_response import GetPaymentVolumeSummaryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentVolumeSummaryResponse from a JSON string
get_payment_volume_summary_response_instance = GetPaymentVolumeSummaryResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentVolumeSummaryResponse.to_json())

# convert the object into a dict
get_payment_volume_summary_response_dict = get_payment_volume_summary_response_instance.to_dict()
# create an instance of GetPaymentVolumeSummaryResponse from a dict
get_payment_volume_summary_response_from_dict = GetPaymentVolumeSummaryResponse.from_dict(get_payment_volume_summary_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


