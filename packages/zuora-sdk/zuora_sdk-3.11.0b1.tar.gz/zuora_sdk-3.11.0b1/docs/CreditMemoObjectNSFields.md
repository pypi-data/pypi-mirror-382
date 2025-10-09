# CreditMemoObjectNSFields

Container for Credit Memo fields provided by the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the credit memo&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**origin__ns** | **str** | Origin of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the credit memo was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**transaction__ns** | **str** | Related transaction in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_object_ns_fields import CreditMemoObjectNSFields

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoObjectNSFields from a JSON string
credit_memo_object_ns_fields_instance = CreditMemoObjectNSFields.from_json(json)
# print the JSON string representation of the object
print(CreditMemoObjectNSFields.to_json())

# convert the object into a dict
credit_memo_object_ns_fields_dict = credit_memo_object_ns_fields_instance.to_dict()
# create an instance of CreditMemoObjectNSFields from a dict
credit_memo_object_ns_fields_from_dict = CreditMemoObjectNSFields.from_dict(credit_memo_object_ns_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


