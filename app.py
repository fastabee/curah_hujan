from flask import Flask, render_template, request
import mysql.connector
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt


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
    


#Arima demam berdarah
    
# Fungsi untuk mengambil data dari database
def fetch_data_from_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT januari, februari, maret, april, mei, juni, juli, agustus, september, oktober, november, desember FROM demam_berdarah ORDER BY id DESC LIMIT 1")
        data = cursor.fetchone()
        cursor.close()
        return data
    except mysql.connector.Error as e:
        print("Error fetching data from database:", e)
        return None
    


# Fungsi untuk mengambil hasil ringkasan model, p-value, dan forecast
def get_model_results(data, p, d, q):
    if data:
        data_series = list(data)
        # Menyesuaikan model ARIMA ke data dengan order yang diberikan
        model = ARIMA(data_series, order=(p, d, q))
        model_fit = model.fit()

        # Mendapatkan hasil ringkasan model
        model_summary = model_fit.summary()

        # Mendapatkan p-value
        p_value = model_fit.pvalues

        # Mendapatkan forecast values
        forecast = model_fit.forecast(steps=12)  # Adjust steps as needed

        return model_summary, p_value, forecast
    else:
        return None, None, None


#arima curah_hujan
def fetch_data_from_database2(connection):
    try:
        cursor2 = connection.cursor()
        cursor2.execute("SELECT januari, februari, maret, april, mei, juni, juli, agustus, september, oktober, november, desember FROM curah_hujan ORDER BY id DESC LIMIT 1")
        data2 = cursor2.fetchone()
        cursor2.close()
        return data2
    except mysql.connector.Error as e:
        print("Error fetching data from database:", e)
        return None
    


# Fungsi untuk mengambil hasil ringkasan model, p-value, dan forecast
def get_model_results2(data2,p, d, q):
    if data2:
        data_series2 = list(data2)
        # Menyesuaikan model ARIMA ke data
        model2 = ARIMA(data_series2, order=(p, d, q))
        model_fit2 = model2.fit()

        

        # Mendapatkan hasil ringkasan model
        model_summary2 = model_fit2.summary()

        # Mendapatkan p-value
        p_value2 = model_fit2.pvalues

        # Mendapatkan forecast values
        forecast2 = model_fit2.forecast(steps=12)  # Adjust steps as needed

        return model_summary2, p_value2, forecast2
    else:
        return None, None, None
    


#route arima curah_hujan

@app.route('/curah_hujan', methods=['GET', 'POST'])
def curah_hujan():
    connection = connect_to_database()
    if request.method == 'POST':
        p_order = int(request.form['p_order'])
        d_order = int(request.form['d_order'])
        q_order = int(request.form['q_order'])
        if connection:
            data2 = fetch_data_from_database2(connection)
            if data2:
                model_summary2, p_value2, forecast2 = get_model_results2(data2, p_order, d_order, q_order)
                return render_template('curah.html', model_summary2=model_summary2, p_value2=p_value2, forecast2=forecast2, data_series2=data2, body='index.html')
            else:
                return "No data available from the database"
        else:
            return "Failed to connect to the database"
    else:
        data2 = fetch_data_from_database2(connection)
        return render_template('curah.html', data_series2=data2)


#route arima demam_berdarah

@app.route('/', methods=['GET', 'POST'])
def index():
    connection = connect_to_database()
    if request.method == 'POST':
        p_order = int(request.form['p_order'])
        d_order = int(request.form['d_order'])
        q_order = int(request.form['q_order'])
        if connection:
            data = fetch_data_from_database(connection)
            if data:
                model_summary, p_value, forecast = get_model_results(data, p_order, d_order, q_order)
                return render_template('index.html', model_summary=model_summary, p_value=p_value, forecast=forecast, data_series=data, body='index.html')
            else:
                return "No data available from the database"
        else:
            return "Failed to connect to the database"
    else:
        data = fetch_data_from_database(connection)
        return render_template('index.html', data_series=data)
    


#differensial demam_berdarah

