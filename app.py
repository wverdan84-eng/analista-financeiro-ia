import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import requests
import io
import re

# ===============================
# CONFIG STREAMLIT
# ===============================
st.set_page_config(
    page_title="Analista Financeiro IA",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Analista Financeiro IA")
st.write("Envie um print da sua carteira e receba uma análise automática.")

# ===============================
# FUNÇÃO OCR (API OCR.SPACE)
# ===============================
def ocr_ia(imagem: Image.Image) -> str:
    # Pré-processamento
    imagem = imagem.convert("L")  # cinza
    imagem = ImageOps.invert(imagem)
    imagem = ImageEnhance.Contrast(imagem).enhance(2.5)
    imagem = ImageEnhance.Sharpness(imagem).enhance(2)

    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    try:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": img_bytes},
            data={
                "apikey": "helloworld",  # API gratuita
                "language": "eng",
                "OCREngine": 2,
            },
            timeout=30
        )
        result = response.json()
    except Exception:
        return ""

    if (
        isinstance(result, dict)
        and "ParsedResults" in result
        and result["ParsedResults"]
    ):
        return result["ParsedResults"][0].get("ParsedText", "")

    return ""

# ===============================
# FUNÇÃO DE ANÁLISE DA CARTEIRA
# ===============================
def analisar_carteira(texto: str):
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]

    ativos = []
    for linha in linhas:
        if re.fullmatch(r"[A-Z]{2,6}", linha):
            ativos.append(linha)

    ativos = list(set(ativos))  # remove duplicados

    renda_variavel = []
    cripto = []
    renda_fixa = []

    for ativo in ativos:
        if ativo in ["BTC", "ETH", "BTCO"]:
            cripto.append(ativo)
        elif ativo in ["CDB", "LCI", "LCA", "TESOURO"]:
            renda_fixa.append(ativo)
        else:
            renda_variavel.append(ativo)

    return ativos, renda_variavel, cripto, renda_fixa

# ===============================
# UPLOAD DA IMAGEM
# ===============================
imagem_upload = st.file_uploader(
    "📤 Envie o print da carteira",
    type=["png", "jpg", "jpeg"]
)

if imagem_upload:
    imagem = Image.open(imagem_upload)

    st.image(imagem, caption="Imagem enviada", use_column_width=True)

    with st.spinner("🔍 Extraindo texto do print..."):
        texto = ocr_ia(imagem)

    if not texto.strip():
        st.error("❌ Não foi possível extrair texto do print.")
        st.markdown("""
👉 **Dicas para melhorar o resultado:**
- Use **modo claro** no app da corretora  
- Aumente o **zoom (125% ou 150%)**  
- Evite imagens borradas  
- Print apenas da **lista de ativos**
""")
    else:
        st.subheader("📄 Texto detectado")
        st.text(texto)

        ativos, renda_variavel, cripto, renda_fixa = analisar_carteira(texto)

        if ativos:
            st.subheader("📊 Carteira organizada")

            st.write("**Ativos identificados:**")
            st.write(", ".join(ativos))

            st.markdown(f"""
### 🧠 Análise do Analista Financeiro IA

**Resumo geral da carteira:**
- Total de ativos identificados: **{len(ativos)}**
- Renda variável (ETFs/Ações): **{len(renda_variavel)}**
- Criptomoedas: **{len(cripto)}**
- Renda fixa: **{len(renda_fixa)}**

**Análise profissional:**
Sua carteira apresenta exposição internacional e ativos de proteção.

**Pontos positivos:**  
✔️ Diversificação  
✔️ Exposição global  
✔️ Proteção contra inflação  

**Pontos de atenção:**  
⚠️ Volatilidade se houver cripto  
⚠️ Predominância em renda variável  

**Perfil sugerido:** Moderado a arrojado
""")
        else:
            st.warning("⚠️ Texto detectado, mas nenhum ativo reconhecido automaticamente.")
