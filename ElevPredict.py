import streamlit as st
import pandas as pd
import random
from datetime import datetime

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="ElevPredict IoT",
    layout="wide"
)

# =====================================
# VARIABLES DE SESIÓN
# =====================================

if "historial_vibracion" not in st.session_state:
    st.session_state.historial_vibracion = []

if "bitacora" not in st.session_state:
    st.session_state.bitacora = pd.DataFrame(columns=[
        "FechaHora",
        "Estado",
        "Piso",
        "Vibración",
        "Temperatura",
        "Corriente",
        "Salud",
        "Riesgo"
    ])

if "piso_actual" not in st.session_state:
    st.session_state.piso_actual = 1

if "destino" not in st.session_state:
    st.session_state.destino = random.randint(2, 15)

if "ciclos" not in st.session_state:
    st.session_state.ciclos = 0

# =====================================
# PANEL LATERAL
# =====================================

st.sidebar.title("Configuración")

desgaste = st.sidebar.checkbox(
    "Simular desgaste"
)

desgaste_severo = st.sidebar.checkbox(
    "Simular desgaste severo"
)

# =====================================
# LÓGICA DEL ASCENSOR
# =====================================

piso_actual = st.session_state.piso_actual
destino = st.session_state.destino

if piso_actual < destino:
    estado = "Subiendo"
    piso_actual += 1

elif piso_actual > destino:
    estado = "Bajando"
    piso_actual -= 1

else:
    estado = random.choice([
        "Apertura de puertas",
        "Cierre de puertas",
        "Detenido"
    ])

    if estado == "Detenido":
        st.session_state.destino = random.randint(1, 15)
        st.session_state.ciclos += 1

st.session_state.piso_actual = piso_actual

# =====================================
# VARIABLES SEGÚN ESTADO
# =====================================

if estado == "Detenido":
    vibracion = random.uniform(0.1, 0.5)
    temperatura = random.uniform(45, 55)
    corriente = random.uniform(0, 2)
    velocidad = 0

elif estado == "Apertura de puertas":
    vibracion = random.uniform(0.5, 1.0)
    temperatura = random.uniform(46, 56)
    corriente = random.uniform(2, 5)
    velocidad = 0

elif estado == "Cierre de puertas":
    vibracion = random.uniform(0.5, 1.2)
    temperatura = random.uniform(46, 56)
    corriente = random.uniform(2, 5)
    velocidad = 0

elif estado == "Subiendo":
    vibracion = random.uniform(2.0, 4.0)
    temperatura = random.uniform(55, 70)
    corriente = random.uniform(15, 25)
    velocidad = random.uniform(1.0, 2.0)

else:
    vibracion = random.uniform(1.8, 3.5)
    temperatura = random.uniform(52, 65)
    corriente = random.uniform(12, 22)
    velocidad = random.uniform(1.0, 1.8)

# =====================================
# DESGASTE
# =====================================

factor_ciclos = st.session_state.ciclos * 0.01

vibracion += factor_ciclos
temperatura += factor_ciclos
corriente += factor_ciclos

if desgaste:
    vibracion *= 1.4
    temperatura *= 1.15
    corriente *= 1.10

if desgaste_severo:
    vibracion *= 1.8
    temperatura *= 1.3
    corriente *= 1.2

# =====================================
# SALUD Y RIESGO
# =====================================

indice = (
    vibracion * 10 +
    temperatura * 0.5 +
    corriente * 0.8
)

salud = max(0, min(100, 100 - indice))
riesgo = max(0, min(100, indice))

# =====================================
# TENDENCIA
# =====================================

st.session_state.historial_vibracion.append(
    round(vibracion, 2)
)

if len(st.session_state.historial_vibracion) > 50:
    st.session_state.historial_vibracion.pop(0)

promedio = sum(st.session_state.historial_vibracion) / len(
    st.session_state.historial_vibracion
)

if vibracion > promedio + 0.5:
    tendencia = "Creciente"

elif vibracion < promedio - 0.5:
    tendencia = "Decreciente"

else:
    tendencia = "Estable"

# =====================================
# FECHA Y HORA
# =====================================

fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# =====================================
# CABECERA
# =====================================

st.title("ElevPredict IoT")

