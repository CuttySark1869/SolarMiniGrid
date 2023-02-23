import sqlite3
import pandas as pd

def db2csv(name):
    db_file = name + '.db'
    csv_file = name + '.csv'
    conn = sqlite3.connect(db_file)

    data_log = pd.read_sql_query('SELECT * FROM datalog', conn)
    conn.close()

    columns_names = ['DateTime', 'battery_soc', 'battery_voltage', 'battery_power', 'pv_voltage', 'pv_power', 'ac_in_voltage', 'ac_in_power', 'ac_out_voltage', 'ac_out_power']
    data_log.columns = columns_names

    data_log.to_csv(csv_file, index=None)
