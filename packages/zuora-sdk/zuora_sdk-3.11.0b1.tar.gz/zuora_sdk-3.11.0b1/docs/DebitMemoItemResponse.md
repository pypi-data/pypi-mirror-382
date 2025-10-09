# DebitMemoItemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**amount** | **float** | The amount of the debit memo item. For tax-inclusive debit memo items, the amount indicates the debit memo item amount including tax. For tax-exclusive debit memo items, the amount indicates the debit memo item amount excluding tax. | [optional] 
**amount_without_tax** | **float** | The debit memo item amount excluding tax. | [optional] 
**applied_to_item_id** | **str** | The parent debit memo item that this debit memo items is applied to if this item is discount. | [optional] 
**balance** | **float** | The balance of the debit memo item. | [optional] 
**be_applied_amount** | **float** | The applied amount of the debit memo item. | [optional] 
**comment** | **str** | Comments about the debit memo item.  **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the debit memo item. | [optional] 
**created_date** | **str** | The date and time when the debit memo item was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**description** | **str** | The description of the debit memo item.  **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the debit memo item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**finance_information** | [**GetDebitMemoItemFinanceInformation**](GetDebitMemoItemFinanceInformation.md) |  | [optional] 
**id** | **str** | The ID of the debit memo item. | [optional] 
**processing_type** | [**BillingDocumentItemProcessingType**](BillingDocumentItemProcessingType.md) |  | [optional] 
**quantity** | **float** | The number of units for the debit memo item. | [optional] 
**reflect_discount_in_net_amount** | **bool** | The flag to reflect Discount in Apply To Charge Net Amount.  | [optional] 
**service_end_date** | **date** | The end date of the service period associated with this debit memo item. Service ends one second before the date specified in this field. | [optional] 
**service_start_date** | **date** | The start date of the service period associated with this debit memo item. If the associated charge is a one-time fee, this date is the date of that charge. | [optional] 
**ship_to_contact_id** | **str** | The ID of the ship-to contact associated with the debit memo item.  The value of this field is &#x60;null&#x60; if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled. | [optional] 
**sku** | **str** | The SKU for the product associated with the debit memo item. | [optional] 
**sku_name** | **str** | The name of the SKU. | [optional] 
**sold_to_contact_id** | **str** | The ID of the sold-to contact associated with the debit memo item.  The value of this field is &#x60;null&#x60; if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled. | [optional] 
**sold_to_contact_snapshot_id** | **str** | The ID of the sold-to contact snapshot associated with the invoice item.  The value of this field is &#x60;null&#x60; if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled.                 | [optional] 
**source_item_id** | **str** | The ID of the source item. | [optional] 
**source_item_type** | [**BillingDocumentItemSourceType**](BillingDocumentItemSourceType.md) |  | [optional] 
**subscription_id** | **str** | The ID of the subscription associated with the debit memo item. | [optional] 
**tax_items** | [**List[GetDebitMemoTaxItem]**](GetDebitMemoTaxItem.md) | Container for the taxation items of the debit memo item.   **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;239.0&#x60; or later.  | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**taxation_items** | [**DebitMemoItemTaxationItems**](DebitMemoItemTaxationItems.md) |  | [optional] 
**unit_of_measure** | **str** | The units to measure usage. | [optional] 
**unit_price** | **float** | The per-unit price of the debit memo item. | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the debit memo item. | [optional] 
**updated_date** | **str** | The date and time when the debit memo item was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_item_response import DebitMemoItemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoItemResponse from a JSON string
debit_memo_item_response_instance = DebitMemoItemResponse.from_json(json)
# print the JSON string representation of the object
print(DebitMemoItemResponse.to_json())

# convert the object into a dict
debit_memo_item_response_dict = debit_memo_item_response_instance.to_dict()
# create an instance of DebitMemoItemResponse from a dict
debit_memo_item_response_from_dict = DebitMemoItemResponse.from_dict(debit_memo_item_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


