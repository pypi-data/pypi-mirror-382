# CoreServiceCreateNewFeatureSetVersionBody


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**schema** | [**[V1FeatureSchema]**](V1FeatureSchema.md) |  | [optional] 
**affected_features** | **[str]** |  | [optional] 
**reason** | **str** |  | [optional] 
**derived_from** | [**V1DerivedInformation**](V1DerivedInformation.md) |  | [optional] 
**primary_key** | **[str]** |  | [optional] 
**use_primary_key_from_previous_version** | **bool** |  | [optional] 
**backfill_options** | [**V1BackfillOptions**](V1BackfillOptions.md) |  | [optional] 
**partition_by** | **[str]** |  | [optional] 
**use_partition_by_from_previous_version** | **bool** |  | [optional] 
**use_time_travel_column_as_partition** | **bool** |  | [optional] 
**feature_set_version** | **str** |  | [optional] 
**time_travel_column** | **str** |  | [optional] 
**time_travel_column_format** | **str** |  | [optional] 
**use_time_travel_column_from_previous_version** | **bool** |  | [optional] 
**use_time_travel_column_format_from_previous_version** | **bool** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


