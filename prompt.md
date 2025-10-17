**Uzdevums:** Salīdzini sekojošo darba aprakstu ar kandidāta CV un sniedz atbildi JSON formātā.

**Darba apraksts:**
{{JD_TEXT}}

**Kandidāta CV:**
{{CV_TEXT}}

**Lūdzu, atbildi šādā JSON struktūrā:**
{
  "match_score": 0-100,
  "summary": "Īss apraksts, cik labi CV atbilst JD.",
  "strengths": [
    "Galvenās prasmes/pieredze no CV, kas atbilst JD"
  ],
  "missing_requirements": [
    "Svarīgas JD prasības, kas CV nav redzamas"
  ],
  "verdict": "strong match | possible match | not a match"
}

