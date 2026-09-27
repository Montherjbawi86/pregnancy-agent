import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

DOCS_DIR = "data/documents"

# موديلات embeddings المحتملة في Groq
EMBED_MODELS = [
    "nomic-embed-text-v1.5",
    "nomic-embed-text-v1_5",
    "BAAI/bge-large-en-v1.5",
    "BAAI/bge-small-en-v1.5",
]

_documents = []
_embeddings = []
_index_built = False
_working_model = None


def _load_documents():
    global _documents
    if _documents:
        return
    if not os.path.isdir(DOCS_DIR):
        print(f"⚠️ مجلد {DOCS_DIR} غير موجود")
        return
    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(DOCS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        sections = [s.strip() for s in content.split("\n\n") if len(s.strip()) > 50]
        for sec in sections:
            if len(sec) > 800:
                for i in range(0, len(sec), 800):
                    chunk = sec[i:i+800].strip()
                    if len(chunk) > 50:
                        _documents.append({"text": chunk, "source": filename})
            else:
                _documents.append({"text": sec, "source": filename})
    print(f"📄 تم تحميل {len(_documents)} مقطع")


def _try_embed(texts):
    """يجرب كل موديلات embeddings المتاحة"""
    global _working_model
    models_to_try = [ _working_model ] if _working_model else []
    models_to_try += [m for m in EMBED_MODELS if m != _working_model]

    for model in models_to_try:
        if not model:
            continue
        try:
            response = client.embeddings.create(model=model, input=texts)
            _working_model = model
            print(f"✅ يستخدم: {model}")
            return [item.embedding for item in response.data]
        except Exception as e:
            err = str(e)[:100]
            print(f"  ❌ {model}: {err}")
            continue
    return None


def _cosine_sim(a, b):
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb + 1e-9)


def _build_index():
    global _embeddings, _index_built
    if _index_built:
        return
    _load_documents()
    if not _documents:
        _index_built = True
        return
    print(f"🔨 بناء فهرس RAG لـ {len(_documents)} مقطع...")
    texts = [d["text"] for d in _documents]
    embs = _try_embed(texts)
    if embs and len(embs) == len(texts):
        _embeddings = embs
        print(f"✅ تم بناء الفهرس")
    else:
        print(f"⚠️ فشل — سأستخدم البحث بالكلمات المفتاحية")
    _index_built = True


# ==================== البحث بالكلمات المفتاحية (fallback) ====================
SYNONYMS = {
    "أكل": ["طعام", "تغذية", "أطعمة", "مأكولات"],
    "طعام": ["أكل", "تغذية", "أطعمة"],
    "رياضة": ["تمارين", "نشاط"],
    "فحص": ["تحليل", "فحوصات", "تحاليل", "سونار"],
    "خطر": ["علامات", "تحذير", "طوارئ"],
    "ممنوع": ["تجنب", "تجنبي", "لا"],
    "أسبوع": ["أسابيع", "week"],
    "نزيف": ["دم", "bleeding"],
    "صداع": ["headache"],
    "غثيان": ["قيء", "vomiting"],
    "تغذية": ["أكل", "طعام"],
}

def _keywords(text):
    stop = {"في", "من", "إلى", "على", "عن", "ما", "هي", "هو", "هل", "أن", "و", "أو",
            "the", "a", "an", "is", "are", "of", "to", "in", "and", "or", "for"}
    words = text.replace("؟", " ").replace("?", " ").replace("،", " ").replace(",", " ").replace(".", " ").split()
    result = set()
    for w in words:
        w = w.strip().lower()
        if len(w) > 2 and w not in stop:
            result.add(w)
            for syn in SYNONYMS.get(w, []):
                result.add(syn)
    return result


def _keyword_search(query, top_k=3):
    q_words = _keywords(query)
    if not q_words:
        return []
    scored = []
    for i, doc in enumerate(_documents):
        doc_lower = doc["text"].lower()
        doc_words = _keywords(doc["text"])
        overlap = len(q_words & doc_words)
        direct = sum(1 for w in q_words if w in doc_lower)
        score = overlap * 2 + direct
        if score > 0:
            scored.append((score, i))
    scored.sort(reverse=True)
    return scored[:top_k]


# ==================== الواجهة ====================
def search_knowledge(query: str, top_k: int = 3) -> str:
    _build_index()
    if not _documents:
        return json.dumps({"error": "لا مستندات"}, ensure_ascii=False)

    results = []

    # جرّب embeddings أولاً
    if _embeddings:
        q_emb = _try_embed([query])
        if q_emb:
            q_vec = q_emb[0]
            scores = [(_cosine_sim(q_vec, emb), i) for i, emb in enumerate(_embeddings)]
            scores.sort(reverse=True)
            for score, i in scores[:top_k]:
                doc = _documents[i]
                results.append({
                    "source": doc["source"],
                    "score": round(score, 3),
                    "text": doc["text"][:600],
                })

    # إذا لم ينجح embeddings، استخدم الكلمات المفتاحية
    if not results:
        for score, i in _keyword_search(query, top_k):
            doc = _documents[i]
            results.append({
                "source": doc["source"],
                "score": score,
                "text": doc["text"][:600],
            })

    if not results:
        return json.dumps({"error": "لا نتائج"}, ensure_ascii=False)

    return json.dumps({"results": results}, ensure_ascii=False)
