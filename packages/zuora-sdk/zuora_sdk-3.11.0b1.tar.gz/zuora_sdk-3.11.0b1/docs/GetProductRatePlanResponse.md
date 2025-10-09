# GetProductRatePlanResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**external_id_source_system** | **str** | The combination of &#x60;externallyManagedPlanId&#x60; and &#x60;externalIdSourceSystem&#x60; is the unique identifier for the rate plan purchased on a third-party store. This field is used to represent a subscription rate plan created through third-party stores.  | [optional] 
**description** | **str** | The short description of the product rate plan.  | [optional] 
**effective_end_date** | **date** | The end date of the product rate plan.  | [optional] 
**effective_start_date** | **date** | The start date of the product rate plan.  | [optional] 
**externally_managed_plan_ids** | **List[str]** | The unique identifier for the product rate plan in a third-party store. This field is used to represent a rate plan created through third-party stores.  | [optional] 
**grade** | **float** | The grade of the product rate plan.  **Note**: This field is in the **Early Adopter** phase. We are actively soliciting feedback from a small set of early adopters before releasing it as generally available. If you want to join this early adopter program, submit a request at [Zuora Global Support](http://support.zuora.com/).  | [optional] 
**id** | **str** | The unique product rate plan ID.  | [optional] 
**name** | **str** | The name of the product rate plan.  | [optional] 
**product_rate_plan_number** | **str** | The natural key of the product rate plan.  | [optional] 
**status** | [**ProductRatePlanStatus**](ProductRatePlanStatus.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_product_rate_plan_response import GetProductRatePlanResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetProductRatePlanResponse from a JSON string
get_product_rate_plan_response_instance = GetProductRatePlanResponse.from_json(json)
# print the JSON string representation of the object
print(GetProductRatePlanResponse.to_json())

# convert the object into a dict
get_product_rate_plan_response_dict = get_product_rate_plan_response_instance.to_dict()
# create an instance of GetProductRatePlanResponse from a dict
get_product_rate_plan_response_from_dict = GetProductRatePlanResponse.from_dict(get_product_rate_plan_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


