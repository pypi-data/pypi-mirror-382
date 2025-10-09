# CreateProductRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**integration_status__ns** | **str** | Status of the product&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**item_type__ns** | [**ProductObjectNSFieldsItemTypeNS**](ProductObjectNSFieldsItemTypeNS.md) |  | [optional] 
**sync_date__ns** | **str** | Date when the product was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**sku** | **str** | The unique SKU for the product.  **Values**:    - leave null for automatically generated string   - an alphanumeric string of 50 characters or fewer  | [optional] 
**name** | **str** | The name of the product. This information is displayed in the product catalog pages in the web-based UI. | 
**product_number** | **str** | The natural key of the product.   **Values**:    - leave null for automatically generated string   - an alphanumeric string of 100 characters or fewer  **Note**: This field is only available if you set the &#x60;X-Zuora-WSDL-Version&#x60; request header to &#x60;133&#x60; or later. | [optional] 
**category** | [**ProductCategory**](ProductCategory.md) |  | [optional] 
**description** | **str** | A description of the product.  | [optional] 
**effective_start_date** | **date** | The date when the product becomes available and can be subscribed to, in &#x60;yyyy-mm-dd&#x60; format. | 
**effective_end_date** | **date** | The date when the product expires and can&#39;t be subscribed to anymore, in &#x60;yyyy-mm-dd&#x60; format. | 
**allow_feature_changes** | **bool** | Controls whether to allow your users to add or remove features while creating or amending a subscription.   **Values**: true, false (default) | [optional] 

## Example

```python
from zuora_sdk.models.create_product_request import CreateProductRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateProductRequest from a JSON string
create_product_request_instance = CreateProductRequest.from_json(json)
# print the JSON string representation of the object
print(CreateProductRequest.to_json())

# convert the object into a dict
create_product_request_dict = create_product_request_instance.to_dict()
# create an instance of CreateProductRequest from a dict
create_product_request_from_dict = CreateProductRequest.from_dict(create_product_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


