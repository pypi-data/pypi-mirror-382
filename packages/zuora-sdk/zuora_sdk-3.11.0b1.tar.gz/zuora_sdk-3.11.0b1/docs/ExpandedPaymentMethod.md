# ExpandedPaymentMethod


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** |  | [optional] 
**ach_aba_code** | **str** |  | [optional] 
**ach_account_name** | **str** |  | [optional] 
**ach_account_number_mask** | **str** |  | [optional] 
**ach_account_type** | **str** |  | [optional] 
**ach_address1** | **str** |  | [optional] 
**ach_address2** | **str** |  | [optional] 
**ach_bank_name** | **str** |  | [optional] 
**ach_city** | **str** |  | [optional] 
**ach_country** | **str** |  | [optional] 
**ach_postal_code** | **str** |  | [optional] 
**ach_state** | **str** |  | [optional] 
**active** | **bool** |  | [optional] 
**is_system** | **bool** |  | [optional] 
**bank_branch_code** | **str** |  | [optional] 
**bank_check_digit** | **str** |  | [optional] 
**bank_city** | **str** |  | [optional] 
**bank_code** | **str** |  | [optional] 
**bank_identification_number** | **str** |  | [optional] 
**bank_name** | **str** |  | [optional] 
**bank_postal_code** | **str** |  | [optional] 
**bank_street_name** | **str** |  | [optional] 
**bank_street_number** | **str** |  | [optional] 
**bank_transfer_account_name** | **str** |  | [optional] 
**bank_transfer_account_number_mask** | **str** |  | [optional] 
**bank_transfer_account_type** | **str** |  | [optional] 
**bank_transfer_type** | **str** |  | [optional] 
**business_identification_code** | **str** |  | [optional] 
**city** | **str** |  | [optional] 
**country** | **str** |  | [optional] 
**credit_card_address1** | **str** |  | [optional] 
**credit_card_address2** | **str** |  | [optional] 
**credit_card_city** | **str** |  | [optional] 
**credit_card_country** | **str** |  | [optional] 
**credit_card_expiration_month** | **int** |  | [optional] 
**credit_card_expiration_year** | **int** |  | [optional] 
**credit_card_holder_name** | **str** |  | [optional] 
**credit_card_mask_number** | **str** |  | [optional] 
**credit_card_postal_code** | **str** |  | [optional] 
**credit_card_state** | **str** |  | [optional] 
**credit_card_type** | **str** |  | [optional] 
**device_session_id** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**existing_mandate** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**i_ban** | **str** |  | [optional] 
**i_p_address** | **str** |  | [optional] 
**identity_number** | **str** |  | [optional] 
**company_name** | **str** |  | [optional] 
**is_company** | **bool** |  | [optional] 
**last_failed_sale_transaction_date** | **date** |  | [optional] 
**last_name** | **str** |  | [optional] 
**last_transaction_date_time** | **str** |  | [optional] 
**last_transaction_status** | **str** |  | [optional] 
**mandate_creation_date** | **date** |  | [optional] 
**mandate_id** | **str** |  | [optional] 
**mandate_reason** | **str** |  | [optional] 
**mandate_received** | **str** |  | [optional] 
**mandate_status** | **str** |  | [optional] 
**mandate_update_date** | **date** |  | [optional] 
**max_consecutive_payment_failures** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**num_consecutive_failures** | **int** |  | [optional] 
**payment_method_status** | **str** |  | [optional] 
**payment_retry_window** | **int** |  | [optional] 
**paypal_baid** | **str** |  | [optional] 
**paypal_email** | **str** |  | [optional] 
**paypal_preapproval_key** | **str** |  | [optional] 
**paypal_type** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**postal_code** | **str** |  | [optional] 
**second_token_id** | **str** |  | [optional] 
**state** | **str** |  | [optional] 
**street_name** | **str** |  | [optional] 
**street_number** | **str** |  | [optional] 
**token_id** | **str** |  | [optional] 
**total_number_of_error_payments** | **int** |  | [optional] 
**total_number_of_processed_payments** | **int** |  | [optional] 
**type** | **str** |  | [optional] 
**use_default_retry_rule** | **bool** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**card_brand** | **str** |  | [optional] 
**card_class** | **str** |  | [optional] 
**card_product_type** | **str** |  | [optional] 
**card_issuing_bank** | **str** |  | [optional] 
**card_issuing_country** | **str** |  | [optional] 
**method_reference_id** | **str** |  | [optional] 
**user_reference_id** | **str** |  | [optional] 
**sub_type** | **str** |  | [optional] 
**method_specific_data** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_payment_method import ExpandedPaymentMethod

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPaymentMethod from a JSON string
expanded_payment_method_instance = ExpandedPaymentMethod.from_json(json)
# print the JSON string representation of the object
print(ExpandedPaymentMethod.to_json())

# convert the object into a dict
expanded_payment_method_dict = expanded_payment_method_instance.to_dict()
# create an instance of ExpandedPaymentMethod from a dict
expanded_payment_method_from_dict = ExpandedPaymentMethod.from_dict(expanded_payment_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


