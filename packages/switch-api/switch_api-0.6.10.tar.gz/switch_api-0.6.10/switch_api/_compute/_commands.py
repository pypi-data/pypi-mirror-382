# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for compute SQL commands
"""
from datetime import datetime


def COMMAND_INSTALLATION_LOCATION_DETAIL(installation_list: list[str]):
    installation_ids_str = ', '.join(
        [f"'{id.lower()}'" for id in installation_list])

    query = f"""
    SELECT
        Installation.InstallationID,
        Installation.Country,
        Installation.StateName,
        CountryStates.CarbonCalculationRegionName
    FROM
        Installation
        INNER JOIN CountryStates ON Installation.StateName = CountryStates.StateName
    WHERE Installation.InstallationID IN ({installation_ids_str})
    """

    return query


def COMMAND_CARBON_CALCULATION_EXPRESSION(year_list: list[int], obj_prop_ids: list[str]):

    years_string = ', '.join([f"('{year}')" for year in year_list])
    obj_prop_ids_string = ', '.join([f"'{id.lower()}'" for id in obj_prop_ids])

    year_query = ''

    if year_list and len(year_list) > 0:
        year_query = f"""
        WITH YearList AS (
            SELECT Year
            FROM (VALUES {years_string}) AS YearTable(Year)
        )"""

    query = f"""
        {year_query}
        SELECT 
            ObjectPropertyTemplates.ObjectPropertyTypeID, 
            ObjectProperties.ObjectPropertyID, 
            CarbonCalculationRegions.IntCountryCode, 
            CarbonCalculationRegions.RegionName, 
            CountryStates.StateName, 
            CountryStates.IntCountryCode AS Expr1, 
            CarbonCalculations.FromDate, 
            CarbonCalculations.ToDate, 
            CarbonCalculations.CarbonExpression, 
            CarbonCalculationRegionObjectPropertyTemplates.ObjectPropertyTemplateID
        FROM ObjectProperties INNER JOIN
            Installation ON ObjectProperties.InstallationID = Installation.InstallationID INNER JOIN
            CountryStates ON Installation.CountryStateID = CountryStates.CountryStateID INNER JOIN
            ObjectPropertyTemplates ON ObjectProperties.ObjectPropertyTemplateName = ObjectPropertyTemplates.ObjectPropertyTemplateName INNER JOIN
            CarbonCalculationRegions ON ObjectPropertyTemplates.ObjectPropertyTypeID = CarbonCalculationRegions.ObjectPropertyTypeID AND CountryStates.CarbonCalculationRegionName = CarbonCalculationRegions.RegionName INNER JOIN
            CarbonCalculations ON CarbonCalculationRegions.CarbonCalculationRegionID = CarbonCalculations.CarbonCalculationRegionID LEFT OUTER JOIN
            CarbonCalculationRegionObjectPropertyTemplates ON CarbonCalculationRegions.CarbonCalculationRegionID = CarbonCalculationRegionObjectPropertyTemplates.CarbonCalculationRegionID AND 
            ObjectPropertyTemplates.ID IN (CarbonCalculationRegionObjectPropertyTemplates.ObjectPropertyTemplateID, NULL) 
        INNER JOIN YearList ON YearList.Year BETWEEN YEAR(CarbonCalculations.FromDate) AND YEAR(CarbonCalculations.ToDate)        
        WHERE ObjectProperties.ObjectPropertyID IN ({obj_prop_ids_string})
        """

    return query
