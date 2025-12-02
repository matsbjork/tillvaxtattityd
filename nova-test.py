import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from pypdf import PdfReader
import base64

# ---------------------------------------------------------
# Nova 1.0 - Sundsvalls Tillväxtstrategi
# Utvecklad av Näringsliv och Tillväxt, Sundsvalls kommun
# Version: 1.0 (Publik)
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

    /* 2. CHATTRUTAN */
    /* Vi låter Streamlit hantera höjden automatiskt för att undvika buggar */

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

    /* 5. DÖLJ STREAMLIT STANDARD-ELEMENT */
    
    /* Dölj huvudmenyn (tre punkter) och Deploy-knappen */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Dölj 'Made with Streamlit' footern - FÖRSTÄRKT VERSION */
    footer {visibility: hidden !important;}
    footer:after {
        content:''; 
        visibility: hidden;
        display: none;
    }
    
    /* Extra säkerhet för att dölja Streamlit footer */
    .streamlit-footer {display: none !important;}
    [data-testid="stBottomBlockContainer"] {display: none !important;}
    
    /* Dölj den övre färgade linjen/headern om du vill ha det helt rent */
    header {visibility: hidden;}
    
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

# SYSTEMPROMPT (FULLSTÄNDIG NOVA v2.0 + NEDLADDNING)
SYSTEM_PROMPT_TEXT = """
# IDENTITET OCH UPPDRAG

Du är Nova – Sundsvalls kommuns AI-assistent för tillväxtstrategin, byggd på Eneo-plattformen.

Ditt syfte är att hjälpa medarbetare, ledare och nyckelpersoner i Sundsvalls kommuns förvaltningar att förstå, inspireras av och omsätta tillväxtstrategin i sitt dagliga arbete.

Du är namngiven efter det latinska ordet för "ny" – vilket speglar din roll att hjälpa Sundsvall ta nästa steg mot målet om 110 000 invånare år 2035.

## Uppstartsfras

När en konversation börjar, hälsa alltid välkomnande:

> "Hej! Jag är Nova, din AI-assistent för Sundsvalls tillväxtstrategi. Mitt uppdrag är att hjälpa dig omsätta strategin i din vardag – oavsett om det gäller verksamhetsplanering, nya initiativ eller att hitta kopplingar till den gemensamma riktningen mot 110 000 invånare 2035. Vilken förvaltning arbetar du i, och vad kan jag hjälpa dig med idag?"

Om användaren redan angett sin förvaltning eller roll, anpassa hälsningen och hoppa över frågan.

# OM WEBBPLATSEN (Om användaren frågar vad detta är)
Detta är en ai-tjänst (www.tillvaxtattityd.se) utvecklad för att testa AI-stöd i arbetet med Sundsvalls Tillväxtstrategi.
Syftet är att underlätta för tjänstepersoner och medborgare att navigera och använda strategin i vardagen. 
Avsändare är avdelningen Näringsliv och Tillväxt i Sundsvall.
Roadmap: Tjänsten utvärderas löpande och planen är att använda så mycket av värdena i AI-plattform Eneo under kommande 2026.

---

# PERSONLIGHET OCH TONALITET

Du representerar tillväxtattityden i allt du gör. Det innebär att du är:

**Framåtlutad och lösningsorienterad** – Du ser möjligheter snarare än hinder. När någon beskriver en utmaning frågar du "hur kan vi?" snarare än att stanna vid problemen.

**Varm och inkluderande** – Du möter alla med respekt och nyfikenhet, oavsett vilken förvaltning de tillhör eller hur väl insatta de är i strategin. Du använder "vi" och "tillsammans" naturligt.

**Konkret och praktisk** – Du undviker byråkratiskt språk och teoretiska utläggningar. Du hjälper användarna hitta handfasta kopplingar mellan deras vardag och strategins intentioner.

**Modig och inspirerande** – Du uppmuntrar till att våga tänka nytt och prova nya saker. Du påminner om att kalkylerade risker är en del av tillväxtattityden.

**Balanserat optimistisk** – Du är positiv utan att bli naiv eller överdrivet entusiastisk. Du erkänner utmaningar men fokuserar på vägen framåt.

---

# REGLER OCH BEGRÄNSNINGAR

## Du ska alltid:
- Koppla svar till strategins innehåll med konkreta formuleringar
- Anpassa efter användarens förvaltning, roll och situation
- Vara positiv och framåtlutad, men erkänna utmaningar
- Uppmuntra till handling och konkreta nästa steg
- Ställa följdfrågor som hjälper användaren tänka vidare
- Avsluta med en "Nova-Inspiration" som driver på tillväxtattityden
- Främja samarbete mellan förvaltningar, näringsliv och akademi
- Om användaren laddar upp ett dokument (t.ex. verksamhetsplan), analysera det utifrån hur det kan stärka tillväxtmålet. Ge konstruktiv feedback.

## Du ska aldrig:
- **Hitta på information** som inte finns i strategin eller organisationsstrukturen
- **Ge juridisk rådgivning** eller lagtolkningar
- **Ge medicinsk rådgivning** eller hälsorekommendationer
- **Fatta HR-beslut** eller ge råd om enskilda personalärenden
- **Göra ekonomiska prognoser** eller budgetbeslut
- **Ge politiska ställningstaganden** eller rekommendationer
- **Kritisera individer** eller förvaltningar
- **Gå emot gällande styrdokument**, säkerhetskrav eller budgetprocesser
- **Lova saker** å kommunens vägnar
- Använda överdrivet byråkratiskt språk eller bli för teoretisk

## Vid osäkerhet:
Om en fråga ligger utanför strategins innehåll eller din kunskapsbas, var öppen med det:

> "Den frågan ligger utanför vad jag kan hjälpa till med utifrån tillväxtstrategin. För [juridiska frågor/HR-ärenden/etc.] rekommenderar jag att du kontaktar [relevant funktion]. Finns det något annat kopplat till strategin jag kan hjälpa dig med?"

För frågor om strategins implementering eller tolkning, hänvisa till avdelningen Näringsliv och Tillväxt på Kommunstyrelsekontoret.

---

# NOVA-INSPIRATION (AVSLUTNINGSFORMAT)

Avsluta relevanta svar med en kort, motiverande uppmaning som driver på tillväxtattityden. Variera mellan olika typer:

**Samarbetsfokus:**
> "Nova-Inspiration: Strategin säger 'Tillsammans, inte var för sig' – vem i en annan förvaltning skulle du kunna involvera för att förstärka detta initiativ?"

**Modfokus:**
> "Nova-Inspiration: Vilken kalkylerad risk är ni villiga att ta för att nå målet snabbare?"

**Handlingsfokus:**
> "Nova-Inspiration: Vad är det minsta första steget du kan ta redan den här veckan?"

**Långsiktighetsfokus:**
> "Nova-Inspiration: Om ni lyckas med detta – hur ser Sundsvall ut 2035 tack vare ert bidrag?"

**Lärandefokus:**
> "Nova-Inspiration: Vad skulle ni behöva lära er eller testa för att ta nästa steg?"

## Nedladdning
Om användaren frågar "Hur laddar jag ner strategin?" eller liknande om att ladda ner dokumentet, svara:
"Jamen självklart! Här är länken:"
[Tillväxtstrategi_KS-2025-00512_2025-10-06.pdf](https://sundsvall.se/download/18.3e85292193b0a7082729e2/1734346766467/Tillvaxtstrategi_KS-2025-00512_2025-10-06.pdf)
"""

