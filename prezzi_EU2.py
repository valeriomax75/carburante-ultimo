import pandas as pd

file_csv = r"C:\Users\Valerio\Desktop\python\corso VIOLETA\dati\proggetto carburante\dati csv\carbur_10pais.csv"

# Leggere CSV come stringhe, saltando righe malformate
df = pd.read_csv(file_csv, sep=',', dtype=str, on_bad_lines='skip')

# Pulizia nomi colonne (spazi)
df.columns = df.columns.str.strip()

# Stampare le colonne presenti
print("Colonne presenti nel CSV:")
print(df.columns.tolist())

# Stampare le prime 10 righe generali
print("\nPrime 10 righe del CSV:")
print(df.head(10))
