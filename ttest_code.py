import requests
import numpy as np
import pandas as pd
from scipy import stats

# Configuring API
API_KEY = "7972b1357b175d36ca9292a2555a0b7327844be3"

BASE_URL = "https://api.census.gov/data/2022/acs/acs5"

# Variable: Median Household Income (estimate)
Variables = ["B19013_001E"]

# Build request parameters 
params = {
    "get": ",".join(Variables),
    "for": "county:*",              # * gets all counties (defined by API) 
    "in": "state:*",
    "key": API_KEY
}

# Make API requests
response = requests.get(BASE_URL, params=params)


# Convert JSON -> DataFrame
data = response.json()              # Converts all data from JSON into python data structures 

columns = data[0]
rows = data[1:]

df = pd.DataFrame(rows, columns=columns)

# Basic cleaning 
df["B19013_001E"] = pd.to_numeric(df["B19013_001E"], errors="coerce")

df.rename(
    columns = {
        "B19013_001E": "median_household_income",
        "state": "state_fips",
        "county": "county_fips"
    },
    inplace=True
)

df["county_fips"] = (
    df["state_fips"].astype(str).str.zfill(2) +
    df["county_fips"].astype(str).str.zfill(3)
)

df.drop(columns=["state_fips"], inplace=True)

# Handling missing values
df = df.replace(-666666666, np.nan)   # -666666666 indicates the value is missing

# Getting urban vs rural data from USDA database
usda_df = pd.read_csv(r"C:\Users\vikra\OneDrive\Desktop\Data Science Projects\t-test project\Ruralurbancontinuumcodes2023.csv",
                      encoding="latin1"
                      )

rucc_df = usda_df[usda_df["Attribute"].str.contains("RUCC")]

rucc_df = rucc_df[["FIPS", "Value"]]

rucc_df.rename(
    columns = {
        "FIPS": "county_fips",
        "Value": "rucc_code"
    },
    inplace=True
)

rucc_df["rucc_code"] = rucc_df["rucc_code"].astype(int)

# Creating a binary flag for urban vs rural 
rucc_df["flag"] = np.where(rucc_df["rucc_code"] > 3, 0, 1)

# Now combining both datasets
df["county_fips"] = df["county_fips"].astype(str)
rucc_df["county_fips"] = rucc_df["county_fips"].astype(str)

merged_df = pd.merge(df, rucc_df, on="county_fips", how="inner")

# Split dataframes based on rural vs urban
urban = merged_df.loc[merged_df["flag"] == 1, "median_household_income"].dropna()
rural = merged_df.loc[merged_df["flag"] == 0, "median_household_income"].dropna()

t_stat, p_value = stats.ttest_ind(
    urban, 
    rural,
    equal_var=False
)

print("t-stat: ", t_stat)
print("p-value: ", p_value)


"""
Interpretation: The t-stat is much greater than 1.96. 
The p-stat is much less than 0.05. 
Therefore, we reject the null hypothesis to conclude there is a significant differnce between median incomes in urban and rural counties. 
"""