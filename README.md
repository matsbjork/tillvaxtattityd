# Nova – AI-assistent för Sundsvalls Tillväxtstrategi

Detta är källkoden för **www.tillvaxtattityd.se**. Applikationen är en prototyp byggd i Python med Streamlit för att hjälpa Sundsvalls kommuns tjänstepersoner att interagera med tillväxtstrategin.

Webbplatsen fungerar som en brygga innan migrering sker till kommunens egna plattform Eneo.

## 🚀 Funktioner
- **Chatt:** Konversera med Nova (baserad på GPT-4o) som är instruerad enligt "Nova Systemprompt v2.0".
- **Dokumentanalys:** Möjlighet att ladda upp verksamhetsplaner (PDF) för att få direkt feedback kopplat till strategins mål.
- **Responsiv:** Fungerar på mobil och desktop.

## 🛠️ Teknisk Översikt
- **Språk:** Python 3.9+
- **Frontend:** Streamlit
- **AI-motor:** OpenAI API (GPT-4o)
- **Hosting:** Streamlit Community Cloud (kopplat via GitHub)
- **Domän:** One.com (DNS pekar mot Streamlit)

## 💻 Installation & Körning Lokalt

Följ dessa steg för att köra Nova på din egen dator.

### 1. Klona projektet
```bash
git clone [https://github.com/matsbjork/tillvaxtattityd.git](https://github.com/matsbjork/tillvaxtattityd.git)
cd tillvaxtattityd
