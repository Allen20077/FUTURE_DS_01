import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression

# =====================================
# 1. FILE PATHS
# =====================================
DATA_PATH = "data/sales_data.csv"
OUTPUT_DIR = "outputs"

FORECAST_MONTHLY_FILE = "outputs/forecast_dashboard.csv"
FORECAST_REGION_FILE = "outputs/forecast_region.csv"

# =====================================
# 2. SAFETY CHECKS
# =====================================
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("❌ sales_data.csv not found inside data/ folder")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================
# 3. LOAD & PREPARE DATA
# =====================================
df = pd.read_csv(DATA_PATH)

df["Date"] = pd.to_datetime(df["Date"])
df["Revenue"] = df["Quantity"] * df["UnitPrice"]
df["Month"] = df["Date"].dt.month
df["Year"] = df["Date"].dt.year

# =====================================
# 4. MONTHLY AGGREGATION
# =====================================
monthly_sales = (
    df.groupby(["Year", "Month"])["Revenue"]
    .sum()
    .reset_index()
)

# Use latest year for training
latest_year = monthly_sales["Year"].max()
train_data = monthly_sales[monthly_sales["Year"] == latest_year]

X = train_data[["Month"]]
y = train_data["Revenue"]

# =====================================
# 5. TRAIN ML MODEL
# =====================================
model = LinearRegression()
model.fit(X, y)

# =====================================
# 6. FORECAST FULL 12 MONTHS (YTD STYLE)
# =====================================
future_months = np.arange(1, 13).reshape(-1, 1)
forecast_values = model.predict(future_months)

forecast_df = pd.DataFrame({
    "Month": range(1, 13),
    "Forecasted_Revenue": forecast_values.astype(int)
})

# =====================================
# 7. REGION-WISE FORECAST (PROPORTIONAL)
# =====================================
region_ratio = (
    df.groupby("Region")["Revenue"].sum()
    / df["Revenue"].sum()
)

total_forecast_revenue = forecast_df["Forecasted_Revenue"].sum()

region_forecast = (region_ratio * total_forecast_revenue).astype(int)

region_df = region_forecast.reset_index()
region_df.columns = ["Region", "Forecasted_Revenue"]
# =====================================
# 8. LAST YEAR MONTHLY ACTUALS
# =====================================
last_year = df["Year"].max()

last_year_df = (
    df[df["Year"] == last_year]
    .groupby("Month")["Revenue"]
    .sum()
    .reindex(range(1, 13), fill_value=0)
    .astype(int)
    .reset_index()
)

last_year_df.columns = ["Month", "Revenue"]


# =====================================
# 9. SAVE OUTPUTS (FOR DASHBOARD)
# =====================================
forecast_df.to_csv(FORECAST_MONTHLY_FILE, index=False)
region_df.to_csv(FORECAST_REGION_FILE, index=False)
last_year_df.to_csv("outputs/last_year_monthly.csv", index=False)
# =====================================

print("✅ Forecast dashboard data generated successfully")
print("📁 Files created:")
print("   - outputs/forecast_dashboard.csv")
print("   - outputs/forecast_region.csv")
