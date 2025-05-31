import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# ====================================
# 1. Load and clean the dataset
# ====================================
try:
    df = pd.read_csv("datos_madrid.csv", encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv("datos_madrid.csv", encoding="latin1")

# Fix time format issues
df['hora_limpia'] = df['hora'].str.replace('a.Êm.', 'AM', regex=False).str.replace('p.Êm.', 'PM', regex=False)
df['hora_limpia'] = df['hora_limpia'].str.replace('a.m.', 'AM', regex=False).str.replace('p.m.', 'PM', regex=False)

# Parse datetime
df['fecha_hora'] = pd.to_datetime(df['fecha'] + ' ' + df['hora_limpia'], errors='coerce', dayfirst=True)
df = df.dropna(subset=['fecha_hora'])

# Translate weekday names
dias_ingles_espanol = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
df['dia_semana'] = df['fecha_hora'].dt.day_name().map(dias_ingles_espanol)
df['tipo_dia'] = df['dia_semana'].apply(lambda d: 'fin de semana' if d in ['Sábado', 'Domingo'] else 'laborable')
df['hora_numero'] = df['fecha_hora'].dt.hour

# ====================================
# 2. Analysis Functions
# ====================================
def accidentes_por_columna(df, columna, nombre_columna):
    if columna in df.columns:
        return df[columna].value_counts(dropna=False).reset_index().rename(columns={'index': nombre_columna, columna: 'Accidentes'})
    else:
        return pd.DataFrame(columns=[nombre_columna, 'Accidentes'])

def normalizar_dia(d):
    return d.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')

def contar_accidentes_por_dia(df, dia_input):
    dia_normalizado = normalizar_dia(dia_input)
    coincidencias = df[df['dia_semana'].apply(lambda d: normalizar_dia(d) == dia_normalizado)]
    return len(coincidencias)

# ====================================
# 3. Show Results in Terminal
# ====================================
print("\n📊 Accidents by day type:")
print(tabulate(accidentes_por_columna(df, 'tipo_dia', 'Tipo de Día'), headers='keys', tablefmt='fancy_grid'))

print("\n📅 Accidents by day of the week:")
print(tabulate(accidentes_por_columna(df, 'dia_semana', 'Día'), headers='keys', tablefmt='fancy_grid'))

print("\n🚻 Accidents by sex:")
print(tabulate(accidentes_por_columna(df, 'sexo', 'Sexo'), headers='keys', tablefmt='fancy_grid'))

print("\n💊 Alcohol positive:")
print(tabulate(accidentes_por_columna(df, 'positiva_alcohol', 'Alcohol'), headers='keys', tablefmt='fancy_grid'))

print("\n💊 Drug positive:")
print(tabulate(accidentes_por_columna(df, 'positiva_droga', 'Droga'), headers='keys', tablefmt='fancy_grid'))

print("\n🌦️ Accidents by weather condition:")
col_clima = [col for col in df.columns if "estado" in col.lower()][0]
print(tabulate(accidentes_por_columna(df, col_clima, 'Clima'), headers='keys', tablefmt='fancy_grid'))

print("\n🛻 Accidents by vehicle type:")
print(tabulate(accidentes_por_columna(df, 'tipo_vehiculo', 'Vehículo'), headers='keys', tablefmt='fancy_grid'))

print("\n👤 Accidents by person type:")
print(tabulate(accidentes_por_columna(df, 'tipo_persona', 'Tipo Persona'), headers='keys', tablefmt='fancy_grid'))

print("\n📈 Accidents by age group:")
print(tabulate(accidentes_por_columna(df, 'rango_edad', 'Edad'), headers='keys', tablefmt='fancy_grid'))

# ====================================
# 4. Ask user for day query
# ====================================
dias_validos = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
for intento in range(3):
    dia_usuario = input("\nEnter a day of the week (e.g., 'Lunes'): ")
    if normalizar_dia(dia_usuario) in [normalizar_dia(d) for d in dias_validos]:
        total = contar_accidentes_por_dia(df, dia_usuario)
        print(f"\n🔎 Total accidents on {dia_usuario.capitalize()}: {total}")
        break
    else:
        print(f"❌ '{dia_usuario}' is not valid. Attempt {intento + 1} of 3.")
else:
    print("⚠️ Maximum attempts reached.")

# ====================================
# 5. Export to Excel
# ====================================
with pd.ExcelWriter("resumen_accidentes.xlsx") as writer:
    accidentes_por_columna(df, 'dia_semana', 'Día').to_excel(writer, sheet_name='Por Día', index=False)
    accidentes_por_columna(df, 'tipo_dia', 'Tipo de Día').to_excel(writer, sheet_name='Tipo Día', index=False)
    accidentes_por_columna(df, 'sexo', 'Sexo').to_excel(writer, sheet_name='Sexo', index=False)
    accidentes_por_columna(df, 'positiva_alcohol', 'Alcohol').to_excel(writer, sheet_name='Alcohol', index=False)
    accidentes_por_columna(df, 'positiva_droga', 'Droga').to_excel(writer, sheet_name='Drogas', index=False)
    accidentes_por_columna(df, col_clima, 'Clima').to_excel(writer, sheet_name='Clima', index=False)
    accidentes_por_columna(df, 'tipo_vehiculo', 'Vehículo').to_excel(writer, sheet_name='Vehículo', index=False)
    accidentes_por_columna(df, 'tipo_persona', 'Persona').to_excel(writer, sheet_name='Persona', index=False)
    accidentes_por_columna(df, 'rango_edad', 'Edad').to_excel(writer, sheet_name='Edad', index=False)

print("\n✅ Data exported to 'resumen_accidentes.xlsx'")

# ====================================
# 6. Charts and Visualizations
# ====================================
sns.set(style="whitegrid")
os.makedirs("graficos", exist_ok=True)

def plot_bar(df, column, title, filename, order=None):
    plt.figure(figsize=(10, 5))
    sns.countplot(data=df, x=column, order=order, palette="Set2")
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"graficos/{filename}")
    plt.close()

def plot_pie(df, column, title, filename):
    plt.figure(figsize=(6, 6))
    df[column].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
    plt.title(title)
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"graficos/{filename}")
    plt.close()

# Generate plots
plot_bar(df, 'tipo_dia', "Accidents by Day Type", "by_day_type.png")
plot_bar(df, 'dia_semana', "Accidents by Weekday", "by_weekday.png",
         order=['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'])
plot_bar(df, 'sexo', "Accidents by Sex", "by_sex.png")
plot_bar(df, 'tipo_vehiculo', "Accidents by Vehicle Type", "by_vehicle.png")
plot_bar(df, col_clima, "Accidents by Weather", "by_weather.png")
plot_bar(df, 'tipo_persona', "Accidents by Person Type", "by_person.png")
plot_bar(df, 'rango_edad', "Accidents by Age Group", "by_age.png")
plot_pie(df, 'positiva_alcohol', "Alcohol Test Results", "alcohol_pie.png")
plot_pie(df, 'positiva_droga', "Drug Test Results", "drug_pie.png")

print("\n📊 Charts saved in the 'graficos/' folder.")
