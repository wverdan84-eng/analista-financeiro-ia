import streamlit as st
import requests
import io
from PIL import Image, ImageEnhance, ImageOps
import re

st.set_page_config(page_title="Analista Financeiro IA", layout="centered")

st.title("📊 Analista Financeiro IA")
st.write("Envie o print da sua carteira ou cole os ativos manualmente.")

# ---------- OCR ----------
def ocr_ia(imagem):
    try:
        imagem = imagem.convert("L")
        imagem = ImageOps.invert(imagem)
        imagem = ImageEnhance.Contrast(imagem).enhance(2.5)
        imagem = ImageEnhance.Sharpness(imagem).enhance(2)

        buffer = io.BytesIO()
        imagem.save(buffer, format="PNG")

        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": buffer.getvalue()},
            data={
                "apikey": "helloworld",
                "language": "eng",
                "OCREngine": 2,
            },
            timeout=20,
        )

        data = response.json()
        if isinstance(data, dict) and data.get("ParsedResults"):
            return data["ParsedResults"][0].get("ParsedText", "")
    except Exception:
        pass

    return ""

# ---------- PARSER ----------
def organizar_ativos(texto):
    linhas = texto.splitlines()
    ativos = []

    for linha in linhas:
        ticker = re.findall(r"\b[A-Z]{2,5}\b", linha)
        if ticker:
            ativos.append(ticker[0])

    return list(set(ativos))

# ---------- APP ----------
imagem = st.file_uploader("📷 Envie o print da carteira", type=["png", "jpg", "jpeg"])

texto_extraido = ""

if imagem:
    img = Image.open(imagem)
    texto_extraido = ocr_ia(img)

    if texto_extraido.strip():
        st.success("📄 Texto detectado automaticamente")
        st.text_area("Texto detectado", texto_extraido, height=150)
    else:
        st.warning("❌ OCR não conseguiu ler o print")

texto_manual = st.text_area(
    "✍️ Cole ou digite seus ativos (ex: VT, VNQ, GLD, BTCO)",
    height=120,
)

texto_final = texto_extraido if texto_extraido.strip() else texto_manual

if st.button("🔍 Analisar carteira"):
    if not texto_final.strip():
        st.error("Informe ao menos um ativo.")
    else:
        ativos = organizar_ativos(texto_final)

        renda_variavel = []
        cripto = []
        renda_fixa = []

        for a in ativos:
            if a in ["BTC", "ETH", "BTCO"]:
                cripto.append(a)
            elif a in ["CDB", "TESOURO", "LCI", "LCA"]:
                renda_fixa.append(a)
            else:
                renda_variavel.append(a)

        st.markdown("## 🧠 Análise do Analista Financeiro IA")

        st.markdown(f"""
**Resumo da carteira**

- Total de ativos: **{len(ativos)}**
- Renda variável: **{len(renda_variavel)}**
- Criptomoedas: **{len(cripto)}**
- Renda fixa: **{len(renda_fixa)}**
        """)

        st.markdown("""
### 📈 Diagnóstico profissional

✔️ Diversificação internacional  
✔️ Exposição a ativos reais (ETFs)  

⚠️ Renda variável dominante  
⚠️ Cripto aumenta volatilidade  

**Perfil sugerido:** Moderado a arrojado  
**Sugestão:** incluir renda fixa para equilíbrio
        """)
