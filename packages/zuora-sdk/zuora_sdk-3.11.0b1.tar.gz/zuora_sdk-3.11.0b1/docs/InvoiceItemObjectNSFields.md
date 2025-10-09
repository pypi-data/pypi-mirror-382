# InvoiceItemObjectNSFields

Container for Invoice Item fields provided by the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the invoice item&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the invoice item was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 

## Example

```python
from zuora_sdk.models.invoice_item_object_ns_fields import InvoiceItemObjectNSFields

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceItemObjectNSFields from a JSON string
invoice_item_object_ns_fields_instance = InvoiceItemObjectNSFields.from_json(json)
# print the JSON string representation of the object
print(InvoiceItemObjectNSFields.to_json())

# convert the object into a dict
invoice_item_object_ns_fields_dict = invoice_item_object_ns_fields_instance.to_dict()
# create an instance of InvoiceItemObjectNSFields from a dict
invoice_item_object_ns_fields_from_dict = InvoiceItemObjectNSFields.from_dict(invoice_item_object_ns_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


