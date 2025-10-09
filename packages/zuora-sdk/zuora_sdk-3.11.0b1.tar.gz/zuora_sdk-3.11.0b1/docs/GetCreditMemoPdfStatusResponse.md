# GetCreditMemoPdfStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_memo_id** | **str** | The ID of the credit memo whose pdf status is requested.  | [optional] 
**credit_memo_number** | **str** | The credit memo number of the credit memo whose pdf status is requested.  | [optional] 
**pdf_generation_status** | **str** | The generation status of the credit memo PDF. Can be one of - None/Pending/Processing/Generated/Error/Obsolete/Archived  | [optional] 
**pdf_file_url** | **str** | The file URL of the credit memo PDF if it&#39;s generated successfully.  | [optional] 
**error_category** | **str** | The error category if credit memo PDF generation failed.  | [optional] 
**error_message** | **str** | The error message if credit memo PDF generation failed.  | [optional] 
**created_on** | **str** | The time at which the request to generate the PDF was created.  | [optional] 
**updated_on** | **str** | The time at which the request to generate the PDF was updated.  | [optional] 

## Example

```python
from zuora_sdk.models.get_credit_memo_pdf_status_response import GetCreditMemoPdfStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCreditMemoPdfStatusResponse from a JSON string
get_credit_memo_pdf_status_response_instance = GetCreditMemoPdfStatusResponse.from_json(json)
# print the JSON string representation of the object
print(GetCreditMemoPdfStatusResponse.to_json())

# convert the object into a dict
get_credit_memo_pdf_status_response_dict = get_credit_memo_pdf_status_response_instance.to_dict()
# create an instance of GetCreditMemoPdfStatusResponse from a dict
get_credit_memo_pdf_status_response_from_dict = GetCreditMemoPdfStatusResponse.from_dict(get_credit_memo_pdf_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


