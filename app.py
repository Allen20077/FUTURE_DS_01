from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "sales_data.csv"))
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    total_revenue = int(df["Revenue"].sum())
    total_orders = df["OrderID"].nunique()
    profit = int(total_revenue * 0.30) # 30% profit margin

    region_sales = df.groupby("Region")["Revenue"].sum().to_dict()

    return render_template(
    "dashboard.html",
    total_revenue=total_revenue,
    total_orders=total_orders,
    profit=profit,
    region_sales=region_sales
)

@app.route("/forecast")
def forecast():
    return render_template("forecast.html")
@app.route("/api/forecast-light")
def api_forecast_light():

    # Monthly forecast
    forecast_df = pd.read_csv(
        os.path.join(BASE_DIR, "outputs", "forecast_dashboard.csv")
    )

    # Region forecast
    region_df = pd.read_csv(
        os.path.join(BASE_DIR, "outputs", "forecast_region.csv")
    )

    # Sales data (for yearly trend)
    sales_df = pd.read_csv(
        os.path.join(BASE_DIR, "data", "sales_data.csv")
    )

    sales_df["Date"] = pd.to_datetime(sales_df["Date"])
    sales_df["Year"] = sales_df["Date"].dt.year
    sales_df["Revenue"] = sales_df["Quantity"] * sales_df["UnitPrice"]

    yearly = (
        sales_df.groupby("Year")["Revenue"]
        .sum()
        .reset_index()
    )

    return jsonify({
        "months": ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"],
        "monthly_forecast": forecast_df["Forecasted_Revenue"].tolist(),

        "regions": region_df["Region"].tolist(),
        "region_values": region_df["Forecasted_Revenue"].tolist(),

        "years": yearly["Year"].astype(str).tolist(),
        "yearly_revenue": yearly["Revenue"].tolist()
    })


@app.route("/api/forecast")
def api_forecast():
    forecast_path = os.path.join(BASE_DIR, "outputs", "forecast.csv")
    df = pd.read_csv(forecast_path)

    return jsonify({
        "labels": df.iloc[:, 0].astype(str).tolist(),
        "values": df.iloc[:, 1].tolist()
    })
from flask import request

@app.route("/api/filtered-data")
def filtered_data():
    df = pd.read_csv(
        os.path.join(BASE_DIR, "data", "sales_data.csv"),
        skipinitialspace=True
    )
    df.columns = df.columns.str.strip()

    region = request.args.get("region")
    category = request.args.get("category")

    if region and region != "All":
        df = df[df["Region"] == region]

    if category and category != "All":
        df = df[df["Category"] == category]

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    summary = (
        df.groupby("Region")["Revenue"]
        .sum()
        .reset_index()
    )

    return jsonify({
        "labels": summary["Region"].tolist(),
        "values": summary["Revenue"].tolist()
    })

if __name__ == "__main__":
    app.run()