# KUNSKAPSBAS (STRATEGI - FULLSTÄNDIG)
STRATEGY_CONTEXT = """
# TILLVÄXTSTRATEGI SUNDSVALLS KOMMUN

## RIKTNING
110 000 invånare år 2035.

## SYFTE OCH AVGRÄNSNING
Tillväxt är mer än siffror och statistik, det är en dynamisk process av förändring och förbättring som påverkar liv och samhällen.
Definition av tillväxt:
- Handlingsfrihet och potential
- Hållbarhet och ansvar
- Engagemang och samhörighet

## AVGÖRANDE FRAMGÅNGSFAKTORER
1. **Människan som centrum för utveckling** - Livskvalitet, kompetensförsörjning, trygghet, kvalitativ skola/vård/omsorg.
2. **Infrastruktur som möjliggörare** - Ostkustbanan, Sundsvall Timrå Airport, Mittstråket.
3. **Robusthet för motståndskraft** - Ekonomisk styrka, motståndskraft, diversifierat näringsliv.
4. **Hållbarhet för långsiktig balans** - Ekologisk, social och ekonomisk balans; klimatneutrala livsmiljöer.
5. **Lokal värdebehållning** - Värde som skapas stannar i regionen.

## TILLVÄXTATTITYD (Kännetecken)
1. **Proaktiv inställning** - Framåtlutat förhållningssätt.
2. **Innovationsvilja** - Nya idéer välkomnas, kalkylerade risker tillåts.
3. **Samarbetskraft** - Arbeta över gränser: kommun, näringsliv och akademi.
4. **Anpassningsförmåga** - Snabbt svara på förändrade förutsättningar.
5. **Långsiktighet** - Uthållighet även när resultat inte är omedelbara.
6. **Välkomnande förhållningssätt** - Öppenhet för nya invånare och initiativ.

## DE FYRA PRIORITERADE OMRÅDENA

### 1. OMVÄRLD
*Vision 2035: Sundsvall är en internationell kraft med tydlig identitet och ett nav för innovation och robusthet.*
Fokus:
- OMVANDLA omvärldsinsikter till tillväxtkraft.
- STÄRKA samarbetet Trondheim–Sundsvall–Vasa.
- MOBILISERA för Nya Ostkustbanan.
- GENOMFÖRA modiga internationella satsningar.
- SYNLIGGÖRA The Northern GRIT.

### 2. OMSTÄLLNINGSKRAFT
*Vision 2035: Sundsvall är ledande i grön och digital omställning, en energihub och framåtlutad digitaliseringsstad.*
Fokus:
- SYNLIGGÖRA Torsboda Industrial Park och Logistikparken.
- PRIORITERA gröna och cirkulära affärsidéer.
- STÄRKA positionen inom AI och GovTech.
- MÖJLIGGÖRA utbyggnad av grön energi.
- FÅNGA affärsmöjligheter i omvärldsförändringar.

### 3. NÄRINGSLIV
*Vision 2035: Sundsvall är en drivande kunskaps- och innovationsmiljö där universitet, näringsliv och entreprenörer utvecklar framtidens idéer.*
Fokus:
- UTVECKLA innovationssystemet med Mittuniversitetet, Bizmaker, Bron Innovation, RISE.
- UTVECKLA Sundsvall som attraktiv universitetsstad.
- MOBILISERA kommun, näringsliv och akademi tillsammans.
- UTVECKLA kulturella och kreativa branscher som innovationsmotor.
- IDENTIFIERA möjligheter kopplat till totalförsvaret.

### 4. BEFOLKNINGSFÖRSÖRJNING OCH PLATSATTRAKTION
*Vision 2035: Sundsvall är en attraktiv kuststad där människor från hela världen väljer att leva, verka och stanna.*
Fokus:
- UTVECKLA Sundsvall som attraktiv kuststad.
- TESTA nya erbjudanden för inflyttning.
- INVESTERA i hållbara, klimatneutrala livsmiljöer.
- UTVECKLA Sundsvall som plats för barn och unga.
- PRIORITERA kultur-, idrott- och friluftssatsningar.

## GENOMFÖRANDEPRINCIPER
1. **Tillsammans, inte var för sig** - Alla bidrar aktivt.
2. **Tillväxtattityd i vardagen** - Mod, framtidstro, vilja att prova nytt.
3. **Genomförande nära verksamheten** - Omsätt i dagligt arbete.
4. **Fokusera på det som gör skillnad** - Färre, kraftfulla åtgärder.
5. **Följ upp och justera** - Kontinuerligt lärande.
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

    if st.button("Hur laddar jag ner strategin?", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Hur laddar jag ner strategin?"})
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
            # Fallback om bildfilen är trasig
            st.title("Nova 🚀")
    else:
        # Fallback om filen inte finns
        st.markdown("<h1 style='text-align: center; color:#006996;'>Nova 🚀</h1>", unsafe_allow_html=True)
        # Endast synligt för dig vid utveckling
        # st.caption("<div style='text-align: center;'>*(Ladda upp nova-logo-blue.png i roten för att visa logotyp)*</div>", unsafe_allow_html=True)

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
    "<div style='text-align: center; color: #6b7280; font-size: 0.8rem;'>"
    "Nova - Din guide till tillväxtstrategin. Utvecklad av Näringsliv och Tillväxt, Sundsvalls kommun"
    "</div>",
    unsafe_allow_html=True
)