st.markdown("""
### Sistema de Monitoreo Predictivo

**Edificio Costanera Center**  
**Ascensor Torre Norte N°3**  
**Activo: ASC-TN-003**
""")

st.info(f"Última actualización: {fecha_hora}")

# =====================================
# ESTADO OPERACIONAL
# =====================================

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Estado", estado)
c2.metric("Piso Actual", piso_actual)
c3.metric("Destino", st.session_state.destino)
c4.metric("Velocidad", f"{velocidad:.1f} m/s")
c5.metric("Ciclos", st.session_state.ciclos)

st.divider()

# =====================================
# VARIABLES
# =====================================

v1, v2, v3 = st.columns(3)

v1.metric("Vibración", f"{vibracion:.2f} mm/s")
v2.metric("Temperatura", f"{temperatura:.1f} °C")
v3.metric("Corriente", f"{corriente:.1f} A")

st.divider()

# =====================================
# SALUD Y RIESGO
# =====================================

r1, r2, r3 = st.columns(3)

r1.metric("Salud del Motor", f"{salud:.0f}%")
r2.metric("Riesgo de Falla", f"{riesgo:.0f}%")
r3.metric("Tendencia", tendencia)

# =====================================
# ALERTAS
# =====================================

if riesgo < 30:
    st.success("Condición normal")

elif riesgo < 60:
    st.warning("Advertencia: revisar condición del motor")

else:
    st.error("Condición crítica: inspección requerida")

# =====================================
# DIAGNÓSTICO AUTOMÁTICO
# =====================================

st.subheader("Diagnóstico Inteligente")

if vibracion > 5:
    st.error(
        "Posible desgaste de rodamientos o desalineación mecánica."
    )

elif temperatura > 75:
    st.warning(
        "Posible sobrecalentamiento del motor."
    )

else:
    st.success(
        "Condiciones operacionales dentro de parámetros normales."
    )

# =====================================
# GRÁFICO
# =====================================

st.subheader("Tendencia de Vibración")

df = pd.DataFrame(
    st.session_state.historial_vibracion,
    columns=["Vibración"]
)

st.line_chart(df)

# =====================================
# ACCIONES REMOTAS
# =====================================

st.subheader("Acciones Remotas")

a1, a2, a3, a4 = st.columns(4)

with a1:
    if st.button("Reducir Velocidad"):
        st.success("Velocidad reducida.")

with a2:
    if st.button("Activar Alarma"):
        st.warning("Alarma enviada al personal.")

with a3:
    if st.button("Programar Mantenimiento"):
        st.success("Mantenimiento programado.")

with a4:
    if st.button("Ajustar Umbral"):
        st.info("Umbral actualizado.")

# =====================================
# BITÁCORA
# =====================================

st.subheader("Bitácora de Mediciones")

if st.button("Guardar Medición"):

    nueva_fila = pd.DataFrame([{
        "FechaHora": fecha_hora,
        "Estado": estado,
        "Piso": piso_actual,
        "Vibración": round(vibracion, 2),
        "Temperatura": round(temperatura, 1),
        "Corriente": round(corriente, 1),
        "Salud": round(salud, 0),
        "Riesgo": round(riesgo, 0)
    }])

    st.session_state.bitacora = pd.concat(
        [
            st.session_state.bitacora,
            nueva_fila
        ],
        ignore_index=True
    )

    st.success("Medición almacenada.")

st.dataframe(
    st.session_state.bitacora,
    use_container_width=True
)

# =====================================
# DESCARGA TXT
# =====================================

contenido_txt = """
=================================
ELEVPREDICT IoT
BITÁCORA DE MEDICIONES
=================================

"""

for _, fila in st.session_state.bitacora.iterrows():

    contenido_txt += f"""
Fecha y Hora: {fila['FechaHora']}
Estado: {fila['Estado']}
Piso: {fila['Piso']}
Vibración: {fila['Vibración']} mm/s
Temperatura: {fila['Temperatura']} °C
Corriente: {fila['Corriente']} A
Salud: {fila['Salud']} %
Riesgo: {fila['Riesgo']} %

---------------------------------
"""

st.download_button(
    label="Descargar Bitácora TXT",
    data=contenido_txt,
    file_name="bitacora_elevpredict.txt",
    mime="text/plain"
)
