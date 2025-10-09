# SubscriptionCreditMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount_without_tax** | **float** | The credit memo item amount excluding tax.  | [optional] 
**charge_amount** | **float** | The amount of the credit memo item. For tax-inclusive credit memo items, the amount indicates the credit memo item amount including tax. For tax-exclusive credit memo items, the amount indicates the credit memo item amount excluding tax | [optional] 
**charge_description** | **str** | Description of this credit memo item.  | [optional] 
**charge_name** | **str** | Name of this credit memo item.  | [optional] 
**product_name** | **str** | Name of the product associated with this credit memo item.  | [optional] 
**product_rate_plan_charge_id** | **str** | ID of the product rate plan charge associated with this credit memo item.  | [optional] 
**quantity** | **int** | Quantity of the charge associated with this credit memo item.  | [optional] 
**service_end_date** | **date** | End date of the service period for this credit memo item, as yyyy-mm-dd.  | [optional] 
**service_start_date** | **date** | Service start date of this credit memo item, as yyyy-mm-dd.  | [optional] 
**tax_amount** | **float** | The tax amount of the credit memo item.  | [optional] 
**taxation_items** | [**List[SubscriptionTaxationItem]**](SubscriptionTaxationItem.md) | List of taxation items.  **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;315.0&#x60; or later.  | [optional] 
**unit_of_measure** | **str** | Unit used to measure consumption. | [optional] 

## Example

```python
from zuora_sdk.models.subscription_credit_memo_item import SubscriptionCreditMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionCreditMemoItem from a JSON string
subscription_credit_memo_item_instance = SubscriptionCreditMemoItem.from_json(json)
# print the JSON string representation of the object
print(SubscriptionCreditMemoItem.to_json())

# convert the object into a dict
subscription_credit_memo_item_dict = subscription_credit_memo_item_instance.to_dict()
# create an instance of SubscriptionCreditMemoItem from a dict
subscription_credit_memo_item_from_dict = SubscriptionCreditMemoItem.from_dict(subscription_credit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


