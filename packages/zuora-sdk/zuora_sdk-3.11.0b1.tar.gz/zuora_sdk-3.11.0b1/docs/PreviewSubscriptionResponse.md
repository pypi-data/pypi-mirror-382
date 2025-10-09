# PreviewSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | Invoice amount. This field is in Zuora REST API version control. Supported minor versions are &#x60;206.0&#x60; and earlier. It is moved to this **invoice** container after 206.0  | [optional] 
**amount_without_tax** | **float** | Invoice amount minus tax. This field is in Zuora REST API version control. Supported minor versions are &#x60;206.0&#x60; and earlier. It is moved to this **invoice** container after 206.0  | [optional] 
**charge_metrics** | [**List[ChargeMetrics]**](ChargeMetrics.md) |  | [optional] 
**contracted_mrr** | **float** | Monthly recurring revenue of the subscription.  | [optional] 
**credit_memo** | [**SubscriptionCreditMemo**](SubscriptionCreditMemo.md) |  | [optional] 
**document_date** | **date** | The date of the billing document, in &#x60;yyyy-mm-dd&#x60; format. It represents the invoice date for invoices, credit memo date for credit memos, and debit memo date for debit memos.   - If this field is specified, the specified date is used as the billing document date.   - If this field is not specified, the date specified in the &#x60;targetDate&#x60; is used as the billing document date. | [optional] 
**invoice** | [**PreviewSubscriptionInvoice**](PreviewSubscriptionInvoice.md) |  | [optional] 
**invoice_items** | [**List[PreviewSubscriptionInvoiceItem]**](PreviewSubscriptionInvoiceItem.md) | Container for invoice items. This field is in Zuora REST API version control. Supported minor versions are &#x60;206.0&#x60; and earlier. It is moved to this **invoice** container after 206.0  | [optional] 
**invoice_target_date** | **date** | Date through which charges are calculated on the invoice, as yyyy-mm-dd.   **Note:** This field is only available if you do not specify the Zuora REST API minor version or specify the minor version to 186.0, 187.0, 188.0, 189.0, 196.0, and 206.0. See [Zuora REST API Versions](https://www.zuora.com/developer/api-references/api/overview/#section/API-Versions) for more information. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**target_date** | **date** | Date through which to calculate charges if an invoice is generated, as yyyy-mm-dd. Default is current date.   **Note:** This field is only available if you set the Zuora REST API minor version to 207.0 or later in the request header. See [Zuora REST API Versions](https://www.zuora.com/developer/api-references/api/overview/#section/API-Versions) for more information. | [optional] 
**tax_amount** | **float** | Tax amount on the invoice. This field is in Zuora REST API version control. Supported minor versions are &#x60;206.0&#x60; and earlier. It is moved to this **invoice** container after 206.0  | [optional] 
**total_contracted_value** | **float** | Total contracted value of the subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.preview_subscription_response import PreviewSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewSubscriptionResponse from a JSON string
preview_subscription_response_instance = PreviewSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(PreviewSubscriptionResponse.to_json())

# convert the object into a dict
preview_subscription_response_dict = preview_subscription_response_instance.to_dict()
# create an instance of PreviewSubscriptionResponse from a dict
preview_subscription_response_from_dict = PreviewSubscriptionResponse.from_dict(preview_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


