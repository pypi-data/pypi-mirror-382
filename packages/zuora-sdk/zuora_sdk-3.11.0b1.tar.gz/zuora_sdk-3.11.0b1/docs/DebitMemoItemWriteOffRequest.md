# DebitMemoItemWriteOffRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** | Comments about the credit memo item.  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**debit_memo_item_id** | **str** | The ID of the debit memo item.  | [optional] 
**service_end_date** | **date** | The service end date of the credit memo item.   | [optional] 
**service_start_date** | **date** | The service start date of the credit memo item.   | [optional] 
**sku_name** | **str** | The name of the charge associated with the invoice.  | [optional] 
**unit_of_measure** | **str** | The definable unit that you measure when determining charges.  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**taxation_items** | [**List[DebitMemoTaxationItemWriteOffRequest]**](DebitMemoTaxationItemWriteOffRequest.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_item_write_off_request import DebitMemoItemWriteOffRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoItemWriteOffRequest from a JSON string
debit_memo_item_write_off_request_instance = DebitMemoItemWriteOffRequest.from_json(json)
# print the JSON string representation of the object
print(DebitMemoItemWriteOffRequest.to_json())

# convert the object into a dict
debit_memo_item_write_off_request_dict = debit_memo_item_write_off_request_instance.to_dict()
# create an instance of DebitMemoItemWriteOffRequest from a dict
debit_memo_item_write_off_request_from_dict = DebitMemoItemWriteOffRequest.from_dict(debit_memo_item_write_off_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


