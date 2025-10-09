# ProductRatePlanChargeObjectNSFields

Container for Product Rate Plan Charge fields provided by the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**class__ns** | **str** | Class associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**deferred_rev_account__ns** | **str** | Deferrred revenue account associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**department__ns** | **str** | Department associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**include_children__ns** | [**ProductRatePlanChargeObjectNSFieldsIncludeChildrenNS**](ProductRatePlanChargeObjectNSFieldsIncludeChildrenNS.md) |  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**integration_status__ns** | **str** | Status of the product rate plan charge&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**item_type__ns** | [**ProductRatePlanChargeObjectNSFieldsItemTypeNS**](ProductRatePlanChargeObjectNSFieldsItemTypeNS.md) |  | [optional] 
**location__ns** | **str** | Location associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**recognized_rev_account__ns** | **str** | Recognized revenue account associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**rev_rec_end__ns** | [**ProductRatePlanChargeObjectNSFieldsRevRecEndNS**](ProductRatePlanChargeObjectNSFieldsRevRecEndNS.md) |  | [optional] 
**rev_rec_start__ns** | [**ProductRatePlanChargeObjectNSFieldsRevRecStartNS**](ProductRatePlanChargeObjectNSFieldsRevRecStartNS.md) |  | [optional] 
**rev_rec_template_type__ns** | **str** | Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**subsidiary__ns** | **str** | Subsidiary associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**sync_date__ns** | **str** | Date when the product rate plan charge was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 

## Example

```python
from zuora_sdk.models.product_rate_plan_charge_object_ns_fields import ProductRatePlanChargeObjectNSFields

# TODO update the JSON string below
json = "{}"
# create an instance of ProductRatePlanChargeObjectNSFields from a JSON string
product_rate_plan_charge_object_ns_fields_instance = ProductRatePlanChargeObjectNSFields.from_json(json)
# print the JSON string representation of the object
print(ProductRatePlanChargeObjectNSFields.to_json())

# convert the object into a dict
product_rate_plan_charge_object_ns_fields_dict = product_rate_plan_charge_object_ns_fields_instance.to_dict()
# create an instance of ProductRatePlanChargeObjectNSFields from a dict
product_rate_plan_charge_object_ns_fields_from_dict = ProductRatePlanChargeObjectNSFields.from_dict(product_rate_plan_charge_object_ns_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


