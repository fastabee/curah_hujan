from flask import Flask, render_template, request
import mysql.connector
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

app = Flask(__name__)

# Fungsi untuk terhubung ke database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="steven"
        )
        print("Connected to the database")
        return connection
    except mysql.connector.Error as e:
        print("Error connecting to database:", e)
        return None

# Fungsi untuk mengambil data dari database
def fetch_data_from_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT januari, februari, maret, april, mei, juni, juli, agustus, september, oktober, november, desember FROM curah_hujan ORDER BY id DESC LIMIT 1")
        data = cursor.fetchone()
        cursor.close()
        return data
    except mysql.connector.Error as e:
        print("Error fetching data from database:", e)
        return None
    


# Fungsi untuk mengambil hasil ringkasan model, p-value, dan forecast
def get_model_results(data):
    if data:
        data_series = list(data)
        # Menyesuaikan model ARIMA ke data
        model = ARIMA(data_series, order=(1, 1, 1))
        model_fit = model.fit()

        

        # Mendapatkan hasil ringkasan model
        model_summary = model_fit.summary()

        # Mendapatkan p-value
        p_value = model_fit.pvalues

        # Mendapatkan forecast values
        forecast = model_fit.forecast(steps=10)  # Adjust steps as needed

        return model_summary, p_value, forecast
    else:
        return None, None, None

@app.route('/curah_hujan', methods=['GET', 'POST'])
def index():
    connection = connect_to_database()
    if connection:
        data = fetch_data_from_database(connection)
        if data:
            model_summary, p_value, forecast = get_model_results(data)
            return render_template('curah.html', model_summary=model_summary, p_value=p_value, forecast=forecast, data_series=data)
        else:
            return "No data available from the database"
    else:
        return "Failed to connect to the database"

if __name__ == '__main__':
    app.run(debug=True)
