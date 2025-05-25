import pandas as pd

# Cargamos el archivo CSV
df = pd.read_csv("datos_madrid.csv", encoding="latin1")

print(df.head())
# Printeamos para verificar que se ha cargado correctamente donde veremos las primeras 5 filas del DataFrame
# Utilizamos el método encoding="latin1" Para evitar problemas de codificación con caracteres especiales en el archivo CSV.

# Limpiamos la columna 'hora' reemplazando 'a.Êm.' por 'AM' y 'p.Êm.' por 'PM'
df['hora_limpia'] = df['hora'].str.replace('a.Êm.', 'AM', regex=False)
df['hora_limpia'] = df['hora_limpia'].str.replace('p.Êm.', 'PM', regex=False)

# Combina el contenido de la columna 'fecha' y la columna 'hora_limpia' en una sola cadena, separadas por un espacio.
df['fecha_hora'] = pd.to_datetime(df['fecha'] + ' ' + df['hora_limpia'], errors='coerce', dayfirst=True)

# Eliminamos filas con fechas inválidas para evitar errores en análisis o exportación
df = df.dropna(subset=['fecha_hora'])

# Creamos un diccionario para traducir días de la semana de inglés a español
dias_ingles_espanol = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

# Creamos una columna 'dia_semana' con los nombres en español
df['dia_semana'] = df['fecha_hora'].dt.day_name().map(dias_ingles_espanol)

# Clasificamos el tipo de día como laborable o fin de semana
def clasificar_dia(dia):
    if dia in ['Sábado', 'Domingo']:
        return 'fin de semana'
    else:
        return 'laborable'

df['tipo_dia'] = df['dia_semana'].apply(clasificar_dia)

# Extraemos la hora en formato numérico (0 a 23) para análisis temporal
df['hora_numero'] = df['fecha_hora'].dt.hour

# Imprimimos las nuevas columnas
print(df[['fecha_hora', 'dia_semana', 'tipo_dia', 'hora_numero']].head())

# Análisis de accidentes por tipo de día
accidentes_por_dia = df.groupby('tipo_dia').size()
print("Accidentes por tipo de día:")
print(accidentes_por_dia)

# Análisis por día de la semana
accidentes_semana = df['dia_semana'].value_counts()
print("Accidentes por día de la semana:")
print(accidentes_semana)

# Lista de días válidos normalizados para la entrada del usuario
dias_validos = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']

# Función para normalizar cadenas (quitar tildes y pasar a minúsculas)
def normalizar_dia(dia):
    return dia.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

# Función para contar accidentes por día de la semana
def contar_accidentes_por_dia(dia_nombre):
    contador = 0
    for dia in df['dia_semana']:
        if normalizar_dia(dia) == normalizar_dia(dia_nombre):
            contador += 1
    return contador

# Bucle para solicitar al usuario un día y contar los accidentes
intentos = 0
max_intentos = 3

while intentos < max_intentos:
    dia_input = input("Introduce un día de la semana (por ejemplo, 'Lunes'): ")
    dia_normalizado = normalizar_dia(dia_input)
    if dia_normalizado in [normalizar_dia(d) for d in dias_validos]:
        dia_mostrar = [d for d in df['dia_semana'].unique() if normalizar_dia(d) == dia_normalizado][0]
        total = contar_accidentes_por_dia(dia_mostrar)
        print(f"Accidentes un {dia_mostrar}: {total}")
        break
    else:
        intentos += 1
        print(f"'{dia_input}' no es un día válido. Intento {intentos} de {max_intentos}.")

if intentos == max_intentos:
    print("Has superado el número máximo de intentos. Cerrando sesión.")

# Exportamos el DataFrame limpio a CSV y Excel para Power BI o análisis adicional
df.to_csv("accidentes_limpios.csv", index=False, encoding="utf-8-sig")
df.to_excel("accidentes_limpios.xlsx", index=False)

print("Datos exportados como 'accidentes_limpios.csv' y 'accidentes_limpios.xlsx'")
print(df.info())
