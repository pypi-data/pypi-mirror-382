# %%
import os
import sys

import pandas as pd

import pytidycensus as tc
from pytidycensus import acs
from pytidycensus.utils import process_census_data

sys.path.insert(0, "/home/mmann1123/Documents/github/pytidycensus")

# Now set breakpoints in acs.py

import os

# Try to get API key from environment
api_key = os.environ.get("CENSUS_API_KEY")
# For documentation builds without a key, we'll mock the responses
try:
    tc.set_census_api_key(api_key)
    print("Using Census API key from environment")
except Exception:
    print("Using example API key for documentation")
    # This won't make real API calls during documentation builds
    tc.set_census_api_key("EXAMPLE_API_KEY_FOR_DOCS")
# %%

age_table = tc.get_acs(geography="state", table="B01001", year=2020)

print(age_table.head())

# %%
# Get median age by state from 2020 Census
age_2020 = tc.get_decennial(
    geography="state",
    variables="P13_001N",  # Median age variable
    year=2020,
    sumfile="dhc",  # Demographic and Housing Characteristics file
)
print(f"Data shape: {age_2020.shape}")
age_2020.head()

# %%
# # Get median household income by state
cbsa_population = tc.get_acs(geography="cbsa", geometry=True, variables="B01003_001", year=2020)
# %%
cbsa_population.explore()
# %%
cbsa_population = tc.get_acs(geography="zcta", geometry=True, variables="B01003_001", year=2020)

print(cbsa_population.head())
# %%
cbsa_population.plot()

# %%
# # Tract data for Harris County, Texas
# harris_tracts = tc.get_acs(
#     geography="tract",
#     variables="B01003_001",
#     state="TX",
#     county="Harris County",  # Harris County FIPS code
# )

# # %%
# harris_tracts
# # %%
# current_data = tc.get_acs(
#     geography="state", variables="B01003_001", survey="acs1", year=2022
# )
# current_data
# # %%
# components = tc.get_estimates(
#     geography="state",
#     variables=["BIRTHS", "DEATHS", "DOMESTICMIG", "INTERNATIONALMIG"],
#     vintage=2022,
# )  # %%
# components
# # %%
# demographics = tc.get_estimates(
#     geography="state",
#     variables="POP",
#     breakdown=["SEX", "RACE"],
#     breakdown_labels=True,  # Include human-readable labels
#     year=2022,
# )
# demographics
# # %%
# result = tc.get_acs(
#     geography="county",
#     variables="B19013_001",  # Median income
#     summary_var="B01003_001",  # Total population
#     state="VT",
#     year=2022,
# )
# result.head()
# # %%
# race_vars = dict(
#     White="B03002_003",
#     Black="B03002_004",
#     Native="B03002_005",
#     Asian="B03002_006",
#     HIPI="B03002_007",
#     Hispanic="B03002_012",
# )

# az_race = acs.get_acs(
#     geography="county",
#     state="AZ",
#     variables=race_vars,
#     summary_var="B03002_001",
#     year=2020,
# )

# az_race
# # %%
# # Get data with 90% confidence (default)
# result_90 = tc.get_acs(
#     geography="state",
#     variables="B19013_001",
#     state="VT",
#     year=2022,
#     moe_level=90,
#     output="wide",
# )

# # Get data with 95% confidence
# result_95 = tc.get_acs(
#     geography="state",
#     variables="B19013_001",
#     state="VT",
#     year=2022,
#     moe_level=95,
#     output="wide",
# )
# result_95
# # %%
# # 95% MOE should be larger than 90% MOE
# moe_90 = result_90["B19013_001_moe"].iloc[0]
# moe_95 = result_95["B19013_001_moe"].iloc[0]

# assert moe_95 > moe_90
# %%

result = tc.get_decennial(
    geography="county",
    variables="P1_003N",  # White population
    summary_var="P1_001N",  # Total population
    state="VT",
    year=2020,
)

# Verify summary variable
assert isinstance(result, pd.DataFrame)
assert "summary_est" in result.columns
assert all(result["summary_est"] >= result["estimate"])  # Total >= subset

# %%
result.head()

# %%
# %%
race_vars = dict(
    White="B03002_003",
    Black="B03002_004",
    Native="B03002_005",
    Asian="B03002_006",
    HIPI="B03002_007",
    Hispanic="B03002_012",
)

az_race = acs.get_acs(
    geography="tract",
    state="AZ",
    variables=race_vars,
    summary_var="B03002_001",
    year=2020,
)
az_race.head()
# %%
az_race
assert all(az_race["summary_est"] >= az_race["estimate"])  # Total >= subset

