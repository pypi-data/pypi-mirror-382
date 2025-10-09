# GetProductRatePlanChargeTierResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by_id** | **str** | The ID of the Zuora user who created the ProductRatePlanChargeTier object.  | [optional] 
**created_date** | **datetime** | The date when the ProductRatePlanChargeTier object was created.  | [optional] 
**currency** | **str** | The valid code corresponding to the currency for the tier&#39;s price.  | [optional] 
**ending_unit** | **float** | The end number of a range of units for the tier.  **Character limit**: 16  **Values**: any positive decimal value  | [optional] 
**id** | **str** | Object identifier. | [optional] 
**price** | **float** | The price of the tier if the charge is a flat fee, or the price of each unit in the tier if the charge model is tiered pricing.   **Character limit**: 16   **Values**: a valid currency value | [optional] 
**price_format** | [**PriceFormatProductRatePlanChargeTier**](PriceFormatProductRatePlanChargeTier.md) |  | [optional] 
**starting_unit** | **float** | The starting number of a range of units for the tier.  **Character limit**: 16  **Values**: any positive decimal value  | [optional] 
**tier** | **int** | A unique number that identifies the tier that the price applies to.  **Character limit**: 20  **Values**: automatically generated  | [optional] 
**updated_by_id** | **str** | The ID of the user who last updated the product rate plan charge tier.  | [optional] 
**updated_date** | **datetime** | The date when the product rate plan charge tier was last updated.  | [optional] 

## Example

```python
from zuora_sdk.models.get_product_rate_plan_charge_tier_response import GetProductRatePlanChargeTierResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetProductRatePlanChargeTierResponse from a JSON string
get_product_rate_plan_charge_tier_response_instance = GetProductRatePlanChargeTierResponse.from_json(json)
# print the JSON string representation of the object
print(GetProductRatePlanChargeTierResponse.to_json())

# convert the object into a dict
get_product_rate_plan_charge_tier_response_dict = get_product_rate_plan_charge_tier_response_instance.to_dict()
# create an instance of GetProductRatePlanChargeTierResponse from a dict
get_product_rate_plan_charge_tier_response_from_dict = GetProductRatePlanChargeTierResponse.from_dict(get_product_rate_plan_charge_tier_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


