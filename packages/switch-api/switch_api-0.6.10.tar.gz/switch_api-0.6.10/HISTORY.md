# History

# 0.6.7

### Modified
In the `integration` module
- Computing of carbon calculation expressions is refactored for efficiency, utilizing `numexpr` library for faster evaluation of Carbon Calculation Expressions


# 0.6.6

### Modified

In the `integration` module:

- `send_reading_summaries()` method now rounds up float values for Value, Cost, and Carbon to 4 decimal places before sending to Reading Summaries API Endpoint

# 0.6.5

### Modified

In the `integration` module:

- Refactored the `send_reading_summaries()` method to compute daily totals for Carbon, Cost, and Value directly within the method.
  - This update is internal and does **not** require any changes to the input dataframe used by `upsert_timeseries()`.
  - This update still requires the `generate_summaries` parameter to be `True` to generate reading summaries.
  - If generate_summaries parameter is set to True it requires that the dataframe passed to upsert_timeseries method contains the complete interval records for a given Calendar day. It can't be a partial day worth of data.
- Added a new error type: `ReadingSummariesTimeout` to improve categorization and handling of timeouts specifically related to reading summaries.

In the `_utils` module:

- Set max retries to 10 if more than 10 was passed in the `requests_retry_session2()` method


## 0.6.2

### Modified 

In the `integration` module: 

- Added new functionality to the helper method `update_last_record()` and renamed to `update_last_record_property_value()`
    - Requires additional column to be included on the `pandas.Dataframe` passed via the `df` called `Value` 
      which contains the Value at the UTC datetime of `LastRecord`
    - This helper method is called internally to the `upsert_timeseries()` method

## 0.6.0

### Added

In the `integration` module:

- Added new helper method `update_last_record()` to update the the last record datetime for sensors.
  - This method is called internally within the `upsert_timeseries()` method and sets the last record for each sensor to their maximum datetime present in the data_frame passed.

### Modified

In the `integration` module:

- Added optional columns `ImportStatus`, `PointClassName` and `EntityClassName` to the defined column list for the dataframe passed to the `upsert_discovered_records()` method.
  - Allowed Values for the `ImportStatus` column are:
  - The `PointClassName` and `EntityClassName` fields allow the brick class for a given point and piece of equipment to be defined as part of the upsert. The `EquipmentLabel` required field is used to set the EntityName.
- Added optional columns `PointClassName` and `EntityClassName` to the defined column list for the dataframe passed to `upsert_device_sensors()` method.
  - The `PointClassName` and `EntityClassName` fields allow the brick class for a given point and piece of equipment to be defined as part of the upsert. The `EquipmentLabel` required field is used to set the EntityName.

In the `automation` module:

- Added optional parameter `run_in_minutes` to delay running of datafeed in minutes.
  - This parameter is set to 0 (zero) by default.
- Updated the `register_task()` method to check whether the `TaskID` and/or the `TaskName` already exist before registering.

In the `utils` module:

- When uploading CSV files for ingestion, we now partitioned those into max 3mb per file.
  - This impacts primarily on the upsert_timeseries() method which started to hit max limits for streaming ingestion to adx.

## 0.5.14

### Added

In the `integration` module:

- Added `generate_summaries` flag which defaults to `True` which tells whether to send a request or not to
  generate summaries for the given datetimes from the passed dataframe readings.

## 0.5.12

### Added

In the `compute` module:

- Added `CostCarbonCalculation` class that handles the calculation of Carbon
  - Has a method called `compute_carbon` to calculate Carbon for sensors

In the `ApiInputs` object from `initialize`:

- Added `iot_url` as config to use across python modules

## 0.5.11

### Added

In the `controls` module:

- Added `submit_control_continue` method to handle control requests with continuation logic
- Added `add_control_component` method in conjunction to `submit_control_continue` method to set control components
  that details the column mapping for the required data frame to send control requests.

## 0.5.10

### Added

In the `controls` module:

- Added handling of `DefautlControlValue` column for `submit_control_request` method
- For sensors without Priority Array, if control command has timeout then this field if existing will be used on revert (otherwise the present value before write is used).
- DefaultControlValue will be ignored for sensors with priority array.

## 0.5.8

### Fixed

In the `analytics` module:

- Fixed bug on AU datacentre API endpoint construction.

## 0.5.7

### Modified

In the `controls` module:

- Modified `submit_control` method
  - Returns sensor control values upon control request acknowledgement

## 0.5.5

### Added

In the `pipeline` module:

- Added a new task `IQTask`
  - Additional abstract property `module_type` that accepts strings. This should define the type of IQ module.
  - Abstract method `process` must be instantiated for the task to be registered.

