# ProductRatePlan


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
**id** | **str** | Unique product rate-plan ID.  | [optional] 
**product_rate_plan_number** | **str** | The natural key of the product rate plan.  | [optional] 
**name** | **str** | Name of the product rate-plan charge. (Not required to be unique.)  | [optional] 
**description** | **str** | Rate plan description.  | [optional] 
**effective_start_date** | **date** | First date the rate plan is active (i.e., available to be subscribed to), as &#x60;yyyy-mm-dd&#x60;.  Before this date, the status is &#x60;NotStarted&#x60;. | [optional] 
**effective_end_date** | **date** | Final date the rate plan is active, as &#x60;yyyy-mm-dd&#x60;. After this date, the rate plan status is &#x60;Expired&#x60;. | [optional] 
**grade** | **float** | The grade of the product rate plan.   **Note**: This field is in the **Early Adopter** phase. We are actively soliciting feedback from a small set of early adopters before releasing it as generally available. If you want to join this early adopter program, submit a request at [Zuora Global Support](http://support.zuora.com/). | [optional] 
**product_rate_plan_charges** | [**List[ProductRatePlanCharge]**](ProductRatePlanCharge.md) | Field attributes describing the product rate plan charges:  | [optional] 
**status** | [**ProductRatePlanStatus**](ProductRatePlanStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.product_rate_plan import ProductRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of ProductRatePlan from a JSON string
product_rate_plan_instance = ProductRatePlan.from_json(json)
# print the JSON string representation of the object
print(ProductRatePlan.to_json())

# convert the object into a dict
product_rate_plan_dict = product_rate_plan_instance.to_dict()
# create an instance of ProductRatePlan from a dict
product_rate_plan_from_dict = ProductRatePlan.from_dict(product_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


