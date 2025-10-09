# CreateBillRunRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the bill run.  | [optional] 
**batches** | **List[str]** | The batch of accounts for this bill run.    You can only specify either this field or the &#x60;billRunFilters&#x60; field.   **Values:** &#x60;AllBatches&#x60; or an array of &#x60;Batch*n*&#x60; where *n* is one of numbers 1 - 50, for example, &#x60;Batch7&#x60;. | [optional] 
**bill_cycle_day** | **str** | The day of the bill cycle. This field is only valid if the &#x60;batches&#x60; field is specified.   **Values:**   - &#x60;AllBillCycleDays&#x60; or one of numbers 1 - 31 for an ad-hoc bill run  - &#x60;AllBillCycleDays&#x60;, one of numbers 1 - 31, or &#x60;AsRunDay&#x60; for a scheduled bill run | [optional] 
**bill_run_filters** | [**List[BillRunFilter]**](BillRunFilter.md) | The target account or subscriptions for this bill run. You can only specify either this field or the &#x60;batches&#x60; field. | [optional] 
**bill_run_type** | [**BillRunType**](BillRunType.md) |  | [optional] 
**charge_type_to_exclude** | [**List[ChargeType]**](ChargeType.md) | The types of the charges to be excluded from the generation of billing documents. You can specify at most two charge types in the array. | [optional] 
**auto_email** | **bool** | Whether to automatically send emails after Auto-Post is complete.   **Note:** To use this field, you must first set the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/CB_Billing/Billing_Settings/Define_Billing_Rules\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Support Bill Run Auto-Post?&lt;/a&gt; billing rule to **Yes** through the Zuora UI. | [optional] [default to False]
**auto_post** | **bool** | Whether to automatically post the bill run after the bill run is created.   **Note:** To use this field, you must first set the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/CB_Billing/Billing_Settings/Define_Billing_Rules\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Support Bill Run Auto-Post?&lt;/a&gt; billing rule to **Yes** through the Zuora UI. | [optional] [default to False]
**auto_renewal** | **bool** | Whether to automatically renew auto-renew subscriptions that are up for renewal. | [optional] [default to False]
**no_email_for_zero_amount_invoice** | **bool** | Whether to suppress emails for invoices with zero total amount generated in this bill run after the bill run is complete.    It is best practice to not send emails for invoices with zero amount. | [optional] [default to False]
**schedule** | [**BillRunSchedule**](BillRunSchedule.md) |  | [optional] 
**invoice_date** | **date** | The invoice date for the bill run.    - When creating an ad-hoc bill run, if you do not specify any value for this field, the default value is the current date.  - When creating a scheduled bill run, if you do not specify any value for this field, the invoice date is the value of the &#x60;repeatFrom&#x60; field. | [optional] 
**invoice_date_month_offset** | **int** | The month offset of invoice date for this bill run based on run date, only valid for monthly scheduled bill runs. invoiceDateOffset and invoiceDateMonthOffset/invoiceDateDayOfMonth are mutually exclusive. invoiceDateMonthOffset and invoiceDateDayOfMonth coexist.  | [optional] 
**invoice_date_day_of_month** | **int** | The day of month of invoice date for this bill run, only valid for monthly scheduled bill runs. Specify any day of the month (1-31, where 31 &#x3D; end-of-month). invoiceDateOffset and invoiceDateMonthOffset/invoiceDateDayOfMonth are mutually exclusive. invoiceDateMonthOffset and invoiceDateDayOfMonth coexist.  | [optional] 
**target_date** | **date** | The target date for this bill run.    - You must specify this field when creating an ad-hoc bill run.  - For scheduled bill runs, if you do not specify any value for this field, the target date is the value of the &#x60;repeatFrom&#x60; field. | [optional] 
**target_date_month_offset** | **int** | The month offset of target date for this bill run based on run date, only valid for monthly scheduled bill runs. targetDateOffset and targetDateMonthOffset/targetDateDayOfMonth are mutually exclusive. targetDateMonthOffset and targetDateDayOfMonth coexist.  | [optional] 
**target_date_day_of_month** | **int** | The day of month of target date for this bill run, only valid for monthly scheduled bill runs. Specify any day of the month (1-31, where 31 &#x3D; end-of-month). targetDateOffset and targetDateMonthOffset/targetDateDayOfMonth are mutually exclusive. targetDateMonthOffset and targetDateDayOfMonth coexist.  | [optional] 
**organization_labels** | [**List[OrganizationLabel]**](OrganizationLabel.md) | The organization(s) that the bill run is created for.  For each item in the array, either the &#x60;organizationId&#x60; or the &#x60;organizationName&#x60; field is required.  This field is only required when you have already turned on Multi-Org feature.  | [optional] 
**include_subscriptions** | **bool** | Whether to bill subscriptions.  | [optional] [default to True]
**include_order_line_items** | **bool** |  Whether to bill order line items.  | [optional] [default to True]

## Example

```python
from zuora_sdk.models.create_bill_run_request import CreateBillRunRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBillRunRequest from a JSON string
create_bill_run_request_instance = CreateBillRunRequest.from_json(json)
# print the JSON string representation of the object
print(CreateBillRunRequest.to_json())

# convert the object into a dict
create_bill_run_request_dict = create_bill_run_request_instance.to_dict()
# create an instance of CreateBillRunRequest from a dict
create_bill_run_request_from_dict = CreateBillRunRequest.from_dict(create_bill_run_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


