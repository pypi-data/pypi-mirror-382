# UpdateProductRatePlanRequest


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
**product_rate_plan_number** | **str** | The natural key of the product rate plan.    For existing Product Rate Plan objects that are created before this field is introduced, this field will be null. Use this field to specify a value for only these objects. Zuora also provides a tool to help you automatically backfill this field with tenant ID for your existing product catalog. If you want to use this backfill tool, contact [Zuora Global Support](https://support.zuora.com/).   **Note**: This field is only available if you set the &#x60;X-Zuora-WSDL-Version&#x60; request header to &#x60;133&#x60; or later. | [optional] 
**name** | **str** | The name of the product rate plan. The name doesn&#39;t have to be unique in a Product Catalog, but the name has to be unique within a product. | [optional] 
**product_id** | **str** | The ID of the product that contains the product rate plan.  | [optional] 
**active_currencies** | **List[str]** | A list of 3-letter currency codes representing active currencies for the product rate plan. Use a comma to separate each currency code.   If the request body contains this field, the value of this field must contain the desired list of active currencies. The new list can never have more than four differences from the existing list.   This field cannot be used to modify the status of more than four currencies in a single request. For example, in a single request, you can only activate four currencies, or deactivate four currencies, or activate two and deactivate two. Making more than four changes to currencies always requires more than one call.   When specifying this field in the update request, you must provide the full list of active currencies you want, not just incremental changes. For each active currency update, provide the following currencies in the list:   Current active currencies + at most four changes (additions or deletions) | [optional] 
**description** | **str** | A description of the product rate plan.  | [optional] 
**effective_start_date** | **date** | The date when the product rate plan becomes available and can be subscribed to, in &#x60;yyyy-mm-dd&#x60; format. | [optional] 
**effective_end_date** | **date** | The date when the product rate plan expires and can&#39;t be subscribed to, in &#x60;yyyy-mm-dd&#x60; format. | [optional] 
**grade** | **float** | The grade that is assigned for the product rate plan. The value of this field must be a positive integer. The greater the value, the higher the grade.   A product rate plan to be added to a Grading catalog group must have one grade. You can specify a grade for a product rate plan in this request or update the product rate plan individually.   **Notes**:    - To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to &#x60;116&#x60; or later. Otherwise, an error occurs.   - This field is in the **Early Adopter** phase. We are actively soliciting feedback from a small set of early adopters before releasing it as generally available. If you want to join this early adopter program, submit a request at [Zuora Global Support](http://support.zuora.com/). | [optional] 

## Example

```python
from zuora_sdk.models.update_product_rate_plan_request import UpdateProductRatePlanRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateProductRatePlanRequest from a JSON string
update_product_rate_plan_request_instance = UpdateProductRatePlanRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateProductRatePlanRequest.to_json())

# convert the object into a dict
update_product_rate_plan_request_dict = update_product_rate_plan_request_instance.to_dict()
# create an instance of UpdateProductRatePlanRequest from a dict
update_product_rate_plan_request_from_dict = UpdateProductRatePlanRequest.from_dict(update_product_rate_plan_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