def get_data_from_databasedifdb():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="steven"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT januari, februari, maret, april, mei, juni, juli, agustus, september, oktober, november, desember FROM demam_berdarah ORDER BY id DESC LIMIT 1")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fungsi untuk melakukan diferensiasi pada data
def differentiate_datadb(data, d):
    diff_data = []
    for i in range(d, len(data)):
        diff_data.append(data[i] - data[i-d])
    return diff_data

#route differensial demam_berdarah
@app.route('/dif', methods=['GET', 'POST'])
def dif():
    if request.method == 'POST':
        d_value = int(request.form['d_value'])

        # Mengambil data dari database
        data_from_db = get_data_from_databasedifdb()

        # Mengubah data menjadi DataFrame menggunakan pandas
        df = pd.DataFrame(data_from_db, columns=['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'])

        # Mengambil data januari-desember sebagai data yang akan didiferensialkan
        data_to_differentiate = df.iloc[-1].values

        # Melakukan diferensiasi pada data
        differentiated_data = differentiate_datadb(data_to_differentiate, d_value)

        # Plot data asli dan data yang telah didiferensialkan
        plt.figure(figsize=(10, 5))
        plt.subplot(2, 1, 1)
        plt.plot(df.columns, data_to_differentiate, marker='o')
        plt.title('Data Asli')
        plt.subplot(2, 1, 2)
        plt.plot(df.columns[d_value:], differentiated_data, marker='o')
        plt.title('Data yang Telah Didiferensialkan (d=' + str(d_value) + ')')
        plt.tight_layout()

        # Simpan plot sebagai file gambar
        plt.savefig('static/plot.png')

    return render_template('differensial.html')

def get_data_from_databasech():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="steven"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT januari, februari, maret, april, mei, juni, juli, agustus, september, oktober, november, desember FROM curah_hujan ORDER BY id DESC LIMIT 1")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fungsi untuk melakukan diferensiasi pada data
def differentiate_datach(data, d):
    diff_data = []
    for i in range(d, len(data)):
        diff_data.append(data[i] - data[i-d])
    return diff_data

@app.route('/dif2', methods=['GET', 'POST'])
def dif2():
    if request.method == 'POST':
        d_value = int(request.form['d_value'])

        # Mengambil data dari database
        data_from_db = get_data_from_databasech()

        # Mengubah data menjadi DataFrame menggunakan pandas
        df = pd.DataFrame(data_from_db, columns=['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'])

        # Mengambil data januari-desember sebagai data yang akan didiferensialkan
        data_to_differentiate = df.iloc[-1].values

        # Melakukan diferensiasi pada data
        differentiated_data = differentiate_datach(data_to_differentiate, d_value)

        # Plot data asli dan data yang telah didiferensialkan
        plt.figure(figsize=(10, 5))
        plt.subplot(2, 1, 1)
        plt.plot(df.columns, data_to_differentiate, marker='o')
        plt.title('Data Asli')
        plt.subplot(2, 1, 2)
        plt.plot(df.columns[d_value:], differentiated_data, marker='o')
        plt.title('Data yang Telah Didiferensialkan (d=' + str(d_value) + ')')
        plt.tight_layout()

        # Simpan plot sebagai file gambar
        plt.savefig('static/plot2.png')

    return render_template('differensial2.html')


# Tambahkan endpoint untuk menyimpan hasil peramalan
@app.route('/save_forecast', methods=['POST'])
def save_forecast():
    connection = connect_to_database()
    if request.method == 'POST':
        forecast_values = request.form['forecast_values'].split(',')
        if connection:
            try:
                cursor = connection.cursor()
                # Simpan hasil peramalan ke dalam tabel database
                query = "INSERT INTO curah_hasil (januari, februari, maret, april, mei, juni, juli, agustus, september, oktober, november, desember) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(query, forecast_values)
                connection.commit()
                cursor.close()
                connection.close()
                return "Hasil peramalan berhasil disimpan."
            except mysql.connector.Error as e:
                connection.rollback()
                return "Gagal menyimpan hasil peramalan:", e
        else:
            return "Gagal terhubung ke database."

    


if __name__ == '__main__':
    app.run(debug=True)
