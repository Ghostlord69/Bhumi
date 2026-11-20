# हस्तलिखित हिंदी डेटासेट (Handwritten Hindi Dataset)

Bhumi के OCR मॉडल को सामान्य संपत्ति / जमाबंदी कागज़ों पर चलाने के लिए यहाँ **दो हिंदी हस्तलेख** स्रोत रखे गए हैं।

## इस फ़ोल्डर में क्या है

| पथ | क्या है | कितना | किस काम के लिए |
|-----|---------|--------|----------------|
| `images/` + `labels/labels.tsv` | UCI Devanagari **अक्षर** (character) | 1,840 PNG, 46 वर्ग | अक्षर-स्तरीय CNN / pretrain |
| `words/` | IIIT-INDIC-HW-WORDS-Hindi **शब्द** (sample) | 300 JPG + हिंदी पाठ | शब्द OCR / CRNN–CTC / TrOCR fine-tune |
| `dataset_info.json` | UCI मेटाडेटा | — | स्रोत लिंक |
| `words/dataset_info.json` | शब्द डेटा मेटाडेटा | — | स्रोत + citation |

## पूर्ण डेटासेट (ट्रेनिंग के लिए अनुशंसित)

सामान्य property paper के लिए **शब्द-स्तरीय** डेटा ज़्यादा उपयोगी है:

1. **IIIT-INDIC-HW-WORDS-Hindi** — ~95,431 हस्तलिखित हिंदी शब्द  
   - https://ilocr.iiit.ac.in/dataset/18/  
   - Hugging Face: https://huggingface.co/datasets/c3rl/IIIT-INDIC-HW-WORDS-Hindi  

2. **ICDAR 2024 HWD (Hindi)** — पृष्ठ + शब्द स्तर  
   - https://ilocr.iiit.ac.in/icdar_2024_hwd/dataset.html  

3. **UCI पूर्ण अक्षर सेट** — 92,000 चित्र  
   - https://archive.ics.uci.edu/dataset/389/devanagari+handwritten+character+dataset  

पूरा शब्द सेट डाउनलोड:

```bash
cd ai-service
source .venv/bin/activate
pip install datasets pillow
python scripts/download_hindi_hw.py --out ../samples/handwritten/hindi/words_full --limit 0
```

`--limit 0` = पूरा train split; छोटे परीक्षण के लिए `--limit 2000`।

## संपत्ति कागज़ पर कैसे लगाएँ

1. इन हिंदी शब्दों पर OCR (PaddleOCR `lang=hi` या TrOCR) fine-tune करें।  
2. अपने राज्य की **जमाबंदी / खसरा** स्कैन पर field labels लगाएँ (`ai-service/TRAINING.md`)।  
3. FastAPI `/extract` पहले OCR चलाता है, फिर `ownerName`, `khasraNumber`, `village` आदि निकालता है।  
4. हस्तलेख वाले असली कागज़ पर confidence कम हो तो backend उन्हें officer verification पर भेजता है।

> नोट: सार्वजनिक शब्द डेटासेट में गाँव/खसरा नाम सीमित हो सकते हैं। प्रोटोटाइप के बाद **20–40 असली (匿名) हस्तलिखित जमाबंदी** खुद annotate करना सबसे अच्छा रहता है।
