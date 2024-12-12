from flask import Flask, render_template, request
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

# Fungsi untuk terhubung ke database dan mengambil data
def get_data_from_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="steven"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT januari, februari, maret, april, mei, juni, juli, agustus, september, oktober, november, desember FROM demam_berdarah ORDER BY id DESC LIMIT 12")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fungsi untuk melakukan diferensiasi pada data
def differentiate_data(data, d):
    diff_data = []
    for i in range(d, len(data)):
        diff_data.append(data[i] - data[i-d])
    return diff_data

@app.route('/dif', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        d_value = int(request.form['d_value'])

        # Mengambil data dari database
        data_from_db = get_data_from_database()

        # Mengubah data menjadi DataFrame menggunakan pandas
        df = pd.DataFrame(data_from_db, columns=['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'])

        # Mengambil data januari-desember sebagai data yang akan didiferensialkan
        data_to_differentiate = df.iloc[-1].values

        # Melakukan diferensiasi pada data
        differentiated_data = differentiate_data(data_to_differentiate, d_value)

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

if __name__ == '__main__':
    app.run(debug=True)