### Modified

In the `pipeline` module:

- Updated the `Automation.register_task()` method to accept tasks that subclass the new `IQTask`.

## 0.5.4

### Added

In the `integration` module:

- Added new function `upsert_reservations()`
  - Upserts data to the ReservationHistory table
  - Two attributes added to assist with creation of the input dataframe:
    - `upsert_reservations.df_required_columns` - returns list of required columns for the input `df`
    - `upsert_reservations.df_optional_columns` - returns list of required columns for the input `df`
  - The following datetime fields are required and must use the `local_date_time_cols` and `utc_date_time_cols`
    parameters to define whether their values are in site-local timezone or UTC timezone:
    - `CreatedDate`
    - `LastModifiedDate`
    - `ReservationStart`
    - `ReservationEnd`
- Added new function `upsert_device_sensors_iq`
  - Same functionality with `upsert_device_sensors` but modified/simplified to work with Switch IQ
  - 'Tags' are included in each row of passing dataframe for upsert instead of a separate list in the original

In the `authentication` module:

- Customized `get_switch_credentials` with custom port instead of a fixed one
  - `initialize` function now has `custom_port` parameter for custom port settings when authenticating

In the `controls` module:

- Modified `submit_control` functon to return consolidated dataframe with added columns: `status` and `writeStatus`
  that flags whether the control request was successful or not. Instead of the previous 2 separate dataframes
- Modified `submit_control` function as well to have paginated processing of dataframe to submit control instead of
  sending them all in one go
- Modified `_mqtt` class to add Gateway Connected check before sending/submitting control request to the MQTT Broker.

## 0.5.3

### Added

- In the `integration` module:
  - Added `override_existing` parameter in `upsert_discovered_records`
    - Flag if it the values passed to df will override existing integration records. Only valid if running locally,
      not on a deployed task where it is triggered via UI.
    - Defaults to False

## 0.5

### Added

- In the `pipeline` module:
  - Added a new task type called `Guide`.
    - this task type should be sub-classed in concert with one of the Task sub-classes when deploying a guide to the
      marketplace.
  - Added a new method to the `Automation` class called `register_guide_task()`
    - this method is used to register tasks that sub-class the `Guide` task and also posts form files to blob and
      registers the guide to the Marketplace.
- New `_guide` module - only to be referenced when doing initial development of a Guide
  - `guide`'s `local_start' method
    - Allows to run mock guides engine locally that ables to debug `Guide` task types with Form Kit playground.

### Fixed

- In `controls` module:
  - modify `submit_control` method parameters - typings
  - remove extra columns from payload to IoT API requests

## 0.4.9

### Added

- New method added in `automation` module:
  - `run_data_feed()` - Run python job based on data feed id. This will be sent to the queue for processing and will
    undergo same procedure as the rest of the datafeed.
    - Required parameters are `api_inputs` and `data_feed_id`
    - This has a restriction of only allowing an AnalyticsTask type datafeed to be run and deployed as a Timer
- New method added in `analytics` module:
  - `upsert_performance_statistics` - this method should only be used by tasks used to populate the Portfolio
    Benchmarking feature in the Switch Automation platform
- New `controls` module added and new method added to this module:
  - `submit_control()` - method to submit control of sensors
    - this method returns a tuple: `(control_response, missing_response)`:
      - `control_response` - is the list of sensors that are acknowledged and process by the MQTTT message broker
      - `missing_response` = is the list of sensors that are sensors that were caught by the connection `time_out` -
        default to 30 secs - meaning the response were no longer waited to be received by the python package.
        Increasing the time out can potentially help with this.

### Fixed

- In the `integration` module, minor fixes to:
  - An unhandled exception when using `pandas==2.1.1` on the following functions:
    - `upsert_sites()`
    - `upsert_device_sensors()`
    - `upsert_device_sensors_ext()`
    - `upsert_workorders()`
    - `upsert_timeseries_ds()`
    - `upsert_timeseries()`
  - Handle deprecation of `pandas.DataFrame.append()` on the following functions:
    - `upsert_device_sensors()`
    - `upsert_device_sensors_ext()`
  - An unhandled exception for `connect_to_sql()` function when the internal API call within
    `_get_sql_connection_string()` fails.

## 0.4.8

### Added

- New class added to the `pipeline` module:
  - `BlobTask` - This class is used to create integrations that post data to the Switch Automation Platform using a
    blob container & Event Hub Queue as the source.
    - Please Note: This task type requires external setup in Azure by Switch Automation Developers before a task can be
      registered or deployed.
    - requires `process_file()` abstract method to be created when sub-classing