# %%
result[result["summary_est"] < result["estimate"]]

# %%
result = tc.get_decennial(geography="state", table="P1", state="VT", year=2020)  # Race table

# Should get all variables from P1 table
assert isinstance(result, pd.DataFrame)
assert len(result) > 0
assert all(var.startswith("P1_") for var in result["variable"].unique())

# %%
result

# %%
result = tc.get_decennial(
    geography="state", table="P1", state="VT", year=2020  # Race table with 71 variables
)
print(result.head())
# Verify the request succeeded
assert isinstance(result, pd.DataFrame)
assert len(result) > 0

# Verify all P1 variables are present
variables = result["variable"].unique()
assert all(var.startswith("P1_") for var in variables)

# P1 table should have exactly 71 variables
assert len(variables) == 71

# Verify proper tidy format structure
expected_columns = {"state", "GEOID", "NAME", "variable", "estimate"}
assert set(result.columns) == expected_columns

# Verify data looks reasonable (population should be > 0)
total_pop = result[result["variable"] == "P1_001N"]["estimate"].iloc[0]
assert int(total_pop) > 600000  # Vermont has ~643k people

print(f"✓ Large table chunking test passed: {len(variables)} variables retrieved")

# %%
result = tc.get_decennial(
    geography="county",
    table="P2",  # Use P2 table (requires chunking)
    state="VT",
    year=2020,
    geometry=True,  # Request geometry
)

# Should return GeoDataFrame when geometry=True
assert hasattr(result, "geometry")  # GeoDataFrame has geometry attribute
assert len(result) > 0

# Should have geographic data
assert "GEOID" in result.columns

# Should have all P2 variables
variables = result["variable"].unique()
assert all(var.startswith("P2_") for var in variables)
assert len(variables) > 50  # P2 is a large table

# %%
result = tc.get_decennial(geography="state", table="P1", state="VT", year=2020)
result
# Verify comprehensive table retrieval
assert isinstance(result, pd.DataFrame)
assert len(result) > 0
variables = result["variable"].unique()
assert all(var.startswith("P1_") for var in variables)
assert len(variables) == 71  # P1 should have exactly 71 variables

# Verify proper data structure
expected_columns = {"state", "GEOID", "NAME", "variable", "estimate"}
assert set(result.columns) == expected_columns
# %%

# Mock Census API response format
mock_data = [
    {"state": "50", "B01003_001E": "643816"},  # Vermont
    {"state": "01", "county": "001", "B01003_001E": "58805"},  # Autauga County, AL
]

result_df = process_census_data(mock_data, variables=["B01003_001E"], output="tidy")
result_df
# %%
# Should have NAME column
assert "NAME" in result_df.columns

# Check that state and county names are properly populated
vermont_rows = result_df[result_df["GEOID"] == "50"]
if not vermont_rows.empty:
    assert vermont_rows["NAME"].iloc[0] == "Vermont"

autauga_rows = result_df[result_df["GEOID"] == "01001"]
if not autauga_rows.empty:
    assert autauga_rows["NAME"].iloc[0] == "Autauga County, Alabama"

# %%
import pytidycensus as tc

# Income analysis with normalization
income_data = tc.get_acs(
    geography="tract",
    variables=[
        "B19013_001E",  # Median Household Income
        "B19001_001E",  # Total Households (Denominator)
        "B19001_002E",  # Households <$25k
        "B17001_001E",  # Total for poverty status (Denominator)
        "B17001_002E",  # Below poverty line
    ],
    state="DC",
    year=2020,
)
# Calculate poverty rate
income_data["poverty_rate"] = (income_data["B17001_002E"] / income_data["B17001_001E"]) * 100

# Education analysis with normalization
education_data = tc.get_acs(
    geography="tract",
    variables=[
        "B15003_001E",  # Total Education Population (Denominator)
        "B15003_002E",  # Less than High School
        "B15003_016E",  # Less than High School (Another category)
        "B15003_022E",  # Bachelor's Degree
    ],
    state="DC",
    year=2020,
)
# Calculate percentage with Bachelor's or Higher
education_data["percentage_bachelors_higher"] = (
    education_data["B15003_022E"] / education_data["B15003_001E"]
) * 100

# Employment analysis with normalization
employment_data = tc.get_acs(
    geography="tract",
    variables=["B23025_002E", "B23025_005E"],  # Labor Force (Denominator)  # Unemployed
    state="DC",
    year=2020,
)
# Calculate unemployment rate
employment_data["unemployment_rate"] = (
    employment_data["B23025_005E"] / employment_data["B23025_002E"]
) * 100

