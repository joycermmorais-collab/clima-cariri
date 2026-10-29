import streamlit as st
import urllib.request
import json
from datetime import datetime

st.set_page_config(
    page_title="Clima do Cariri",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Clima do Cariri Paraibano")
st.write("Compare a temperatura das cidades em tempo real.")

cidades = {
    "Sumé": (-7.6717, -36.8800),
    "Serra Branca": (-7.4817, -36.6650),
    "Monteiro": (-7.8895, -37.1200)
}

@st.cache_data(ttl=600)
def consultar_clima():
    resultados = []

    for cidade, (lat, lon) in cidades.items():
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,"
            "apparent_temperature,wind_speed_10m"
            "&timezone=America%2FSao_Paulo"
        )

        requisicao = urllib.request.Request(
            url,
            headers={"User-Agent": "ClimaCariri/1.0"}
        )

        with urllib.request.urlopen(requisicao, timeout=20) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))

        atual = dados["current"]

        resultados.append({
            "cidade": cidade,
            "temperatura": atual["temperature_2m"],
            "sensacao": atual["apparent_temperature"],
            "umidade": atual["relative_humidity_2m"],
            "vento": atual["wind_speed_10m"],
            "horario": atual["time"]
        })

    return resultados

if st.button("🔄 Atualizar temperaturas"):
    consultar_clima.clear()

try:
    resultados = consultar_clima()
    maior = max(item["temperatura"] for item in resultados)
    mais_quentes = [
        item["cidade"] for item in resultados
        if item["temperatura"] == maior
    ]

    st.success(
        f"🔥 Cidade mais quente: {', '.join(mais_quentes)} "
        f— {maior} °C"
    )

    colunas = st.columns(3)

    for coluna, item in zip(colunas, resultados):
        with coluna:
            st.subheader("📍 " + item["cidade"])
            st.metric("Temperatura", f"{item['temperatura']} °C")
            st.write(f"🌡️ Sensação térmica: {item['sensacao']} °C")
            st.write(f"💧 Umidade: {item['umidade']}%")
            st.write(f"💨 Vento: {item['vento']} km/h")

    st.subheader("📊 Comparação das cidades")
    st.bar_chart({
        item["cidade"]: item["temperatura"]
        for item in resultados
    })

    st.caption(
        "Horário dos dados: " + resultados[0]["horario"]
    )
    st.caption(
        "Fonte: Open-Meteo. Dados meteorológicos estimados."
    )

except Exception as erro:
    st.error("Não foi possível consultar as temperaturas.")
    st.write(str(erro))

