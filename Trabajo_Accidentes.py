import pandas as pd

# Cargar archivo (usa 'latin1' si sigue dando error con 'utf-8-sig')
try:
    df = pd.read_csv("datos_madrid.csv", encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv("datos_madrid.csv", encoding="latin1")

# Limpieza de la columna 'hora'
df['hora_limpia'] = df['hora'].str.replace('a.Êm.', 'AM', regex=False).str.replace('p.Êm.', 'PM', regex=False)
df['hora_limpia'] = df['hora_limpia'].str.replace('a.m.', 'AM', regex=False).str.replace('p.m.', 'PM', regex=False)


# Combinar fecha y hora
df['fecha_hora'] = pd.to_datetime(df['fecha'] + ' ' + df['hora_limpia'], errors='coerce', dayfirst=True)
df = df.dropna(subset=['fecha_hora'])

# Traducir nombres de días
dias_ingles_espanol = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
df['dia_semana'] = df['fecha_hora'].dt.day_name().map(dias_ingles_espanol)

# Clasificación del tipo de día
df['tipo_dia'] = df['dia_semana'].apply(lambda d: 'fin de semana' if d in ['Sábado', 'Domingo'] else 'laborable')

# Extraer hora numérica
df['hora_numero'] = df['fecha_hora'].dt.hour

# Mostrar resumen
print(df[['fecha_hora', 'dia_semana', 'tipo_dia', 'hora_numero']].head())

# Análisis
print("Accidentes por tipo de día:")
print(df['tipo_dia'].value_counts())

print("Accidentes por día de la semana:")
print(df['dia_semana'].value_counts())

# Entrada del usuario para contar accidentes por día
dias_validos = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']

def normalizar_dia(d):
    return d.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')

def contar_accidentes_por_dia(dia_input):
    dia_normalizado = normalizar_dia(dia_input)
    coincidencias = df[df['dia_semana'].apply(lambda d: normalizar_dia(d) == dia_normalizado)]
    return len(coincidencias)

for intento in range(3):
    dia_usuario = input("Introduce un día de la semana (por ejemplo, 'Lunes'): ")
    if normalizar_dia(dia_usuario) in [normalizar_dia(d) for d in dias_validos]:
        total = contar_accidentes_por_dia(dia_usuario)
        print(f"Accidentes un {dia_usuario.capitalize()}: {total}")
        break
    else:
        print(f"'{dia_usuario}' no es válido. Intento {intento + 1} de 3.")
else:
    print("Has superado el número máximo de intentos. Cerrando sesión.")

# Exportar resultados
df.to_csv("accidentes_limpios.csv", index=False, encoding="utf-8-sig")
df.to_excel("accidentes_limpios.xlsx", index=False)
print("Datos exportados correctamente.")
print(df.info())

df
