# GetDebitMemoPdfStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**debit_memo_id** | **str** | The ID of the debit memo whose pdf status is requested.  | [optional] 
**debit_memo_number** | **str** | The debit memo number of the debit memo whose pdf status is requested.  | [optional] 
**pdf_generation_status** | **str** | The generation status of the debit memo PDF. Can be one of - None/Pending/Processing/Generated/Error/Obsolete/Archived  | [optional] 
**pdf_file_url** | **str** | The file URL of the debit memo PDF if it&#39;s generated successfully.  | [optional] 
**error_category** | **str** | The error category if debit memo PDF generation failed.  | [optional] 
**error_message** | **str** | The error message if debit memo PDF generation failed.  | [optional] 
**created_on** | **str** | The time at which the request to generate the PDF was created.  | [optional] 
**updated_on** | **str** | The time at which the request to generate the PDF was updated.  | [optional] 

## Example

```python
from zuora_sdk.models.get_debit_memo_pdf_status_response import GetDebitMemoPdfStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDebitMemoPdfStatusResponse from a JSON string
get_debit_memo_pdf_status_response_instance = GetDebitMemoPdfStatusResponse.from_json(json)
# print the JSON string representation of the object
print(GetDebitMemoPdfStatusResponse.to_json())

# convert the object into a dict
get_debit_memo_pdf_status_response_dict = get_debit_memo_pdf_status_response_instance.to_dict()
# create an instance of GetDebitMemoPdfStatusResponse from a dict
get_debit_memo_pdf_status_response_from_dict = GetDebitMemoPdfStatusResponse.from_dict(get_debit_memo_pdf_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


