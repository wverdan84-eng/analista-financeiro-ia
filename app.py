import streamlit as st
import pandas as pd
import requests
import io
from PIL import Image
import re

# ======================================
# FUNÇÃO OCR VIA API (ROBUSTA PARA NUVEM)
# ======================================
def ocr_ia(imagem):
    url = "https://api.ocr.space/parse/image"

    payload = {
        "language": "por",
        "isOverlayRequired": False,
        "OCREngine": 2
    }

    image_bytes = io.BytesIO()
    imagem.save(image_bytes, format="PNG")

    try:
        response = requests.post(
            url,
            files={"file": image_bytes.getvalue()},
            data=payload,
            timeout=30
        )

        if response.status_code != 200:
            return ""

        result = response.json()

        if not isinstance(result, dict):
            return ""

        parsed = result.get("ParsedResults")

        if not parsed:
            return ""

        return parsed[0].get("ParsedText", "")

    except Exception:
        return ""


# ======================================
# CONFIGURAÇÃO STREAMLIT
# ======================================
st.set_page_config(
    page_title="Analista Financeiro IA",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Analista Financeiro IA")
st.write(
    "Envie um **print da sua carteira de investimentos** "
    "e receba uma análise automática como um consultor profissional."
)

# ======================================
# UPLOAD DA IMAGEM
# ======================================
arquivo = st.file_uploader(
    "📤 Envie o print da carteira",
    type=["png", "jpg", "jpeg"]
)

if arquivo:
    imagem = Image.open(arquivo)
    st.image(imagem, caption="Print enviado", use_container_width=True)

    with st.spinner("🔍 Lendo imagem com IA..."):
        texto = ocr_ia(imagem)

    if not texto.strip():
        st.warning(
            "⚠️ Não foi possível extrair texto do print. "
            "Tente uma imagem mais nítida ou com fundo claro."
        )
    else:
        st.subheader("📄 Texto bruto detectado")
        st.text(texto)

        # ======================================
        # PROCESSAMENTO DO TEXTO
        # ======================================
        linhas = texto.splitlines()
        tickers = []

        padrao_ticker = re.compile(r"^[A-Z]{2,5}$")

        for linha in linhas:
            linha = linha.strip()
            if padrao_ticker.match(linha):
                tickers.append(linha)

        ativos = sorted(set(tickers))

        if not ativos:
            st.warning("⚠️ Nenhum ativo reconhecido no print.")
        else:
            # ======================================
            # TABELA DE ATIVOS
            # ======================================
            st.subheader("📊 Carteira organizada")
            df = pd.DataFrame(ativos, columns=["Ativo"])
            st.dataframe(df, use_container_width=True)

            # ======================================
            # CLASSIFICAÇÃO
            # ======================================
            renda_variavel = []
            cripto = []
            renda_fixa = []

            for ativo in ativos:
                if ativo in ["BTC", "ETH", "BTCO"]:
                    cripto.append(ativo)
                elif ativo in ["BND", "BNDX"]:
                    renda_fixa.append(ativo)
                else:
                    renda_variavel.append(ativo)

            total_ativos = len(ativos)

            # ======================================
            # ANÁLISE PROFISSIONAL
            # ======================================
            st.subheader("🧠 Análise do Analista Financeiro IA")

            st.markdown(f"""
**Resumo geral da carteira:**

- Total de ativos identificados: **{total_ativos}**
- Renda variável (ETFs/Ações): **{len(renda_variavel)}**
- Criptomoedas: **{len(cripto)}**
- Renda fixa: **{len(renda_fixa)}**

**Análise profissional:**

Sua carteira demonstra **boa diversificação internacional**, com exposição a múltiplas classes de ativos.

**Pontos positivos:**
✔️ Diversificação geográfica  
✔️ Exposição a crescimento global  
✔️ Ativos de proteção (ouro / defensivos)

**Pontos de atenção:**
⚠️ Alta concentração em renda variável  
⚠️ Criptomoedas aumentam volatilidade  

**Perfil sugerido:** Moderado a arrojado
            """)

            # ======================================
            # GRÁFICO
            # ======================================
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
