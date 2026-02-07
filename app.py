import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Analista Financeiro IA", layout="centered")

st.title("📊 Analista Financeiro com IA")
st.write("Faça upload de um print da sua carteira para análise automática.")

# ======================
# FUNÇÃO OCR
# ======================
def ocr_ia(imagem):
    api_key = "helloworld"  # chave gratuita OCR.space

    buffered = io.BytesIO()
    imagem.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": img_bytes},
        data={
            "apikey": api_key,
            "language": "por",
            "isOverlayRequired": False,
        },
        timeout=30
    )

    try:
        result = response.json()
    except Exception:
        return ""

    if (
        isinstance(result, dict)
        and "ParsedResults" in result
        and result["ParsedResults"]
        and "ParsedText" in result["ParsedResults"][0]
    ):
        return result["ParsedResults"][0]["ParsedText"]

    return ""


# ======================
# UPLOAD DA IMAGEM
# ======================
arquivo = st.file_uploader(
    "📷 Envie um print da carteira (PNG ou JPG)",
    type=["png", "jpg", "jpeg"]
)

if arquivo:
    imagem = Image.open(arquivo)
    st.image(imagem, caption="Imagem enviada", use_container_width=True)

    with st.spinner("🔍 Extraindo texto da imagem..."):
        texto = ocr_ia(imagem)

    if not texto.strip():
        st.error(
            "❌ Não foi possível extrair texto do print.\n\n"
            "👉 Dicas:\n"
            "- Use fundo claro\n"
            "- Evite imagens borradas\n"
            "- Print direto do app/corretora\n"
            "- Aumente o zoom antes do print"
        )
        st.stop()

    st.success("✅ Texto extraído com sucesso!")
    st.text_area("📄 Texto reconhecido:", texto, height=300)

    # ======================
    # ANÁLISE SIMPLES
    # ======================
    linhas = texto.splitlines()

    renda_variavel = []
    renda_fixa = []
    cripto = []

    for linha in linhas:
        l = linha.lower()
        if any(x in l for x in ["petro", "vale", "itub", "bbas", "ação", "etf"]):
            renda_variavel.append(linha)
        elif any(x in l for x in ["cdb", "tesouro", "lci", "lca"]):
            renda_fixa.append(linha)
        elif any(x in l for x in ["btc", "eth", "bitcoin", "cripto"]):
            cripto.append(linha)

    total_ativos = len(set(renda_variavel + renda_fixa + cripto))

    st.markdown(f"""
### 📌 Resumo da Carteira

- **Total de ativos identificados:** {total_ativos}
- **Renda variável (ações / ETFs):** {len(renda_variavel)}
- **Renda fixa:** {len(renda_fixa)}
- **Criptomoedas:** {len(cripto)}
""")
