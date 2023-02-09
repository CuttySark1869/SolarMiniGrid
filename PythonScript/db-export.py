import sqlite3
import pandas as pd
conn = sqlite3.connect('DataLog.db')

data_log = pd.read_sql_query('SELECT * FROM DataLog', conn)
conn.close()

columns_names = ['DateTime', 'Battery_SOC', 'Battery_Current', 'Battery_Voltage', 'Battery_Power', 'AC_In_Current', 'AC_In_Voltage', 'AC_In_Power']
data_log.columns = columns_names

data_log.to_csv('DataLog.csv', index=None)
