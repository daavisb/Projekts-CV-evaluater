import os
import json
from pathlib import Path

# Gemini klienta inicializācija (aizstāj ar savu metodi, ja lieto Google API)
from google.generativeai import configure, GenerativeModel

configure(api_key="AIzaSyCBmiCr75FFOQUOmdUgk2SAgvIEPTV87Qg")

model = GenerativeModel("models/gemini-2.5-flash-latest")

INPUT_DIR = Path("sample_inputs")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_text(file_path):
    return Path(file_path).read_text(encoding="utf-8")

def build_prompt(jd_text, cv_text):
    return f"""
**Uzdevums:** Salīdzini sekojošo darba aprakstu ar kandidāta CV un sniedz atbildi JSON formātā.

**Darba apraksts:**
{jd_text}

**Kandidāta CV:**
{cv_text}

**Lūdzu, atbildi šādā JSON struktūrā:**
{{
  "match_score": 0-100,
  "summary": "Īss apraksts, cik labi CV atbilst JD.",
  "strengths": [
    "Galvenās prasmes/pieredze no CV, kas atbilst JD"
  ],
  "missing_requirements": [
    "Svarīgas JD prasības, kas CV nav redzamas"
  ],
  "verdict": "strong match | possible match | not a match"
}}
"""

def evaluate_cv(jd_file, cv_file, cv_id):
    jd_text = load_text(jd_file)
    cv_text = load_text(cv_file)

    prompt = build_prompt(jd_text, cv_text)

    # Saglabā prompt (pēc izvēles)
    Path("prompt.md").write_text(prompt, encoding="utf-8")

    # Nosūti uz Gemini
    response = model.generate_content(prompt, generation_config={"temperature": 0.3})
    content = response.text.strip()

    # Parsē JSON atbildi
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        print(f"⚠️ Kļūda parsējot Gemini atbildi par CV {cv_id}")
        return

    # Saglabā JSON
    json_path = OUTPUT_DIR / f"cv{cv_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Ģenerē pārskatu
    report_md = f"""
## Kandidāts CV{cv_id}

**Atbilstības novērtējums:** {result["match_score"]}/100  
**Verdikts:** **{result["verdict"]}**

### Stiprās puses:
{''.join(f"- {s}\n" for s in result["strengths"])}

### Trūkstošās prasības:
{''.join(f"- {m}\n" for m in result["missing_requirements"])}

**Kopsavilkums:**  
{result["summary"]}
"""
    with open(OUTPUT_DIR / f"cv{cv_id}_report.md", "w", encoding="utf-8") as f:
        f.write(report_md.strip())

    print(f"✅ CV{cv_id} analizēts un saglabāts.")

if __name__ == "__main__":
    jd_path = INPUT_DIR / "jd.txt"
    for i in range(1, 4):
        cv_path = INPUT_DIR / f"cv{i}.txt"
        evaluate_cv(jd_path, cv_path, i)
