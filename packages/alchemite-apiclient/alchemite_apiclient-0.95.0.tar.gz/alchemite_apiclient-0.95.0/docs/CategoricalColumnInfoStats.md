# CategoricalColumnInfoStats


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**num_samples** | **int** | The number of non-missing values appearing in this column in the dataset. | [optional]  if omitted the server will use the default value of 0
**categories_present** | **[str]** | The categories that are present for this column in the dataset. If the column is empty, will be empty array. | [optional] 
**mode** | **str, none_type** | The mode of the values appearing in this column in the dataset. If the column is empty, will be set to null. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


