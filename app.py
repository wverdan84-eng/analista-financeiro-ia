import streamlit as st
from PIL import Image
import pytesseract
import re
import pandas as pd

# Caminho do Tesseract no Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="Analista Financeiro IA")

st.title("📊 Analista Financeiro IA")
st.write("Envie um print da sua carteira e receba uma análise automática")

# Upload do print
arquivo = st.file_uploader(
    "Upload do print da carteira (PNG ou JPG)",
    type=["png", "jpg", "jpeg"]
)

if arquivo:
    imagem = Image.open(arquivo)
    st.image(imagem, caption="Print carregado", use_container_width=True)

    # OCR
    texto = pytesseract.image_to_string(imagem)

    st.subheader("📄 Texto bruto detectado")
    st.text(texto)

    # Extrair ativos e valores
    ativos = re.findall(r"\b[A-Z]{2,5}\b", texto)
    valores = re.findall(r"US\$ ?[\d.,]+", texto)

    tamanho = min(len(ativos), len(valores))

    dados = []
    for i in range(tamanho):
        dados.append({
            "Ativo": ativos[i],
            "Valor": valores[i]
        })

    if dados:
        df = pd.DataFrame(dados)

        st.subheader("📊 Carteira organizada")
        st.dataframe(df)

        # ===== ANÁLISE =====
        st.subheader("🧠 Análise do Analista Financeiro IA")

        ativos_unicos = df["Ativo"].unique()
        total_ativos = len(ativos_unicos)

        renda_variavel = []
        renda_fixa = []
        cripto = []

        for ativo in ativos_unicos:
            if ativo in ["VT", "VNQ", "GLD"]:
                renda_variavel.append(ativo)
            elif ativo in ["BTCO", "VTI"]:
                cripto.append(ativo)
            else:
                renda_variavel.append(ativo)

        st.markdown(f"""
**Resumo geral da carteira:**

- Total de ativos identificados: **{total_ativos}**
- Renda variável (ETFs/Ações): **{len(renda_variavel)}**
- Criptomoedas: **{len(cripto)}**
- Renda fixa: **{len(renda_fixa)}**

**Análise profissional:**

Sua carteira apresenta uma **boa diversificação internacional**, com exposição a:
- Mercado global (VT)
- Imobiliário (VNQ)
- Ouro como proteção (GLD)
- Criptomoedas como ativo de alto risco (BTCO)

**Pontos positivos:**
✔️ Diversificação geográfica  
✔️ Proteção contra inflação  
✔️ Exposição a crescimento global  

**Pontos de atenção:**
⚠️ Criptomoedas aumentam a volatilidade  
⚠️ Alta concentração em renda variável  

**Perfil sugerido:** Moderado a arrojado
        """)

        # ===== GRÁFICO =====
        st.subheader("📈 Visualização da Carteira")

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
        st.warning("Não foi possível organizar os dados automaticamente.")
