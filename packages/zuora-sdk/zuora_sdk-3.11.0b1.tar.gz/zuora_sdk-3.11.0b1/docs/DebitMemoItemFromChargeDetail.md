# DebitMemoItemFromChargeDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the debit memo item.  **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;224.0&#x60; or later. | [optional] 
**charge_id** | **str** | The ID of the product rate plan charge that the debit memo is created from.  **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | 
**comment** | **str** | Comments about the product rate plan charge.  **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or before. | [optional] 
**description** | **str** | The description of the product rate plan charge.  **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**finance_information** | [**DebitMemoItemFromChargeDetailFinanceInformation**](DebitMemoItemFromChargeDetailFinanceInformation.md) |  | [optional] 
**memo_item_amount** | **float** | The amount of the debit memo item.  **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;224.0&#x60; or later. | [optional] 
**product_rate_plan_charge_id** | **str** | The ID of the product rate plan charge that the debit memo is created from.  **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | 
**quantity** | **float** | The number of units for the debit memo item. | [optional] 
**service_end_date** | **date** | The service end date of the debit memo item. If not specified, the effective end date of the corresponding product rate plan will be used. | [optional] 
**service_start_date** | **date** | The service start date of the debit memo item. If not specified, the effective start date of the corresponding product rate plan will be used. | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the debit memo item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_item_from_charge_detail import DebitMemoItemFromChargeDetail

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoItemFromChargeDetail from a JSON string
debit_memo_item_from_charge_detail_instance = DebitMemoItemFromChargeDetail.from_json(json)
# print the JSON string representation of the object
print(DebitMemoItemFromChargeDetail.to_json())

# convert the object into a dict
debit_memo_item_from_charge_detail_dict = debit_memo_item_from_charge_detail_instance.to_dict()
# create an instance of DebitMemoItemFromChargeDetail from a dict
debit_memo_item_from_charge_detail_from_dict = DebitMemoItemFromChargeDetail.from_dict(debit_memo_item_from_charge_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


