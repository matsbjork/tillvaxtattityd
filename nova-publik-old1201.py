import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from pypdf import PdfReader
import base64

# ---------------------------------------------------------
# Nova 1.0 - Sundsvalls Tillväxtstrategi
# Utvecklad av Näringsliv och Tillväxt, Sundsvalls kommun
# Version: 1.0 (Publik) matsandreasbjork@gmail.com
# ---------------------------------------------------------


# Ladda miljövariabler (.env) om den finns lokalt
load_dotenv()

# Konfigurera sidans inställningar
st.set_page_config(
    page_title="Nova - Sundsvalls Tillväxtstrategi",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CSS: DESIGN & JUSTERINGAR
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 1. BLÅ KNAPPAR (Behåller detta önskemål) */
    div.stButton > button {
        background-color: #006996;
        color: white;
        border: none;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #005073;
        color: white;
        border: none;
    }

    /* 2. CHATTRUTAN (Återställd för att fungera) */
    /* Vi tar bort den tvingade höjden eftersom den blockerade inmatning i vissa webbläsare.
       Streamlits chattinput expanderar numera automatiskt. */

    /* 3. SVENSK TEXT PÅ UPPLADDNING (Hack) */
    [data-testid='stFileUploader'] section > input + div {
        display: none;
    }
    [data-testid='stFileUploader'] section::after {
        content: "Dra och släpp fil här • Max 20MB per fil • PDF";
        display: block;
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        padding: 10px;
    }

    /* 4. CENTRERING AV RUBRIKER */
    .nova-subtitle {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 500;
        color: #333;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. KONFIGURATION & TEXTER
# ---------------------------------------------------------

# Hämta API-nyckel
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("Ingen API-nyckel hittades. Se till att du har en .env-fil med OPENAI_API_KEY eller konfigurerat Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# SYSTEMPROMPT (NOVA v2.0)
SYSTEM_PROMPT_TEXT = """
# IDENTITET OCH UPPDRAG
Du är Nova – Sundsvalls kommuns AI-assistent för tillväxtstrategin.
Ditt syfte är att hjälpa medarbetare, ledare och nyckelpersoner i Sundsvalls kommuns förvaltningar att förstå, inspireras av och omsätta tillväxtstrategin i sitt dagliga arbete.

Du är namngiven efter det latinska ordet för "ny" – vilket speglar din roll att hjälpa Sundsvall ta nästa steg i riktningen mot 110 000 invånare år 2035.

# OM WEBBPLATSEN (Om användaren frågar vad detta är)
Detta är en ai-tjänst (www.tillvaxtattityd.se) utvecklad för att testa AI-stöd i arbetet med Sundsvalls Tillväxtstrategi.
Syftet är att underlätta för tjänstepersoner och medborgare att navigera och använda strategin i vardagen. 
Avsändare är avdelningen Näringsliv och Tillväxt i Sundsvall.
Roadmap: Tjänsten utvärderas löpande och planen är att använda så mycket av värdena i AI-plattform Eneo under kommande 2026.

## Uppstartsfras
När en konversation börjar, hälsa alltid välkomnande:
"Hej! Jag är Nova, din AI-assistent för Sundsvalls tillväxtstrategi. Mitt uppdrag är att hjälpa dig omsätta strategin i din vardag – oavsett om det gäller verksamhetsplanering, nya initiativ eller att hitta kopplingar till den gemensamma riktningen om 110 000 invånare 2035. Vilken förvaltning arbetar du i, och vad kan jag hjälpa dig med idag?"

# PERSONLIGHET OCH TONALITET
Du representerar tillväxtattityden i allt du gör:
- Framåtlutad och lösningsorienterad.
- Varm och inkluderande.
- Konkret och praktisk.
- Modig och inspirerande.

# REGLER OCH BEGRÄNSNINGAR
- Du ska alltid koppla svar till strategins innehåll.
- Du ska aldrig hitta på information som inte finns i strategin eller organisationsstrukturen.
- Om användaren laddar upp ett dokument (t.ex. verksamhetsplan), analysera det utifrån hur det kan stärka tillväxtmålet. Ge konstruktiv feedback.
- Vid osäkerhet, hänvisa till avdelningen Näringsliv och Tillväxt.

# NOVA-INSPIRATION (AVSLUTNINGSFORMAT)
Avsluta relevanta svar med en kort, motiverande uppmaning som driver på tillväxtattityden, t.ex:
"Nova-Inspiration: Vad är det minsta första steget du kan ta redan den här veckan?"
"""

# KUNSKAPSBAS (STRATEGI)
STRATEGY_CONTEXT = """
# TILLVÄXTSTRATEGI SUNDSVALLS KOMMUN (SAMMANFATTNING & KÄRNA)

## RIKTNING
110 000 invånare år 2035.

## AVGÖRANDE FRAMGÅNGSFAKTORER
1. Människan som centrum för utveckling.
2. Infrastruktur som möjliggörare (Ostkustbanan, Airport, Mittstråket, Torsboda).
3. Robusthet för motståndskraft.
4. Hållbarhet (ekonomisk, social, ekologisk).
5. Lokal värdebehållning.

## TILLVÄXTATTITYD (Kännetecken)
Proaktiv inställning, Innovationsvilja, Samarbetskraft, Anpassningsförmåga, Långsiktighet, Välkomnande förhållningssätt.

## DE FYRA PRIORITERADE OMRÅDENA

### 1. OMVÄRLD
Vision: Sundsvall är en internationell kraft med tydlig identitet.
Fokus:
- Omvandla omvärldsinsikter till tillväxtkraft.
- Stärka samarbetet Trondheim–Sundsvall–Vasa.
- Mobilisera för Nya Ostkustbanan.
- Synliggöra "The Northern GRIT".

### 2. OMSTÄLLNINGSKRAFT
Vision: Ledande i grön och digital omställning.
Fokus:
- Torsboda Industrial Park & Logistikparken.
- Gröna och cirkulära affärsidéer.
- AI och GovTech.
- Grön energi.

### 3. NÄRINGSLIV
Vision: En drivande kunskaps- och innovationsmiljö.
Fokus:
- Utveckla innovationssystemet (Mittuniversitetet, Bizmaker etc).
- Attraktiv universitetsstad.
- Kulturella och kreativa branscher som innovationsmotor.

### 4. BEFOLKNINGSFÖRSÖRJNING OCH PLATSATTRAKTION
Vision: En attraktiv kuststad där människor vill leva och stanna.
Fokus:
- Utveckla Sundsvall som attraktiv kuststad.
- Testa nya erbjudanden för inflyttning.
- Hållbara, klimatneutrala livsmiljöer.
- Plats för barn och unga.
- Kultur-, idrott- och friluftssatsningar.

## GENOMFÖRANDEPRINCIPER
1. Tillsammans, inte var för sig.
2. Tillväxtattityd i vardagen.
3. Genomförande nära verksamheten.
4. Fokusera på det som gör skillnad.
5. Följ upp och justera.
"""

FULL_SYSTEM_MESSAGE = f"{SYSTEM_PROMPT_TEXT}\n\n# KUNSKAPSBAS:\n{STRATEGY_CONTEXT}"

# ---------------------------------------------------------
# 2. SIDEBAR
# ---------------------------------------------------------

with st.sidebar:
    
    # 1. EXEMPELFRÅGOR
    st.header("💡 Kom igång")
    st.write("Klicka på en fråga för att starta:")
    
    if st.button("Hur kopplar min verksamhetsplan till strategin?", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Hur kopplar min verksamhetsplan till strategin?"})
        st.rerun()
        
    if st.button("Vad innebär tillväxtattityd för min förvaltning?", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Vad innebär tillväxtattityd för min förvaltning?"})
        st.rerun()
    
    st.divider()

    # 2. UPPLADDNING AV DOKUMENT
    st.header("📄 Ladda upp dokument")
    st.write("Få feedback på din verksamhetsplan:")
    
    uploaded_file = st.file_uploader(
        "Välj PDF-fil",
        type="pdf",
        label_visibility="collapsed",
        help="Max 20 MB • PDF-format"
    )
    
    if uploaded_file is not None:
        if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
            with st.spinner("🔄 Analyserar dokument..."):
                try:
                    reader = PdfReader(uploaded_file)
                    pdf_text = ""
                    for page in reader.pages:
                        pdf_text += page.extract_text()
                    
                    document_message = f"""
                    ANVÄNDAREN HAR LADDAT UPP ETT DOKUMENT. 
                    Filnamn: {uploaded_file.name}
                    Innehåll:
                    {pdf_text}
                    
                    INSTRUKTION: Använd innehållet i detta dokument när du svarar på användarens frågor. 
                    Ge feedback på hur dokumentets innehåll kopplar till Tillväxtstrategin.
                    """
                    
                    st.session_state.messages.append({"role": "system", "content": document_message})
                    st.session_state.current_file = uploaded_file.name
                    st.success(f"✅ **{uploaded_file.name}** är inläst!")
                    
                except Exception as e:
                    st.error(f"⚠️ Kunde inte läsa filen: {e}")
    
    st.caption("*Ladda inte upp dokument med känsliga personuppgifter.*")
    
    st.divider()

    # 3. EXPORTERA
    st.subheader("💾 Exportera")
    if st.button("📥 Spara konversation", use_container_width=True):
        if len(st.session_state.messages) > 1:
            conversation_text = ""
            for msg in st.session_state.messages:
                if msg["role"] != "system":
                    role_name = "Nova" if msg["role"] == "assistant" else "Du"
                    conversation_text += f"{role_name}:\n{msg['content']}\n\n---\n\n"
            
            st.download_button(
                label="⬇️ Ladda ner som TXT",
                data=conversation_text,
                file_name="nova_konversation.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("Ingen konversation att exportera än.")
    
    st.divider()
    
    # 4. NYFIKEN PÅ NOVA?
    st.subheader("Nyfiken på Nova?")
    if st.button("Vad är det här för webbplats?", help="Klicka för information om tjänsten", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Vad är det här för webbplats?"})
        st.rerun()

# ---------------------------------------------------------
# 3. HUVUDINNEHÅLL (MAIN)
# ---------------------------------------------------------

# Initiera chatthistorik
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": FULL_SYSTEM_MESSAGE},
        {"role": "assistant", "content": "Hej! Jag är Nova, din AI-assistent för Sundsvalls tillväxtstrategi. Mitt uppdrag är att hjälpa dig omsätta strategin i din vardag – oavsett om det gäller verksamhetsplanering, nya initiativ eller att hitta kopplingar till den gemensamma riktningen mot 110 000 invånare 2035. Vilken förvaltning arbetar du i, och vad kan jag hjälpa dig med idag?"}
    ]

# --- Header med Logo och Titel ---

# Funktion för att ladda och centrera bild med HTML (Idiotsäker centrering)
def render_logo():
    logo_filename = "nova-logo-blue.png"
    if os.path.exists(logo_filename):
        try:
            with open(logo_filename, "rb") as f:
                data = f.read()
                encoded = base64.b64encode(data).decode()
            # HTML för att centrera bilden
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
                    <img src="data:image/png;base64,{encoded}" width="300">
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            st.title("Nova 🚀")
    else:
        # Fallback om filen inte finns
        st.markdown("<h1 style='text-align: center; color:#006996;'>Nova 🚀</h1>", unsafe_allow_html=True)
        st.caption("<div style='text-align: center;'>*(Ladda upp nova-logo-blue.png i roten för att visa logotyp)*</div>", unsafe_allow_html=True)

render_logo()

# Centrerad underrubrik
st.markdown('<div class="nova-subtitle">Din guide till Sundsvalls tillväxtstrategi</div>', unsafe_allow_html=True)

# Mellanrum
st.write("") 
st.write("")

# --- Chatthistorik ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Input ---
if prompt := st.chat_input("Skriv din fråga till Nova här..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# --- Generera svar ---
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            st.error(f"Ett fel uppstod: {e}")
            full_response = "Jag stötte på ett problem. Kontrollera anslutningen eller försök igen."

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; font-size: 0.5rem;'>"
    "Nova - Din guide till tillväxtstrategin. Utvecklad av Näringsliv och Tillväxt, Sundsvalls kommun"
    "</div>",
    unsafe_allow_html=True
)