# Print or further analyze the dataframes income_data, education_data, and employment_data
print(income_data.head())
print(education_data.head())
print(employment_data.head())

# %%
import pytidycensus as tc

data = tc.get_acs(
    geography="state",
    variables=[
        "B01003_001E",  # Total population
        "B19013_001E",  # Median household income
        "B25077_001E",  # Median home value
        "B15003_022E",  # Bachelor's degree
    ],
    state="CA",
    year=2022,
    output="wide",
)
data.head()

# Calculate percentage with Bachelor's degree
data["bachelor_rate"] = (data["B15003_022E"] / data["B01003_001E"]) * 100

# %%
# Poverty rate analysis
import pytidycensus as tc

data = tc.get_acs(
    geography="county",
    variables=[
        "B17001_002E",  # Count below poverty line
        "B17001_001E",  # Total for poverty status
        "B01003_001E",  # Total population
    ],
    state="TX",
    year=2022,
    output="wide",
)

# Calculate poverty rate
data["poverty_rate"] = (data["B17001_002E"] / data["B17001_001E"]) * 100
data
# %%
import pytidycensus as tc

data = tc.get_acs(
    geography="tract",
    variables=["B19013_001E"],  # Median income
    state="CA",
    county="Los Angeles",
    geometry=True,  # Include geographic boundaries
    year=2022,
    output="wide",
)

# This returns a GeoPandas GeoDataFrame ready for mapping
data.explore(column="B19013_001E", legend=True)

# %%
import pytidycensus as tc

# DC can be specified as "DC", "11", or "District of Columbia"
data = tc.get_acs(
    geography="tract",
    variables=[
        "B17001_002E",  # Below poverty line
        "B17001_001E",  # Total for poverty status (denominator)
        "B19001_002E",  # Low income households (<$25k)
        "B19001_001E",  # Total households (denominator)
        "B01003_001E",  # Total population
    ],
    state="DC",  # Works with "DC", "11", or "District of Columbia"
    year=2022,
    geometry=True,  # Include geographic boundaries
)

# Calculate rates for proper analysis
data["poverty_rate"] = data["B17001_002E"] / data["B17001_001E"]
data["low_income_rate"] = data["B19001_002E"] / data["B19001_001E"]

data.explore(column="poverty_rate", legend=True, cmap="OrRd")
# %%
import pytidycensus as tc

# Retrieve data for poverty analysis
data = tc.get_acs(
    geography="county",
    variables=[
        "B17001_002E",  # Below poverty
        "B17001_001E",  # Total for poverty status (denominator)
        "B01003_001E",  # Total population
    ],
    state="WA",
    year=2020,
    output="wide",
    geometry=True,  # Include geographic boundaries
    # api_key="YOUR_API_KEY",
)

# Calculate poverty rate
data["poverty_rate"] = (data["B17001_002E"] / data["B17001_001E"]) * 100
data.explore(column="poverty_rate", legend=True, cmap="OrRd")
# Optional: You can visualize the data using GeoPandas for mapping
# Assuming you have a GeoDataFrame with county boundaries
# Example code to merge data with geometry and plot
# merged_data = gdf.merge(data, left_on="GEOID", right_index=True)
# merged_data.plot(column="poverty_rate", cmap="OrRd", legend=True)

# %%
import pytidycensus as tc

# Get American Community Survey data for households under $25k and total households in Washington state counties
data = tc.get_acs(
    geography="county",
    variables=[
        "B19001_002E",  # Households <$25k
        "B19001_001E",  # Total households (denominator)
    ],
    state="WA",
    year=2022,
    output="wide",
    geometry=True,  # For spatial analysis and mapping
    # api_key="YOUR_API_KEY",
)

# Calculate the percentage of households with income under $25,000 in each county
data["households_under_25k_pct"] = (data["B19001_002E"] / data["B19001_001E"]) * 100

# Plotting the data to visualize income inequality at the county level in Washington state
data.explore(column="households_under_25k_pct", legend=True, cmap="OrRd")

# %%
import pytidycensus as tc

# Search for population variables in both years
pop_2010_vars = tc.search_variables(pattern="population", year=2010, dataset="decennial")
pop_2020_vars = tc.search_variables(pattern="total population", year=2020, dataset="decennial")

print("2010 Population Variables:")
print(pop_2010_vars[["name", "label"]].head())
print("\n2020 Population Variables:")
print(pop_2020_vars[["name", "label"]].head())

# %%
import pytidycensus as tc

tc.search_variables(
    "GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME",
    2017,
    "acs",
    "acs5",
)
