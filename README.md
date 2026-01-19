# Urban vs Rural County Income (Welch t-test)

Goal: test whether **median household income** differs between **urban** and **rural** U.S. counties.

## Data
- **Census ACS API**: county median household income  
- **USDA ERS RUCC (CSV)**: Rural–Urban Continuum Codes (1–9) used to label counties
  - Urban = RUCC 1–3
  - Rural = RUCC 4–9

## Theory (what we’re testing)
Two-sample **Welch** t-test (doesn’t assume equal variances):

- **H₀:** mean income(urban) = mean income(rural)  
- **H₁:** means differ  

If `p < 0.05`, reject H₀.

## Workflow (single Python file)
1. **Pull income from Census API**
   - Load response into a DataFrame
   - Replace invalid sentinel values (e.g. negative placeholders) with `NaN`

2. **Load RUCC CSV (same folder as the .py file)**
   - Read CSV into a DataFrame
   - Filter to rows where `Attribute` contains `"RUCC"`
   - Keep only county FIPS + RUCC value
   - Create `flag`:
     - `flag = 1` if RUCC ≤ 3 (urban)
     - `flag = 0` if RUCC > 3 (rural)

3. **Fix the merge key (critical)**
   - Census has `state_fips` (2 digits) and `county_fips` (3 digits)
   - Combine into **5-digit county FIPS** using zero-padding:
     - `"SS" + "CCC" = "SSCCC"`
   - Treat FIPS as **strings** (IDs, not numbers)

4. **Merge datasets**
   - Merge income + RUCC on 5-digit county FIPS

5. **Run the test**
   - Split into two samples using `flag`
   - Run `scipy.stats.ttest_ind(..., equal_var=False)` (Welch)
   - Interpret `(t, p)`:
     - `p < 0.05` → reject H₀

## Output
Print:
- urban mean, rural mean
- t-statistic and p-value

## Conclusion 
We find that the t-stat is approx. 7.7 and the p-stat is 3.42 x 10^-64. The t-stat being greater than 1.96 means that the result is significant, and the p-value being less than 0.05 means the same. 

Therefore, we conclude there is a significant difference between the median incomes of urban and rural counties. 