- New method, `deploy_as_on_demand_data_feed()` added to the `Automation` class of the `pipeline` module
  - this new method is only applicable for tasks that subclass the `BlobTask` base class.
- In the `integration` module, new helper methods have been added:
  - `connect_to_sql()` method creates a pyodbc connection object to enable easier querying of the SQL database via the
    `pyodbc` library
  - `amortise_across_days()` method enables easier amortisation of data across days in a period, either inclusive or
    exclusive of end date.
  - `get_metadata_where_clause()` method enables creation of `sql_where_clause` for the `get_device_sensors`() method
    where for each metadata key the sql checks its not null.
- In the `error_handlers` module:
  - `check_duplicates()` method added to check for duplicates & post appropriate errors to Task Insights UI in the
    Switch Automation platform.
- In the `_utils._utils` module:
  - `requests_retry_session2` helper function added to enable automatic retries of API calls

### Updated

- In the `integration` module:

  - New parameter `include_removed_sites` added to the `get_sites()` function.
    - Determines whether or not to include sites marked as "IsRemoved" in the returned dataframe.
    - Defaults to False, indicating removed sites will not be included.
  - Updated the`get_device_sensor()` method to check if requested metadata keys or requested
    tag groups exist for the portfolio and exception if they don't.
  - New parameter `send_notification` added to the `upsert_timeseries()` function.
    - This enables Iq Notification messages to be sent when set to `True`
    - Defaults to `False`
  - For the `get_sites()`, `get_device_sensors()` and `get_data()` functions, additional parameters have
    been added to allow customisation of the newly implemented retry logic:
    - `retries : int`
      - Number of retries performed beforereturning last retry instance's response status. Max retries = 10.
        Defaults to 0 currently for backwards compatibility.
    - `backoff_factor`
      - If A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
        second try without a delay).
        {_backoff factor_} \* (2 \*\* ({_retry count_} - 1)) seconds

- In the `error_handlers` module:
  - For the `validate_datetime` function, added two new parameters to enable automatic
    posting of errors to the Switch Platform:
    - `errors` : boolean, defaults to False. To enable posting of errors, set to True.
    - `api_inputs`: defaults to None. Needs to be set to the object returned from switch_api.initialize() if `errors=True`.

### Fixed

- In the `integration` module:
  - Resolved outlier scenario resulting in unhandled exception on the `upsert_sites()` function.
  - Minor fix to the `upsert_discovered_records()` method to handle the case when unexpected columns
    are present in the dataframe passed to `df` input parameter

## 0.4.6

### Added

- Task Priority and Task Framework data feed deployment settings
  - Task Priority and Task Framework are now available to set when deploying data feeds
    - Task Priority
      - Determines the priority of the datafeed tasks when processing.
      - This equates to how much resources would be alloted to run the task
      - Available options are: `default`, `standard`, or `advanced`.
        - set to `advanced` for higher resource when processing data feed task
      - Defaults to 'default'.
    - Task Framework
      - Determines the framework of the datafeed tasks when processing.
        - 'PythonScriptFramework' for the old task runner engine.
        - 'TaskInsightsEngine' for the new task running in container apps.
        - Defaults to 'PythonScriptFramework'

## 0.4.5

### Added

- Email Sender Module
  - Send emails to active users within a Portfolio in Switch Automation Platform
  - Limitations:
    - Emails cannot be sent to users outside of the Portfolio including other users within the platform
    - Maximum of five attachments per email
    - Each attachment has a maximum size of 5mb
  - See function code documentation and usage example below
- New `generate_filepath` method to provide a filepath where files can be stored
  - Works well with the attachment feature of the Email Sender Module. Store files in the generated filepath of this method and pass into email attachments
  - See function code documentation and usage example below

### Email Sender Usage

```python
import switch_api as sw

sw.email.send_email(
    api_inputs=api_inputs,
    subject='',
    body='',
    to_recipients=[],
    cc_recipients=[], # Optional
    bcc_recipients=[], # Optional
    attachments=['/file/path/to/attachment.csv'], # Optional
    conversation_id='' # Optional
)
```

### generate_filepath Usage

```python
import switch_api as sw

generated_attachment_filepath = sw.generate_filepath(api_inputs=api_inputs, filename='generated_attachment.txt')

# Example of where it could be used
sw.email.send_email(
    ...
    attachments=[generated_attachment_filepath]
    ...
)
```

### Fixed

- Issue where `upsert_device_sensors_ext` method was not posting metadata and tag_columns to API

## 0.3.3

### Added

