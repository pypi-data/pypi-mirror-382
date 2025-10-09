# PreviewSubscriptionAccountInfo

A container for providing a customer account information if you do not have an existing customer account. This customer account information is only used for subscription preview.   You must specify the account information either in this field or in the `accountKey` field with the following conditions:   * If you already have a customer account, specify the account number or ID in the accountKey field.  * If you do not have a customer account, provide account information in this field.

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
**bill_cycle_day** | **int** | The account&#39;s bill cycle day (BCD), when bill runs generate invoices for the account. Specify any day of the month (&#x60;1&#x60;-&#x60;31&#x60;, where &#x60;31&#x60; &#x3D; end-of-month), or &#x60;0&#x60; for auto-set. | 
**bill_to_contact** | [**PreviewSubscriptionBillToContact**](PreviewSubscriptionBillToContact.md) |  | 
**currency** | **str** | A currency as defined in Billing Settings.  | 

## Example

```python
from zuora_sdk.models.preview_subscription_account_info import PreviewSubscriptionAccountInfo

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewSubscriptionAccountInfo from a JSON string
preview_subscription_account_info_instance = PreviewSubscriptionAccountInfo.from_json(json)
# print the JSON string representation of the object
print(PreviewSubscriptionAccountInfo.to_json())

# convert the object into a dict
preview_subscription_account_info_dict = preview_subscription_account_info_instance.to_dict()
# create an instance of PreviewSubscriptionAccountInfo from a dict
preview_subscription_account_info_from_dict = PreviewSubscriptionAccountInfo.from_dict(preview_subscription_account_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


