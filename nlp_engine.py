from __future__ import annotations

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import math
import re
from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class DocumentReader:

    @staticmethod
    def read_file(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            return DocumentReader._read_txt(file_path)
        elif ext == ".pdf":
            return DocumentReader._read_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return DocumentReader._read_docx(file_path)
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {ext}")

    @staticmethod
    def _read_txt(file_path: str) -> str:
        encodings: List[str] = ["utf-8", "utf-8-sig", "latin-1", "cp1254", "iso-8859-9"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Metin dosyası uygun karakter kodlaması ile okunamadı: {file_path}")

    @staticmethod
    def _read_pdf(file_path: str) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            extracted_pages: List[str] = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(extracted_pages).strip()
        except ImportError:
            raise ImportError("pypdf kütüphanesi gereklidir.")
        except Exception as e:
            raise RuntimeError(f"PDF okuma hatası: {str(e)}")

    @staticmethod
    def _read_docx(file_path: str) -> str:
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs: List[str] = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs).strip()
        except ImportError:
            raise ImportError("python-docx kütüphanesi gereklidir.")
        except Exception as e:
            raise RuntimeError(f"DOCX okuma hatası: {str(e)}")


class TextPreprocessor:

    NOISE_UPPERWORDS: Set[str] = {
        "EĞİTİM", "DENEYİM", "PROJELER", "YETENEKLER", "YETENEKLERİ", "SERTİFİKALAR",
        "İLETİŞİM", "HAKKINDA", "PROFILE", "EXPERIENCE", "EDUCATION", "SKILLS",
        "PROJECTS", "SUMMARY", "AUTHOR", "DIARY", "LIFE", "TELEFON", "YAZILIM",
        "POSTA", "STRATEGY", "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
        "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
        "OCAK", "ŞUBAT", "MART", "NİSAN", "MAYIS", "HAZİRAN", "TEMMUZ", "AĞUSTOS",
        "EYLÜL", "EKİM", "KASIM", "ARALIK", "PAZARTESİ", "SALI", "ÇARŞAMBA",
        "PERŞEMBE", "CUMA", "CUMARTESİ", "PAZAR"
    }

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        pattern = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+"
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    @staticmethod
    def chunk_text(text: str, max_words: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        if len(words) <= max_words:
            return [text]

        chunks: List[str] = []
        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunk_words = words[start:end]
            chunks.append(" ".join(chunk_words))
            if end == len(words):
                break
            start += max_words - overlap
        return chunks


class DocumentClassifier:

    @staticmethod
    def classify(text: str) -> str:
        t_lower = text.lower()

        cv_keywords = ["özgeçmiş", "curriculum vitae", "deneyim", "yetenekler", "eğitim", "projeler", "experience", "education", "skills", "github.com", "linkedin.com"]
        paper_keywords = ["abstract", "özet", "giris", "giriş", "yöntem", "methodology", "bulgular", "results", "sonuçlar", "kaynakça", "references", "doi:", "ieee"]
        legal_keywords = ["dilekçe", "mahkemesi", "sözleşme", "taraf", "taraflar", "maddesi", "hüküm", "talep", "karar", "arz ederim", "gereğini"]

        cv_score = sum(1 for k in cv_keywords if k in t_lower)
        paper_score = sum(1 for k in paper_keywords if k in t_lower)
        legal_score = sum(1 for k in legal_keywords if k in t_lower)

        if cv_score >= 2 and cv_score >= paper_score and cv_score >= legal_score:
            return "CV / Resumé"
        elif paper_score >= 2 and paper_score >= legal_score:
            return "Research Paper / Technical Report"
        elif legal_score >= 2:
            return "Legal Document / Petition"
        else:
            return "General Document"


class AdvancedEntityExtractor:

    STOP_WORDS: Set[str] = {
        "ve", "ile", "bir", "bu", "da", "de", "için", "olan", "olarak", "gibi",
        "kadar", "daha", "çok", "en", "var", "yok", "ama", "fakat", "ancak", "veya",
        "ya", "çünkü", "ise", "diye", "şu", "o", "biz", "siz", "onlar", "ben", "sen",
        "tarafından", "üzerine", "göre", "sonra", "önce", "kendi", "tüm", "her", "ilgili",
        "a", "an", "the", "and", "or", "but", "about", "above", "after", "again", "against",
        "all", "am", "are", "as", "at", "be", "because", "been", "before", "being", "below",
        "between", "both", "by", "could", "did", "do", "does", "doing", "down", "during",
        "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "her",
        "here", "him", "his", "how", "if", "in", "into", "is", "it", "its", "me", "more",
        "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "other",
        "our", "out", "over", "own", "same", "she", "should", "so", "some", "such", "than",
        "that", "their", "them", "then", "there", "these", "they", "this", "those", "through",
        "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when",
        "where", "which", "while", "who", "whom", "why", "with", "would", "you", "your", "end"
    }

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, List[str]]:
        entities: Dict[str, List[str]] = {
            "emails": [],
            "urls": [],
            "citations": [],
            "acronyms": [],
            "dates": [],
            "metrics": []
        }

        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
        entities["emails"] = sorted(list(set(emails)))

        urls = re.findall(r"(?:https?://[^\s<>\"']+|github\.com/[A-Za-z0-9_.-]+)", text)
        entities["urls"] = sorted(list(set(urls)))

        citations = re.findall(r"\[\d+(?:[\s,\-–\d]+)?\]|\([A-Z][a-z]+(?:\s+et\s+al\.)?,\s*(?:19|20)\d{2}\)", text)
        entities["citations"] = sorted(list(set(citations)))

        raw_acronyms = set(re.findall(r"\b[A-Z0-9]{2,6}(?:-[A-Z0-9]+)?\b", text))
        text_lower = text.lower()
        roman_numerals = {"II", "III", "IV", "VI", "VII", "VIII", "IX", "XI"}

        valid_acronyms: List[str] = []
        for ac in raw_acronyms:
            if ac in roman_numerals or ac in TextPreprocessor.NOISE_UPPERWORDS:
                continue
            if ac.isdigit():
                continue
            if text_lower.count(ac.lower()) > text.count(ac):
                continue
            valid_acronyms.append(ac)

        entities["acronyms"] = sorted(valid_acronyms)

        dates = re.findall(r"\b(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}[./-]\d{1,2}[./-]\d{1,2})\b", text)
        entities["dates"] = sorted(list(set(dates)))

        metrics = re.findall(r"\b\d+(?:\.\d+)?%\b|[\$€₺£]\s*\d+(?:,\d+)*(?:\.\d+)?", text)
        entities["metrics"] = sorted(list(set(metrics)))

        return entities

    @classmethod
    def extract_keywords(cls, text: str, top_n: int = 15) -> List[Dict[str, Any]]:
        words = re.findall(r"\b[A-Za-z0-9ğüşıöçĞÜŞİÖÇ\.-]{2,}\b", text)
        clean_words: List[str] = []

        for w in words:
            wl = w.lower().strip(".-")
            if wl not in cls.STOP_WORDS and not wl.isdigit() and len(wl) > 2:
                clean_words.append(wl)

        if not clean_words:
            return []

        total_words = len(clean_words)
        word_counts = Counter(clean_words)

        bigrams = [
            f"{clean_words[i]} {clean_words[i+1]}"
            for i in range(len(clean_words) - 1)
        ]
        bigram_counts = Counter(bigrams)

        results: List[Dict[str, Any]] = []
        used_words_in_bigrams: Set[str] = set()

        for term, count in bigram_counts.most_common(6):
            if count >= 2:
                results.append({
                    "term": term,
                    "frequency": count,
                    "type": "Bigram",
                    "score": round((count / total_words) * 150, 2)
                })
                used_words_in_bigrams.update(term.split())

        for term, count in word_counts.most_common(top_n):
            if term in used_words_in_bigrams and count <= 2:
                continue
            score = round((count / total_words) * 100, 2)
            results.append({
                "term": term,
                "frequency": count,
                "type": "Unigram",
                "score": score
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]


class NLPEngine:

    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6") -> None:
        self.model_name = model_name
        self._summarizer_pipeline: Any = None
        self._transformers_available: bool = False
        self._check_transformers()

    def _check_transformers(self) -> None:
        try:
            import torch
            import transformers
            self._transformers_available = True
        except ImportError:
            self._transformers_available = False

    def load_pipeline(self) -> bool:
        if not self._transformers_available:
            return False
        if self._summarizer_pipeline is not None:
            return True

        try:
            from transformers import pipeline
            self._summarizer_pipeline = pipeline(
                "summarization",
                model=self.model_name,
                device=-1
            )
            return True
        except Exception:
            self._summarizer_pipeline = None
            return False

    def summarize(self, text: str, doc_type: str = "General Document", progress_callback: Optional[Callable[[str, int], None]] = None) -> str:
        clean_text = TextPreprocessor.clean(text)
        if not clean_text:
            return "Özetlenecek içerik bulunamadı."

        word_count = len(clean_text.split())
        if word_count < 35:
            return clean_text

        if doc_type == "Research Paper / Technical Report":
            clean_text = re.sub(r"\[\d+(?:[\s,\-–\d]+)?\]|\([A-Z][a-z]+(?:\s+et\s+al\.)?,\s*(?:19|20)\d{2}\)", "", clean_text)

        if self.load_pipeline() and self._summarizer_pipeline:
            try:
                if progress_callback:
                    progress_callback("Yapay zeka modeli ile özet çıkartılıyor...", 50)

                chunks = TextPreprocessor.split_sentences(clean_text)
                chunk_text = " ".join(chunks[:15])

                input_len = len(chunk_text.split())
                max_len = min(150, max(40, int(input_len * 0.5)))
                min_len = min(25, int(input_len * 0.2))

                res = self._summarizer_pipeline(
                    chunk_text,
                    max_length=max_len,
                    min_length=min_len,
                    do_sample=False,
                    truncation=True
                )
                if res and isinstance(res, list):
                    return res[0]["summary_text"].strip()
            except Exception:
                pass

        if progress_callback:
            progress_callback("Metinsel ağırlık analizi ile özet oluşturuluyor...", 70)

        return self._summarize_extractive(clean_text, doc_type)

    def _summarize_extractive(self, text: str, doc_type: str = "General Document", num_sentences: int = 4) -> str:
        sentences = TextPreprocessor.split_sentences(text)
        if len(sentences) <= num_sentences:
            return "\n".join(sentences)

        words = re.findall(r"\b[A-Za-z0-9ğüşıöçĞÜŞİÖÇ]{3,}\b", text.lower())
        word_freq = Counter([w for w in words if w not in AdvancedEntityExtractor.STOP_WORDS])

        if not word_freq:
            return "\n".join(sentences[:num_sentences])

        max_freq = max(word_freq.values())
        norm_freq = {k: v / max_freq for k, v in word_freq.items()}

        sentence_scores: List[Tuple[float, int, str]] = []
        for i, sentence in enumerate(sentences):
            sent_words = re.findall(r"\b[A-Za-z0-9ğüşıöçĞÜŞİÖÇ]{3,}\b", sentence.lower())
            if not sent_words:
                continue

            score = sum(norm_freq.get(w, 0.0) for w in sent_words) / len(sent_words)

            if doc_type == "CV / Resumé":
                if any(kw in sentence.lower() for kw in ["mühendis", "geliştirici", "developer", "engineer", "uzman", "lisans", "üniversite", "mezun", "yazılım"]):
                    score *= 1.6
                if i == 0:
                    score *= 1.5
            else:
                if i == 0:
                    score *= 1.4
                elif i < 3:
                    score *= 1.2

            sentence_scores.append((score, i, sentence))

        sentence_scores.sort(key=lambda x: x[0], reverse=True)
        top_sentences = sorted(sentence_scores[:num_sentences], key=lambda x: x[1])
        return "\n".join(s[2] for s in top_sentences)

    def generate_takeaways(self, text: str, keywords: List[Dict[str, Any]], entities: Dict[str, List[str]]) -> List[str]:
        takeaways: List[str] = []

        top_terms = [k["term"] for k in keywords[:5]]
        if top_terms:
            takeaways.append(f"Öne çıkan anahtar kavramlar: {', '.join(top_terms)}.")

        if entities.get("acronyms"):
            takeaways.append(f"Tespit edilen teknolojiler ve kuruluşlar: {', '.join(entities['acronyms'][:5])}.")

        if entities.get("metrics"):
            takeaways.append(f"Kilit performans göstergeleri ve metrikler: {', '.join(entities['metrics'][:4])}.")

        sentences = TextPreprocessor.split_sentences(text)
        if sentences and len(takeaways) < 3:
            takeaways.append(f"Önemli bulgu: {sentences[0]}")

        return takeaways[:3]

    def analyze_document(
        self,
        raw_text: str,
        filename: str = "Dokuman",
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        if progress_callback:
            progress_callback("Metin temizleniyor ve ön işleme yapılıyor...", 10)

        cleaned_text = TextPreprocessor.clean(raw_text)
        words = cleaned_text.split()
        word_count = len(words)
        char_count = len(cleaned_text)

        doc_type = DocumentClassifier.classify(cleaned_text)

        if progress_callback:
            progress_callback("Varlıklar (Entities) ve Anahtar Kelimeler ayıklanıyor...", 30)

        entities = AdvancedEntityExtractor.extract_entities(cleaned_text)
        keywords = AdvancedEntityExtractor.extract_keywords(cleaned_text, top_n=15)

        summary = self.summarize(cleaned_text, doc_type, progress_callback)
        takeaways = self.generate_takeaways(cleaned_text, keywords, entities)

        if progress_callback:
            progress_callback("Analiz tamamlanıyor...", 90)

        reading_time = max(1.0, round(word_count / 200, 1))

        payload = {
            "filename": filename,
            "document_type": doc_type,
            "raw_text": cleaned_text,
            "summary": summary,
            "executive_summary": summary,
            "key_takeaways": takeaways,
            "keywords": keywords,
            "entities": entities,
            "metrics": {
                "word_count": word_count,
                "char_count": char_count,
                "reading_time_minutes": reading_time
            }
        }

        if progress_callback:
            progress_callback("İşlem Tamamlandı.", 100)

        return payload


nlp_engine = NLPEngine()