- New `upsert_device_sensors_ext` method to the `integration` module.
  - Compared to existing `upsert_device_sensors` following are supported:
    - Installation Code or Installation Id may be provided
      - BUT cannot provide mix of the two, all must have either code or id and not both.
    - DriverClassName
    - DriverDeviceType
    - PropertyName

### Added Feature - Switch Python Extensions

- Extensions may be used in Task Insights and Switch Guides for code reuse
- Extensions maybe located in any directory structure within the repo where the usage scripts are located
- May need to adjust your environment to detect the files if you're not running a project environment
  - Tested on VSCode and PyCharm - contact Switch Support for issues.

#### Extensions Usage

```python
import switch_api as sw

# Single import line per extension
from extensions.my_extension import MyExtension

@sw.extensions.provide(field="some_extension")
class MyTask:
    some_extension: MyExtension

if __name__ == "__main__":
    task = MyTask()
    task.some_extension.do_something()
```

#### Extensions Registration

```python
import uuid
import switch_api as sw

class SimpleExtension(sw.extensions.ExtensionTask):
    @property
    def id(self) -> uuid.UUID:
        # Unique ID for the extension.
        # Generate in CLI using:
        #   python -c 'import uuid; print(uuid.uuid4())'
        return '46759cfe-68fa-440c-baa9-c859264368db'

    @property
    def description(self) -> str:
        return 'Extension with a simple get_name function.'

    @property
    def author(self) -> str:
        return 'Amruth Akoju'

    @property
    def version(self) -> str:
        return '1.0.1'

    def get_name(self):
        return "Simple Extension"

# Scaffold code for registration. This will not be persisted in the extension.
if __name__ == '__main__':
    task = SimpleExtension()

    api_inputs = sw.initialize(api_project_id='<portfolio-id>')

    # Usage test
    print(task.get_name())

    # =================================================================
    # REGISTER TASK & DATAFEED ========================================
    # =================================================================
    register = sw.pipeline.Automation.register_task(api_inputs, task)
    print(register)

```

### Updated

- get_data now has an optional parameter to return a pandas.DataFrame or JSON

## 0.2.27

### Fix

- Issue where Timezone DST Offsets API response of `upsert_timeseries` in `integration` module was handled incorrectly

## 0.2.26

### Updated

- Optional `table_def` parameter on `upsert_data`, `append_data`, and `replace_data` in `integration` module
  - Enable clients to specify the table structure. It will be merged to the inferred table structure.
- `list_deployments` in Automation module now provides `Settings` and `DriverId` associated with the deployments

## 0.2.25

### Updated

- Update handling of empty Timezone DST Offsets of `upsert_timeseries` in `integration` module

## 0.2.24

### Updated

- Fix default `ingestion_mode` parameter value to 'Queue' instead of 'Queued' on `upsert_timeseries` in `integration` module

## 0.2.23

### Updated

- Optional `ingestion_mode` parameter on `upsert_timeseries` in `integration` module
  - Include `ingestionMode` in json payload passed to backend API
  - `IngestionMode` type must be `Queue` or `Stream`
  - Default `ingestion_mode` parameter value in `upsert_timeseries` is `Queue`
  - To enable table streaming ingestion, please contact **helpdesk@switchautomation.com** for assistance.

## 0.2.22

### Updated

- Optional `ingestion_mode` parameter on `upsert_data` in `integration` module
  - Include `ingestionMode` in json payload passed to backend API
  - `IngestionMode` type must be `Queue` or `Stream`
  - Default `ingestion_mode` parameter value in `upsert_data` is `Queue`
  - To enable table streaming ingestion, please contact **helpdesk@switchautomation.com** for assistance.

### Fix

- sw.pipeline.logger handlers stacking

## 0.2.21

### Updated

- Fix on `get_data` method in `dataset` module
  - Sync parameter structure to backend API for `get_data`
  - List of dict containing properties of `name`, `value`, and `type` items
  - `type` property must be one of subset of the new Literal `DATA_SET_QUERY_PARAMETER_TYPES`

## 0.2.20

### Added

- Newly supported Azure Storage Account: GatewayMqttStorage
- An optional property on QueueTask to specific QueueType
  - Default: DataIngestion

## 0.2.19

### Fixed

- Fix on `upsert_timeseries` method in `integration` module
  - Normalized TimestampId and TimestampLocalId seconds
- Minor fix on `upsert_entities_affected` method in `integration` utils module
  - Prevent upsert entities affected count when data feed file status Id is not valid
- Minor fix on `get_metadata_keys` method in `integration` helper module
  - Fix for issue when a portfolio does not contain any values in the ApiMetadata table

## 0.2.18

