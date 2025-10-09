# ProductRatePlanObjectNSFields

Container for Product Rate Plan fields provided by the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing_period__ns** | [**ProductRatePlanObjectNSFieldsBillingPeriodNS**](ProductRatePlanObjectNSFieldsBillingPeriodNS.md) |  | [optional] 
**class__ns** | **str** | Class associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**department__ns** | **str** | Department associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**include_children__ns** | [**ProductRatePlanObjectNSFieldsIncludeChildrenNS**](ProductRatePlanObjectNSFieldsIncludeChildrenNS.md) |  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**integration_status__ns** | **str** | Status of the product rate plan&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**item_type__ns** | [**ProductRatePlanObjectNSFieldsItemTypeNS**](ProductRatePlanObjectNSFieldsItemTypeNS.md) |  | [optional] 
**location__ns** | **str** | Location associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**multi_currency_price__ns** | **str** | Multi-currency price associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**price__ns** | **str** | Price associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**subsidiary__ns** | **str** | Subsidiary associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**sync_date__ns** | **str** | Date when the product rate plan was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 

## Example

```python
from zuora_sdk.models.product_rate_plan_object_ns_fields import ProductRatePlanObjectNSFields

# TODO update the JSON string below
json = "{}"
# create an instance of ProductRatePlanObjectNSFields from a JSON string
product_rate_plan_object_ns_fields_instance = ProductRatePlanObjectNSFields.from_json(json)
# print the JSON string representation of the object
print(ProductRatePlanObjectNSFields.to_json())

# convert the object into a dict
product_rate_plan_object_ns_fields_dict = product_rate_plan_object_ns_fields_instance.to_dict()
# create an instance of ProductRatePlanObjectNSFields from a dict
product_rate_plan_object_ns_fields_from_dict = ProductRatePlanObjectNSFields.from_dict(product_rate_plan_object_ns_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


