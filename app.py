import streamlit as st
from PIL import Image
import pytesseract
import yfinance as yf
import re

# Configurar caminho do Tesseract
# ATENÇÃO: ajuste para onde está instalado no seu PC
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("🧠 Analista Financeiro IA - Grátis")
st.write("Suba o print da sua carteira e receba um resumo e análise.")

# Upload da imagem
uploaded_file = st.file_uploader("📷 Escolha o print da carteira", type=["png","jpg","jpeg"])

def extrair_texto(imagem):
    """Usa OCR para extrair texto da imagem"""
    try:
        texto = pytesseract.image_to_string(imagem, lang="por")
        return texto
    except:
        return ""

def processar_texto(texto):
    """Processa texto bruto em ativos e valores"""
    ativos = []
    linhas = texto.split("\n")
    for linha in linhas:
        linha = linha.strip()
        # Detecta tickers (ex: VT, GLD, BTCO)
        if re.match(r"^[A-Z]{2,5}$", linha):
            ativos.append({"ticker": linha, "valor": None})
        # Detecta valores (ex: US$ 1.314,72)
        elif "US$" in linha and ativos:
            valor = re.sub(r"[^\d,\.]", "", linha).replace(",",".")
            ativos[-1]["valor"] = float(valor)
    return ativos

def analisar_ativos(ativos):
    """Consulta preços atuais e sugere classificação"""
    resumo = {"renda_variavel": [], "cripto": [], "renda_fixa": []}
    for ativo in ativos:
        ticker = ativo["ticker"]
        try:
            info = yf.Ticker(ticker)
            tipo = "Renda Variável" if info.info.get("quoteType")=="ETF" else "Outro"
            if "crypto" in ticker.lower():
                tipo = "Criptomoeda"
            if tipo=="Renda Variável":
                resumo["renda_variavel"].append(ativo)
            elif tipo=="Criptomoeda":
                resumo["cripto"].append(ativo)
            else:
                resumo["renda_fixa"].append(ativo)
        except:
            resumo["renda_variavel"].append(ativo)  # fallback
    return resumo

def gerar_relatorio(resumo):
    st.markdown("**Resumo geral da carteira:**")
    st.markdown(f"- Renda variável (ETFs/Ações): {len(resumo['renda_variavel'])}")
    st.markdown(f"- Criptomoedas: {len(resumo['cripto'])}")
    st.markdown(f"- Renda fixa: {len(resumo['renda_fixa'])}")
    
    st.markdown("**Análise simplificada:**")
    if resumo["cripto"]:
        st.markdown("- ⚠️ Contém criptomoedas, cuidado com volatilidade.")
    if resumo["renda_variavel"]:
        st.markdown("- ✔️ Renda variável diversificada.")
    if resumo["renda_fixa"]:
        st.markdown("- ✔️ Presença de ativos mais seguros.")

if uploaded_file:
    imagem = Image.open(uploaded_file)
    st.image(imagem, caption="Print carregado", use_column_width=True)
    texto = extrair_texto(imagem)
    
    if texto.strip():
        ativos = processar_texto(texto)
        if ativos:
            resumo = analisar_ativos(ativos)
            gerar_relatorio(resumo)
        else:
            st.error("❌ Não foi possível identificar ativos. Verifique o print.")
    else:
        st.error("❌ Não foi possível extrair texto do print.")