### Added

- Added new `is_specific_timezone` parameter in `upsert_timeseries` method of `integration` module

  - Accepts a timezone name as the specific timezone used by the source data.
  - Can either be of type str or bool and defaults to the value of False.
  - Cannot have value if 'is_local_time' is set to True.
  - Retrieve list of available timezones using 'get_timezones' method in `integration` module

    | is_specific_timezone | is_local_time | Description                                                                                                                                                     |
    | -------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | False                | False         | Datetimes in provided data is already in UTC and should remain as the value of Timestamp. The TimestampLocal (conversion to site-local Timezone) is calculated. |
    | False                | True          | Datetimes in provided data is already in the site-local Timezone & should be used to set the value of the TimestampLocal field. The UTC Timestamp is calculated |
    | Has Value            | True          | NOT ALLOWED                                                                                                                                                     |
    | Has Value            | False         | Both Timestamp and TimestampLocal fields will are calculated. Datetime is converted to UTC then to Local.                                                       |
    | True                 |               | NOT ALLOWED                                                                                                                                                     |
    | '' (empty string)    |               | NOT ALLOWED                                                                                                                                                     |

### Fixed

- Minor fix on `upsert_tags` and `upsert_device_metadata` methods in `integration` module
  - List of required_columns was incorrectly being updated when these functions were called
- Minor fix on `upsert_event_work_order_id` method in `integration` module when attempting to update status of an Event

### Updated

- Update on `DiscoveryIntegrationInput` namedtuple - added `job_id`
- Update `upsert_discovered_records` method required columns in `integration` module
  - add required `JobId` column for Data Frame parameter

## 0.2.17

### Fixed

- Fix on `upsert_timeseries()` method in `integration` module for duplicate records in ingestion files
  - records whose Timestamp falls in the exact DST start created 2 records with identical values but different TimestampLocal
    - one has the TimestampLocal of a DST and the other does not

### Updated

- Update on `get_sites()` method in `integration` module for `InstallationCode` column
  - when the `InstallationCode' value is null in the database it returns an empty string
  - `InstallationCode` column is explicity casted to dtype 'str'

## 0.2.16

### Added

- Added new 5 minute interval for `EXPECTED_DELIVERY` Literal in `automation` module
  - support for data feed deployments Email, FTP, Upload, and Timer
  - usage: expected_delivery='5min'

### Fixed

- Minor fix on `upsert_timeseries()` method using `data_feed_file_status_id` parameter in `integration` module.
  - `data_feed_file_status_id` parameter value now synced between process records and ingestion files when supplied

### Updated

- Reduced ingestion files records chunking by half in `upsert_timeseries()` method in `integration` module.
  - from 100k records chunk down to 50k records chunk

## 0.2.15

### Updated

- Optimized `upsert_timeseries()` method memory upkeep in `integration` module.

## 0.2.14

### Fixed

- Minor fix on `invalid_file_format()` method creating structured logs in `error_handlers` module.

## 0.2.13

### Updated

- Freeze Pandera[io] version to 0.7.1
  - PandasDtype has been deprecated since 0.8.0

### Compatibility

- Ensure local environment is running Pandera==0.7.1 to match cloud container state
- Downgrade/Upgrade otherwise by running:
  - pip uninstall pandera
  - pip install switch_api

## 0.2.12

### Added

- Added `upsert_tags()` method to the `integration` module.
  - Upsert tags to existing sites, devices, and sensors
  - Upserting of tags are categorised by the tagging level which are Site, Device, and Sensor level
  - Input dataframe requires `Identifier' column whose value depends on the tagging level specified
    - For Site tag level, InstallationIds are expected to be in the `Identifier` column
    - For Device tag level, DeviceIds are expected to be in the `Identifier` column
    - For Sensor tag level, ObjectPropertyIds are expected to be in the `Identifier` column
- Added `upsert_device_metadata()` method to the `integration` module.
  - Upsert metadata to existing devices

### Usage

- `upsert_tags()`
  - sw.integration.upsert_tags(api_inputs=api_inputs, df=raw_df, tag_level='Device')
  - sw.integration.upsert_tags(api_inputs=api_inputs, df=raw_df, tag_level='Sensor')
  - sw.integration.upsert_tags(api_inputs=api_inputs, df=raw_df, tag_level='Site')
- `upsert_device_metadata()`
  - sw.integration.upsert_device_metadata(api_inputs=api_inputs, df=raw_df)

## 0.2.11

### Added

