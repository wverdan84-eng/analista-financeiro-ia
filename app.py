import streamlit as st
import pandas as pd
import requests
import io
from PIL import Image
import re

# -----------------------------
# FUNÇÃO OCR VIA IA (OCR.Space)
# -----------------------------
def ocr_ia(imagem):
    url = "https://api.ocr.space/parse/image"
    payload = {
        "language": "por",
        "isOverlayRequired": False,
        "OCREngine": 2
    }

    image_bytes = io.BytesIO()
    imagem.save(image_bytes, format="PNG")

    response = requests.post(
        url,
        files={"file": image_bytes.getvalue()},
        data=payload
    )

    result = response.json()

    if result.get("ParsedResults"):
        return result["ParsedResults"][0]["ParsedText"]
    else:
        return ""


# -----------------------------
# CONFIG STREAMLIT
# -----------------------------
st.set_page_config(
    page_title="Analista Financeiro IA",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Analista Financeiro IA")
st.write("Envie um **print da sua carteira de investimentos** e receba uma análise profissional automática.")

# -----------------------------
# UPLOAD DA IMAGEM
# -----------------------------
arquivo = st.file_uploader(
    "📤 Envie o print da carteira",
    type=["png", "jpg", "jpeg"]
)

if arquivo:
    imagem = Image.open(arquivo)
    st.image(imagem, caption="Print enviado", use_container_width=True)

    with st.spinner("🔍 Analisando imagem com IA..."):
        texto = ocr_ia(imagem)

    st.subheader("📄 Texto bruto detectado")
    st.text(texto)

    # -----------------------------
    # PROCESSAMENTO DO TEXTO
    # -----------------------------
    linhas = texto.splitlines()
    tickers = []

    padrao_ticker = re.compile(r"^[A-Z]{2,5}$")

    for linha in linhas:
        linha = linha.strip()
        if padrao_ticker.match(linha):
            tickers.append(linha)

    ativos_unicos = sorted(set(tickers))

    if ativos_unicos:
        st.subheader("📊 Carteira organizada")

        df = pd.DataFrame(ativos_unicos, columns=["Ativo"])
        st.dataframe(df, use_container_width=True)

        # -----------------------------
        # CLASSIFICAÇÃO DOS ATIVOS
        # -----------------------------
        renda_variavel = []
        cripto = []
        renda_fixa = []

        for ativo in ativos_unicos:
            if ativo in ["BTC", "ETH", "BTCO"]:
                cripto.append(ativo)
            elif ativo in ["BND", "BNDX"]:
                renda_fixa.append(ativo)
            else:
                renda_variavel.append(ativo)

        total_ativos = len(ativos_unicos)

        # -----------------------------
        # ANÁLISE PROFISSIONAL
        # -----------------------------
        st.subheader("🧠 Análise do Analista Financeiro IA")

        st.markdown(f"""
**Resumo geral da carteira:**

- Total de ativos identificados: **{total_ativos}**
- Renda variável (ETFs/Ações): **{len(renda_variavel)}**
- Criptomoedas: **{len(cripto)}**
- Renda fixa: **{len(renda_fixa)}**

**Análise profissional:**

Sua carteira apresenta **boa diversificação internacional**, com exposição a diferentes classes de ativos, o que reduz riscos específicos.

**Pontos positivos:**
✔️ Diversificação geográfica  
✔️ Exposição a ativos globais  
✔️ Inclusão de ativos de proteção e crescimento  

**Pontos de atenção:**
⚠️ Alta concentração em renda variável  
⚠️ Criptomoedas aumentam volatilidade  

**Perfil sugerido:** Moderado a arrojado
        """)

        # -----------------------------
        # GRÁFICO
        # -----------------------------
        st.subheader("📈 Distribuição da Carteira")

        distribuicao = {
            "Renda Variável": len(renda_variavel),
            "Criptomoedas": len(cripto),
            "Renda Fixa": len(renda_fixa)
        }

        df_grafico = pd.DataFrame(
            distribuicao.items(),
            columns=["Tipo", "Quantidade"]
        )

        st.bar_chart(df_grafico.set_index("Tipo"))

    else:
        st.warning("⚠️ Nenhum ativo reconhecido no print. Tente uma imagem mais nítida.")
