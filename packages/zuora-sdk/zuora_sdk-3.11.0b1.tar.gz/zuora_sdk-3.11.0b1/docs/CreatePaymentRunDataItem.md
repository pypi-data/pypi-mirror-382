# CreatePaymentRunDataItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_item_id** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**tax_item_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_run_data_item import CreatePaymentRunDataItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentRunDataItem from a JSON string
create_payment_run_data_item_instance = CreatePaymentRunDataItem.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentRunDataItem.to_json())

# convert the object into a dict
create_payment_run_data_item_dict = create_payment_run_data_item_instance.to_dict()
# create an instance of CreatePaymentRunDataItem from a dict
create_payment_run_data_item_from_dict = CreatePaymentRunDataItem.from_dict(create_payment_run_data_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