- New `cache` module that handles cache data related transactions
  - `set_cache` method that stores data to cache
  - `get_cache` method that gets stored data from cache
  - Stored data can be scoped / retrieved into three categories namely Task, Portfolio, and DataFeed scopes
    - For Task scope,
      - Data cache can be retrieved by any Portfolio or Datafeed that runs in same Task
      - provide TaskId (self.id when calling from the driver)
    - For DataFeed scope,
      - Data cache can be retrieved (or set) within the Datafeed deployed in portfolio
      - Provide UUID4 for local testing. api_inputs.data_feed_id will be used when running in the cloud.
    - For Portfolio scope:
      - Data cache can be retrieved (or set) by any Datafeed deployed in portfolio
      - scope_id will be ignored and api_inputs.api_project_id will be used.

## 0.2.10

### Fixed

- Fixed issue with `upsert_timeseries_ds()` method in the `integration` module where required fields such as
  `Timestamp`, `ObjectPropertyId`, `Value` were being removed.

## 0.2.9

### Added

- Added `upsert_timeseries()` method to the `integration` module.
  - Data ingested into table storage in addition to ADX Timeseries table
  - Carbon calculation performed where appropriate
    - Please note: If carbon or cost are included as fields in the `Meta` column then no carbon / cost calculation will be performed

### Changed

- Added `DriverClassName` to required columns for `upsert_discovered_records()` method in the `integration` module

### Fixed

- A minor fix to 15-minute interval in `upsert_timeseries_ds()` method in the `integration` module.

## 0.2.8

### Changed

- For the `EventWorkOrderTask` class in the `pipeline` module, the `check_work_order_input_valid()` and the
  `generate_work_order()` methods expect an additional 3 keys to be included by default in the dictionary passed to
  the `work_order_input` parameter:
  - `InstallationId`
  - `EventLink`
  - `EventSummary`

### Fixed

- Issue with the header/payload passed to the API within the `upsert_event_work_order_id()`
  function of the `integration` module.

## 0.2.7

### Added

- New method, `deploy_as_on_demand_data_feed()` added to the `Automation` class of the `pipeline` module
  - this new method is only applicable for tasks that subclass the `EventWorkOrderTask` base class.

### Changed

- The `data_feed_id` is now a required parameter, not optional, for the following methods on the `Automation` class of
  the `pipeline` module:
  - `deploy_on_timer()`
  - `deploy_as_email_data_feed()`
  - `deploy_as_ftp_data_feed()`
  - `deploy_as_upload_data_feed()`
- The `email_address_domain` is now a required parameter, not optional, for the `deploy_as_email_data_feed()` method
  on the `Automation` class of the `pipeline` module.

### Fixed

- issue with payload on `switch_api.pipeline.Automation.register_task()` method for `AnalyticsTask` and
  `EventWorkOrderTask` base classes.

## 0.2.6

### Fixed

- Fixed issues on 2 methods in the `Automation` class of the `pipeline` module:
  - `delete_data_feed()`
  - `cancel_deployed_data_feed()`

### Added

In the `pipeline` module:

- Added new class `EventWorkOrderTask`
  - This task type is for generation of work orders in 3rd party systems via the Switch Automation Platform's Events UI.

### Changed

In the `pipeline` module:

- `AnalyticsTask` - added a new method & a new abstract property:
  - `analytics_settings_definition` abstract property - defines the required inputs (& how these are displayed in the
    Switch Automation Platform UI) for the task to successfully run
  - added `check_analytics_settings_valid()` method that should be used to validate the
    `analytics_settings` dictionary passed to the `start()` method contains the required keys for the task to
    successfully run (as defined by the `analytics_settings_definition`)

In the `error_handlers` module:

- In the `post_errors()` function, the parameter `errors_df` is renamed to `errors` and now accepts strings in
  addition to pandas.DataFrame

### Removed

Due to cutover to a new backend, the following have been removed:

- `run_clone_modules()` function from the `analytics` module
- the entire `platform_insights` module including the :
  - `get_current_insights_by_equipment()` function

## 0.2.5

### Added

- The `Automation` class of the `pipeline` module has 2 new methods added: -`delete_data_feed()`
  - Used to delete an existing data feed and all related deployment settings
  - `cancel_deployed_data_feed()`
    - used to cancel the specified `deployment_type` for a given `data_feed_id`
    - replaces and expands the functionality previously provided in the `cancel_deployed_timer()` method which has been
      removed.

### Removed

- Removed the `cancel_deployed_timer()` method from the `Automation` class of the `pipeline` module
  - this functionality is available through the new `cancel_deployed_data_feed()` method when `deployment_type`
    parameter set to `['Timer']`

## 0.2.4

### Changed

