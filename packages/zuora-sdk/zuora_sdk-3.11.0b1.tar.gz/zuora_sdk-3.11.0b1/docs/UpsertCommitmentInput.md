# UpsertCommitmentInput

Using the action to indicate whether to create or update the commitment.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | [**ActionType**](ActionType.md) |  | 
**commitment_number** | **str** | The number of the Commitment. | 
**name** | **str** | The value to update. Set to null to clear the existing value. | 
**type** | [**CommitmentTypeEnum**](CommitmentTypeEnum.md) |  | 
**description** | **str** | The value to update. Set to null to clear the existing value. | [optional] 
**priority** | **int** | It defines the evaluation order of the commitment, the lower the number, the higher the priority. when two commitments have the same priority, the one with the earlier created one time will be evaluated first. | [optional] 
**association_rules** | [**List[AssociationRule]**](AssociationRule.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an commitment Segment object. | [optional] 
**accounting_code** | **str** | The accounting code for the Commitment.  | [optional] 
**adjustment_liability_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**adjustment_revenue_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_asset_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_liability_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_recognized_revenue_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**deferred_revenue_accounting_code** | **str** | The deferred revenue accounting code for the Commitment.  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude Commitment related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.   **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**is_allocation_eligible** | **bool** | This field is used to identify if the charge segment is allocation eligible in revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**is_unbilled** | **bool** | This field is used to dictate how to perform the accounting during revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**recognized_revenue_accounting_code** | **str** | The recognized revenue accounting code for the Commitment.  | [optional] 
**revenue_recognition_rule** | **str** | The Revenue Recognition rule for the Commitment.  | [optional] 
**account_receivable_accounting_code** | **str** | The accounting code on the Commitment object for customers | [optional] 
**unbilled_receivables_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**revenue_recognition_timing** | **str** | This field is used to dictate the type of revenue recognition timing. | [optional] 
**revenue_amortization_method** | **str** | This field is used to dictate the type of revenue amortization method. | [optional] 
**taxable** | **bool** | The flag to indicate whether the charge is taxable. If this field is set to true, both the fields &#x60;taxCode&#x60; and &#x60;taxMode&#x60; are required.  | [optional] 
**tax_code** | **str** | The taxCode of a charge. This field is available when the field &#39;taxable&#39; is set to true.  | [optional] 
**tax_mode** | **str** | The taxMode of a charge.  Values: * &#x60;TaxExclusive&#x60; * &#x60;TaxInclusive&#x60; This field is available when the field &#39;taxable&#39; is set to true.  | [optional] 
**currency** | **str** |  | 
**periods** | [**List[UpsertCommitmentPeriodInput]**](UpsertCommitmentPeriodInput.md) |  | 

## Example

```python
from zuora_sdk.models.upsert_commitment_input import UpsertCommitmentInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCommitmentInput from a JSON string
upsert_commitment_input_instance = UpsertCommitmentInput.from_json(json)
# print the JSON string representation of the object
print(UpsertCommitmentInput.to_json())

# convert the object into a dict
upsert_commitment_input_dict = upsert_commitment_input_instance.to_dict()
# create an instance of UpsertCommitmentInput from a dict
upsert_commitment_input_from_dict = UpsertCommitmentInput.from_dict(upsert_commitment_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


