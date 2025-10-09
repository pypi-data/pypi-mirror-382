# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for integrating asset creation, asset updates, data ingestion, etc into the Switch Automation Platform.
"""

from .integration import (upsert_data, upsert_sites, upsert_workorders, upsert_device_sensors, upsert_device_sensors_ext,
                          upsert_timeseries_ds, replace_data, append_data, upsert_file_row_count,
                          upsert_discovered_records, upsert_timeseries, upsert_tags, upsert_device_metadata,
                          upsert_reservations, upsert_device_sensors_iq)

from .helpers import (get_sites, get_tag_groups, get_metadata_keys, get_data, get_device_sensors, get_templates,
                      get_units_of_measure, get_states_by_country, get_operation_state, get_equipment_classes,
                      load_data, get_timezones, amortise_across_days, get_metadata_where_clause, connect_to_sql,
                      update_last_record_property_value)

__all__ = ['upsert_data', 'upsert_sites', 'upsert_workorders', 'upsert_device_sensors', 'upsert_device_sensors_ext',
           'upsert_timeseries_ds', 'replace_data', 'append_data', 'get_sites', 'get_tag_groups', 'get_metadata_keys',
           'get_data', 'get_device_sensors', 'get_templates', 'get_units_of_measure', 'get_states_by_country',
           'get_operation_state', 'get_equipment_classes', 'load_data', 'upsert_file_row_count',
           'upsert_discovered_records', 'upsert_timeseries', 'upsert_tags', 'upsert_device_metadata', 'get_timezones',
           'amortise_across_days', 'get_metadata_where_clause', 'connect_to_sql', 'upsert_reservations', 'upsert_device_sensors_iq',
           'update_last_record_property_value']