- New parameter `data_feed_name` added to the 4 deployment methods in the `pipeline` module's `Automation` class
  - `deploy_as_email_data_feed()`
  - `deploy_as_ftp_data_feed()`
  - `deploy_as_upload_data_feed()`
  - `deploy_on_timer()`

## 0.2.3

### Fixed

- Resolved minor issue on `register_task()` method for the `Automation` class in the `pipeline` module.

## 0.2.2

### Fixed

- Resolved minor issue on `upsert_discovered_records()` function in `integration` module related to device-level
  and sensor-level tags.

## 0.2.1

### Added

- New class added to the `pipeline` module
  - `DiscoverableIntegrationTask` - for API integrations that are discoverable.
    - requires `process()` & `run_discovery()` abstract methods to be created when sub-classing
    - additional abstract property, `integration_device_type_definition`, required compared to base `Task`
- New function `upsert_discovered_records()` added to the `integration` module
  - Required for the `DiscoverableIntegrationTask.run_discovery()` method to upsert discovery records to Build -
    Discovery & Selection UI

### Fixed

- Set minimum msal version required for the switch_api package to be installed.

## 0.2.0

Major overhaul done of the switch_api package. A complete replacement of the API used by the package was done.

### Changed

- The `user_id` parameter has been removed from the `switch_api.initialise()` function.
  - Authentication of the user is now done via Switch Platform SSO. The call to initialise will trigger a web browser
    window to open to the platform login screen.
    - Note: each call to initialise for a portfolio in a different datacentre will open up browser and requires user to
      input their username & password.
    - for initialise on a different portfolio within the same datacentre, the authentication is cached so user will not
      be asked to login again.
- `api_inputs` is now a required parameter for the `switch_api.pipeline.Automation.register_task()`
- The `deploy_on_timer()`, `deploy_as_email_data_feed()`, `deploy_as_upload_data_feed()`, and
  `deploy_as_ftp_data_feed()` methods on the `switch_api.pipeline.Automation` class have an added parameter:
  `data_feed_id`
  - This new parameter allows user to update an existing deployment for the portfolio specified in the `api_inputs`.
  - If `data_feed_id` is not supplied, a new data feed instance will be created (even if portfolio already has that
    task deployed to it)

## 0.1.18

### Changed

- removed rebuild of the ObjectProperties table in ADX on call to `upsert_device_sensors()`
- removed rebuild of the Installation table in ADX on call to `upsert_sites()`

## 0.1.17

### Fixed

- Fixed issue with `deploy_on_timer()` method of the `Automation` class in the `pipeline` module.
- Fixed column header issue with the `get_tag_groups()` function of the `integration` module.
- Fixed missing Meta column on table generated via `upsert_workorders()` function of the `integration` module.

### Added

- New method for uploading custom data to blob `Blob.custom_upload()`

### Updated

- Updated the `upsert_device_sensors()` to improve performance and aid release of future functionality.

## 0.1.16

### Added

To the `pipeline` module:

- New method `data_feed_history_process_errors()`, to the `Automation` class.
  - This method returns a dataframe containing the distinct set of error types encountered for a specific
    `data_feed_file_status_id`
- New method `data_feed_history_errors_by_type` , to the `Automation` class.
  - This method returns a dataframe containing the actual errors identified for the specified `error_type` and
    `data_feed_file_status_id`

Additional logging was also incorporated in the backend to support the Switch Platform UI.

### Fixed

- Fixed issue with `register()` method of the `Automation` class in the `pipeline` module.

### Changed

For the `pipeline` module:

- Standardised the following methods of the `Automation` class to return pandas.DataFrame objects.
- Added additional error checks to ensure only allowed values are passed to the various `Automation` class methods
  for the parameters:
  - `expected_delivery`
  - `deploy_type`
  - `queue_name`
  - `error_type`

For the `integration` module:

- Added additional error checks to ensure only allowed values are passed to `post_errors` function for the parameters:
  - `error_type`
  - `process_status`

For the `dataset` module:

- Added additional error check to ensure only allowed values are provided for the `query_language` parameter of the
  `get_data` function.

For the `_platform` module:

- Added additional error checks to ensure only allowed values are provided for the `account` parameter.

## 0.1.14

### Changed

- updated get_device_sensors() to not auto-detect the data type - to prevent issues such as stripping leading zeroes,
  etc from metadata values.

## 0.1.13

### Added

To the `pipeline` module:

- Added a new method, `data_feed_history_process_output`, to the `Automation` class

## 0.1.11

### Changed

- Update to access to `logger` - now available as `switch_api.pipeline.logger()`
- Update to function documentation

## 0.1.10

### Changed

