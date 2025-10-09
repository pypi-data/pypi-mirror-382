# SubmitDataLabelingJobRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | **List[str]** | The IDs of the objects to be labeled, only required if the &#x60;queryType&#x60; is &#x60;ById&#x60;.   There is a 4MB limit of the JSON payload, so in case of a large number of IDs, please make sure the payload is less than 4MB. | [optional] 
**object_type** | **str** | The object type of the data labeling job.  Currently, the following objects are supported:   * &#x60;User&#x60;   * &#x60;Account&#x60;       All the associated transaction objects of the account being labeled will automatically inherit the org label of the account.   * &#x60;Product&#x60;      You have to label the Account object first, make sure all accounts have been labeled, then you can proceed with the Product object.       You can get all the unlabeled accounts by running a Data Source export job, with the following query:     &#x60;&#x60;&#x60; sql     SELECT Id, Name FROM Account WHERE Organization.Id IS NULL     &#x60;&#x60;&#x60;                        All the ProductRatePlanS of the product will be automatically labeled with the same &#x60;orgs&#x60;.          When labeling products, you can omit the &#x60;orgs&#x60; parameter, i.e, leave it empty, the system will find all the subscriptions that include the product and get the org list of those subscriptions, then label the product with those &#x60;orgs&#x60;, aka, the &#x60;derived orgs&#x60;.          You can also explicitly specify the orgs parameter, in that case, you will need to provide a super set of the &#x60;derived orgs&#x60;.     * &#x60;BillRun&#x60;      You don&#39;t need to specify the &#x60;orgs&#x60; parameter, we will label the &#x60;BillRun&#x60; with all the orgs because existing runs could pick up all accounts. You can definitely create new bill run with certain &#x60;orgs&#x60; to operate separately by &#x60;orgs&#x60;.   * &#x60;PaymentRun&#x60;      Same as BillRun.   * &#x60;ForecastRun&#x60;  | 
**org_ids** | **List[str]** | The IDs of the organizations that the data labeling job will associate with the data to be labeled. Either the &#x60;orgIds&#x60; or &#x60;orgs&#x60; field is required.   For &#x60;Account&#x60; object, one and only one org Id is required.   For configuration objects, &#x60;null&#x60; and &#x60;[]&#x60; are treated differently, use &#x60;null&#x60; to unlabel the object, &#x60;[]&#x60; to label it with all orgs. | [optional] 
**orgs** | **List[str]** | The names of the organizations that the data labeling job will associate with the data to be labeled. Either the &#x60;orgIds&#x60; or &#x60;orgs&#x60; field is required.   For &#x60;Account&#x60; object, one and only one org name is required.   For configuration objects, &#x60;null&#x60; and &#x60;[]&#x60; are treated differently, use &#x60;null&#x60; to unlabel the object, &#x60;[]&#x60; to label it with all orgs. | [optional] 
**query** | **str** | The query that the data labeling job will run to fetch the data to be labeled, only required if the &#x60;queryType&#x60; is &#x60;ByZoql&#x60;. | [optional] 
**query_type** | **str** | Specifies the type of query that the data labeling job will run to fetch the data to be labeled.   * &#x60;ByZoql&#x60; - The data labeling job will run a ZOQL query which is specified in the &#x60;query&#x60; field to fetch the data to be labeled.  * &#x60;ById&#x60; - The data labeling job will fetch the data to be labeled by the IDs specified in the &#x60;ids&#x60; field. | 

## Example

```python
from zuora_sdk.models.submit_data_labeling_job_request import SubmitDataLabelingJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitDataLabelingJobRequest from a JSON string
submit_data_labeling_job_request_instance = SubmitDataLabelingJobRequest.from_json(json)
# print the JSON string representation of the object
print(SubmitDataLabelingJobRequest.to_json())

# convert the object into a dict
submit_data_labeling_job_request_dict = submit_data_labeling_job_request_instance.to_dict()
# create an instance of SubmitDataLabelingJobRequest from a dict
submit_data_labeling_job_request_from_dict = SubmitDataLabelingJobRequest.from_dict(submit_data_labeling_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


