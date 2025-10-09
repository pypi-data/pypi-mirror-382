# AccountObjectNSFields

Container for Account fields provided by the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**class__ns** | **str** | Value of the Class field for the corresponding customer account in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**customer_type__ns** | [**AccountObjectNSFieldsCustomerTypeNS**](AccountObjectNSFieldsCustomerTypeNS.md) |  | [optional] 
**department__ns** | **str** | Value of the Department field for the corresponding customer account in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**integration_status__ns** | **str** | Status of the account&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**location__ns** | **str** | Value of the Location field for the corresponding customer account in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**subsidiary__ns** | **str** | Value of the Subsidiary field for the corresponding customer account in NetSuite. The Subsidiary field is required if you use NetSuite OneWorld. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**sync_date__ns** | **str** | Date when the account was sychronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**syncto_net_suite__ns** | [**AccountObjectNSFieldsSynctoNetSuiteNS**](AccountObjectNSFieldsSynctoNetSuiteNS.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.account_object_ns_fields import AccountObjectNSFields

# TODO update the JSON string below
json = "{}"
# create an instance of AccountObjectNSFields from a JSON string
account_object_ns_fields_instance = AccountObjectNSFields.from_json(json)
# print the JSON string representation of the object
print(AccountObjectNSFields.to_json())

# convert the object into a dict
account_object_ns_fields_dict = account_object_ns_fields_instance.to_dict()
# create an instance of AccountObjectNSFields from a dict
account_object_ns_fields_from_dict = AccountObjectNSFields.from_dict(account_object_ns_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


