# InvoiceItemPreviewResultAdditionalInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**quantity** | **float** |  | [optional] 
**unit_of_measure** | **str** |  | [optional] 
**number_of_deliveries** | **float** | The number of delivery for charge.  **Note**: This field is available only if you have the Delivery Pricing feature enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.invoice_item_preview_result_additional_info import InvoiceItemPreviewResultAdditionalInfo

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceItemPreviewResultAdditionalInfo from a JSON string
invoice_item_preview_result_additional_info_instance = InvoiceItemPreviewResultAdditionalInfo.from_json(json)
# print the JSON string representation of the object
print(InvoiceItemPreviewResultAdditionalInfo.to_json())

# convert the object into a dict
invoice_item_preview_result_additional_info_dict = invoice_item_preview_result_additional_info_instance.to_dict()
# create an instance of InvoiceItemPreviewResultAdditionalInfo from a dict
invoice_item_preview_result_additional_info_from_dict = InvoiceItemPreviewResultAdditionalInfo.from_dict(invoice_item_preview_result_additional_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