- Updated the calculation of min/max date (for timezone conversions) inside the `upsert_device_sensors` function as
  the previous calculation method will not be supported in a future release of numpy.

### Fixed

- Fixed issue with retrieval of tag groups and tags via the functions:
  - `get_sites`
  - `get_device_sensors`

## 0.1.9

### Added

- New module `platform_insights`

In the `integration` module:

- New function `get_sites` added to lookup site information (optionally with site-level tags)
- New function `get_device_sensors` added to assist with lookup of device/sensor information, optionally including
  either metadata or tags.
- New function `get_tag_groups` added to lookup list of sensor-level tag groups
- New function `get_metadata_keys` added to lookup list of device-level metadata keys

### Changed

- Modifications to connections to storage accounts.
- Additional parameter `queue_name` added to the following methods of the `Automation` class of the `pipeline`
  module:
  - `deploy_on_timer`
  - `deploy_as_email_data_feed`
  - `deploy_as_upload_data_feed`
  - `deploy_as_ftp_data_feed`

### Fixed

In the `pipeline` module:

- Addressed issue with the schema validation for the `upsert_workorders` function

## 0.1.8

### Changed

In the `integrations` module:

- Updated to batch upserts by DeviceCode to improve reliability & performance of the `upsert_device_sensors` function.

### Fixed

In the `analytics` module:

- typing issue that caused error in the import of the switch_api package for python 3.8

## 0.1.7

### Added

In the `integrations` module:

- Added new function `upsert_workorders`
  - Provides ability to ingest work order data into the Switch Automation Platform.
  - Documentation provides details on required & optional fields in the input dataframe and also provides information
    on allowed values for some fields.
  - Two attributes available for function, added to assist with creation of scripts by providing list of required &
    optional fields:
    - `upsert_workorders.df_required_columns`
    - `upsert_workorders.df_optional_columns`
- Added new function `get_states_by_country`:
  - Retrieves the list of states for a given country. Returns a dataframe containing both the state name and
    abbreviation.
- Added new function `get_equipment_classes`:
  - Retrieves the list of allowed values for Equipment Class.
    - EquipmentClass is a required field for the upsert_device_sensors function

### Changed

In the `integrations` module:

- For the `upsert_device_sensors` function:
  - New attributes added to assist with creation of tasks:
    - `upsert_device_sensors.df_required_columns` - returns list of required columns for the input `df`
  - Two new fields required to be present in the dataframe passed to function by parameter `df`:
    - `EquipmentClass`
    - `EquipmentLabel`
  - Fix to documentation so required fields in documentation match.
- For the `upsert_sites` function:
  - New attributes added to assist with creation of tasks:
    - `upsert_sites.df_required_columns` - returns list of required columns for the input `df`
    - `upsert_sites.df_optional_columns` - returns list of required columns for the input `df`
- For the `get_templates` function:
  - Added functionality to filter by type via new parameter `object_property_type`
  - Fixed capitalisation issue where first character of column names in dataframe returned by the function had been
    converted to lowercase.
- For the `get_units_of_measure` function:
  - Added functionality to filter by type via new parameter `object_property_type`
  - Fixed capitalisation issue where first character of column names in dataframe returned by the function had been
    converted to lowercase.

In the `analytics` module:

- Modifications to type hints and documentation for the functions:
  - `get_clone_modules_list`
  - `run_clone_modules`
- Additional logging added to `run_clone_modules`

## 0.1.6

### Added

- Added new function `upsert_timeseries_ds()` to the `integrations` module

### Changed

- Additional logging added to `invalid_file_format()` function from the `error_handlers` module.

### Removed

- Removed `append_timeseries()` function

## 0.1.5

### Fixed

- bug with `upsert_sites()` function that caused optional columns to be treated as required columns.

### Added

Added additional functions to the `error_handlers` module:

- `validate_datetime()` - which checks whether the values of the datetime column(s) of the source file are valid. Any
  datetime errors identified by this function should be passed to the `post_errors()` function.
- `post_errors()` - used to post errors (apart from those identified by the `invalid_file_format()` function) to
  the data feed dashboard.

## 0.1.4

### Changed

Added additional required properties to the Abstract Base Classes (ABC): Task, IntegrationTask, AnalyticsTask,
LogicModuleTask. These properties are:

- Author
- Version

Added additional parameter `query_language` to the `switch.integration.get_data()` function. Allowed values for this
parameter are:

- `sql`
- `kql`

Removed the `name_as_filename` and `treat_as_timeseries` parameter from the following functions:

- `switch.integration.replace_data()`
- `switch.integration.append_data()`
- `switch.integration.upload_data()`
