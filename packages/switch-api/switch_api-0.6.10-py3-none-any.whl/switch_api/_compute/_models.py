# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for compute models
"""

from datetime import datetime
import json
import uuid

from ._utils import safe_uuid


class CarbonCacheInfo:
    def __init__(self, carbon_calculation_region_id: int, from_date: datetime, to_date: datetime,
                 country_name: str, region_name: str, object_property_id: uuid.UUID,
                 object_property_type_id: uuid.UUID, object_property_template_id: uuid.UUID,
                 carbon_expression: str):
        self.carbon_calculation_region_id = carbon_calculation_region_id
        self.from_date = from_date
        self.to_date = to_date
        self.country_name = country_name
        self.region_name = region_name
        self.object_property_id = object_property_id
        self.object_property_type_id = object_property_type_id
        self.object_property_template_id = object_property_template_id
        self.carbon_expression = carbon_expression

    def __repr__(self) -> str:
        return (f"CarbonCacheInfo(carbon_calculation_region_id={self.carbon_calculation_region_id}, "
                f"from_date={self.from_date}, to_date={self.to_date}, country_name='{self.country_name}', "
                f"region_name='{self.region_name}', object_property_id='{self.object_property_id}', "
                f"object_property_type_id={self.object_property_type_id}, "
                f"object_property_template_id={self.object_property_template_id}, "
                f"carbon_expression='{self.carbon_expression}')")


class LocationInfo:
    def __init__(self, country_list: list[str], statename_list: list[str], carbon_calculation_region_name_list: list[str]):
        self.countries = country_list
        self.state_names = statename_list
        self.region_names = carbon_calculation_region_name_list

    def __repr__(self):
        return (f"LocationInfo(countries={self.countries}, "
                f"state_names={self.state_names}, "
                f"region_names={self.region_names})")
