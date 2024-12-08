from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load and preprocess dataset
file_path = 'D:\project\project\Full.csv'
data = pd.read_csv(file_path)
data.replace('N/A', pd.NA, inplace=True)

# Convert 'Date' column
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
data.dropna(subset=['Date'], inplace=True)
data['Domain'] = data['Domain'].str.lower()

# Group data by 'Date' and 'Domain'
grouped = data.groupby(['Date', 'Domain']).size().reset_index(name='Job_Count')

@app.route('/')
def home():
    domains = grouped['Domain'].unique()
    return render_template('index.html', domains=domains)

@app.route('/forecast', methods=['POST'])
def forecast():
    domain = request.form['domain']
    period = int(request.form.get('period', 6))  # Default to 6 months

    # Filter data for the selected domain
    domain_data = grouped[grouped['Domain'] == domain].set_index('Date').resample('M').sum()
    job_counts = domain_data['Job_Count']

    # SARIMA Model
    sarima_model = SARIMAX(job_counts, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    sarima_results = sarima_model.fit()
    sarima_forecast = sarima_results.forecast(steps=period)

    # Prepare forecast dates
    forecast_dates = pd.date_range(domain_data.index[-1] + pd.DateOffset(1), periods=period, freq='M')
    forecast_data = [{'date': date.strftime('%Y-%m'), 'job_count': int(count)} 
                     for date, count in zip(forecast_dates, sarima_forecast)]

    # Generate forecast plot
    plt.figure(figsize=(12, 6))
    plt.plot(job_counts, label='Actual')
    plt.plot(forecast_dates, sarima_forecast, label='SARIMA Forecast')
    plt.title(f'Forecasting Job Demands for {domain.capitalize()}')
    plt.xlabel('Date')
    plt.ylabel('Job Count')
    plt.legend()
    plt.grid()

    # Convert plot to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Prepare JSON response
    return jsonify({'plot': plot_data, 'forecast_data': forecast_data})

@app.route('/download_plot', methods=['POST'])
def download_plot():
    domain = request.form['domain']
    period = int(request.form.get('period', 6))  # Default to 6 months

    # Filter data for the selected domain
    domain_data = grouped[grouped['Domain'] == domain].set_index('Date').resample('M').sum()
    job_counts = domain_data['Job_Count']

    # SARIMA Model
    sarima_model = SARIMAX(job_counts, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    sarima_results = sarima_model.fit()
    sarima_forecast = sarima_results.forecast(steps=period)

    # Prepare forecast dates
    forecast_dates = pd.date_range(domain_data.index[-1] + pd.DateOffset(1), periods=period, freq='M')

    # Generate forecast plot
    plt.figure(figsize=(12, 6))
    plt.plot(job_counts, label='Actual')
    plt.plot(forecast_dates, sarima_forecast, label='SARIMA Forecast')
    plt.title(f'Forecasting Job Demands for {domain.capitalize()}')
    plt.xlabel('Date')
    plt.ylabel('Job Count')
    plt.legend()
    plt.grid()

    # Save the plot as a PNG file
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=f'{domain}_forecast.png')

@app.route('/download_csv', methods=['POST'])
def download_csv():
    domain = request.form['domain']
    period = int(request.form.get('period', 6))  # Default to 6 months

    # Filter data for the selected domain
    domain_data = grouped[grouped['Domain'] == domain].set_index('Date').resample('M').sum()
    job_counts = domain_data['Job_Count']

    # SARIMA Model
    sarima_model = SARIMAX(job_counts, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    sarima_results = sarima_model.fit()
    sarima_forecast = sarima_results.forecast(steps=period)

    # Prepare forecast dates and data
    forecast_dates = pd.date_range(domain_data.index[-1] + pd.DateOffset(1), periods=period, freq='M')
    forecast_data = pd.DataFrame({
        'Date': forecast_dates,
        'Job_Count': sarima_forecast
    })

    # Convert DataFrame to CSV and return as file
    csv_io = io.StringIO()
    forecast_data.to_csv(csv_io, index=False)
    csv_io.seek(0)

    return send_file(io.BytesIO(csv_io.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name=f'{domain}_forecast.csv')

if __name__ == '__main__':
    app.run(debug=True)
