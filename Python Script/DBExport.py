import sqlite3
import pandas as pd
conn = sqlite3.connect('StuderOpearion.db')

Discharch1 = pd.read_sql_query('SELECT * FROM Unit1_Discharging', conn)
Discharch3 = pd.read_sql_query('SELECT * FROM Unit3_Discharging', conn)
Discharch7 = pd.read_sql_query('SELECT * FROM Unit7_Discharging', conn)
conn.close()

columns_names = ['DateTime', 'Battery_SOC', 'Battery_Current', 'Battery_Voltage', 'Battery_Power', 'AC_In_Current', 'AC_In_Voltage', 'AC_In_Power']
Discharch1.columns = columns_names
Discharch3.columns = columns_names
Discharch7.columns = columns_names

Discharch1.to_csv('../DataBase/Discharging_Unit1.csv', index=None)
Discharch3.to_csv('../DataBase/Discharging_Unit3.csv', index=None)
Discharch7.to_csv('../DataBase/Discharging_Unit7.csv', index=None)
