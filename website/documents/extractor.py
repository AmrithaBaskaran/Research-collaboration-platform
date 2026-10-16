import os
import re
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def clean_text(text: str, max_length: int = None) -> str:
    """Normalize whitespace and clean extracted PDF text."""
    if not text:
        return ""
    # Merge hyphenated line breaks (e.g. "discov-\nery" -> "discovery")
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
    # Replace multiple spaces/tabs with single space
    text = re.sub(r"[ \t]+", " ", text)
    # Clean multiple empty lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = text.strip()
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0] + "..."
    return text


def extract_section_by_patterns(text: str, heading_names: list, stop_names: list, max_len: int = 2500) -> str:
    """Search for text following standard academic heading patterns."""
    for heading in heading_names:
        for stop in stop_names:
            pattern = (
                rf"(?i)(?:^|\n)\s*(?:\d+[\.\)]\s*|[IVXLCDM]+[\.\)]\s*)?{heading}\s*[:\-\—\.\n]\s*(.*?)(?=\n\s*(?:\d+[\.\)]\s*|[IVXLCDM]+[\.\)]\s*)?{stop}\b|\n\n\n|\Z)"
            )
            try:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    extracted = clean_text(match.group(1), max_length=max_len)
                    # Strip any trailing references/bibliography section if caught
                    extracted = re.split(r"(?i)\n\s*(?:references|bibliography|acknowledgments?|\[1\])", extracted)[0].strip()
                    if len(extracted) > 15:
                        return extracted
            except Exception:
                continue
    return ""


def extract_pdf_metadata(file_path: str) -> dict:
    """
    Extracts structured academic research paper metadata using PyMuPDF (fitz).
    
    Returns a dictionary containing:
      - paper_title: str
      - paper_authors: str
      - paper_abstract: str
      - paper_keywords: str
      - paper_conclusions: str
      - paper_gaps: str
      - page_count: int
      - creation_date: str
      - metadata_extracted: bool
    """
    fallback_title = os.path.basename(file_path).rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    result = {
        "paper_title": fallback_title,
        "paper_authors": "Not specified",
        "paper_abstract": "No abstract detected in document.",
        "paper_keywords": "N/A",
        "paper_conclusions": "No conclusion section detected.",
        "paper_gaps": "No explicit research gaps/limitations section detected.",
        "page_count": 1,
        "creation_date": "N/A",
        "metadata_extracted": False,
    }

    if not fitz or not os.path.exists(file_path):
        return result

    try:
        doc = fitz.open(file_path)
        page_count = len(doc)
        result["page_count"] = page_count

        meta = doc.metadata or {}
        
        # 1. Document Creation Date
        raw_date = meta.get("creationDate")
        if raw_date and raw_date.startswith("D:"):
            try:
                date_str = raw_date[2:10]  # YYYYMMDD
                dt = datetime.strptime(date_str, "%Y%m%d")
                result["creation_date"] = dt.strftime("%B %d, %Y")
            except Exception:
                result["creation_date"] = raw_date
        elif raw_date:
            result["creation_date"] = raw_date

        # 2. Extract full text from initial, total, and trailing pages
        first_pages_text = ""
        for i in range(min(3, page_count)):
            first_pages_text += "\n" + doc[i].get_text("text")

        full_text = ""
        for page in doc:
            full_text += "\n" + page.get_text("text")

        last_pages_text = ""
        start_last = max(0, page_count - 3)
        for i in range(start_last, page_count):
            last_pages_text += "\n" + doc[i].get_text("text")

        # 3. Title Extraction
        meta_title = clean_text(meta.get("title", ""))
        if meta_title and len(meta_title) > 3 and not meta_title.lower().endswith((".pdf", ".docx", ".tmp")) and meta_title.lower() not in ["untitled", "microsoft word"]:
            result["paper_title"] = meta_title
        else:
            page0_lines = [l.strip() for l in doc[0].get_text("text").splitlines() if l.strip()]
            candidate_lines = []
            for line in page0_lines[:6]:
                if re.match(r"(?i)^(abstract|keywords|index terms|volume|issn|isbn|ieee|arxiv|acm|conference|proceedings|journal)", line):
                    break
                if len(line) > 3:
                    candidate_lines.append(line)
                    if len(" ".join(candidate_lines)) > 40:
                        break
            if candidate_lines:
                result["paper_title"] = clean_text(" ".join(candidate_lines), max_length=300)

        # 4. Author Extraction (Accurate parsing separating Title, Authors, and Affiliations)
        meta_author = clean_text(meta.get("author", ""))
        if meta_author and len(meta_author) > 2 and meta_author.lower() not in ["unknown", "user", "admin", "author"] and meta_author.lower() != result["paper_title"].lower():
            result["paper_authors"] = meta_author
        else:
            page0_raw = doc[0].get_text("text")
            lines = [l.strip() for l in page0_raw.splitlines() if l.strip()]

            # Find line where Abstract starts
            abstract_idx = len(lines)
            for idx, line in enumerate(lines):
                if re.match(r"(?i)^abstract\b", line):
                    abstract_idx = idx
                    break

            # Discard title words/lines
            title_words = set(re.findall(r"\w+", result["paper_title"].lower()))

            author_candidates = []
            for line in lines[:abstract_idx]:
                # If line is part of title, skip
                line_words = set(re.findall(r"\w+", line.lower()))
                if line_words and line_words.issubset(title_words) and len(line_words) > 1:
                    continue

                # Filter out affiliations, emails, metadata, conference headers, addresses
                if re.search(
                    r"(?i)(department|school\s+of|university|faculty|institute|college|simats|campus|ieee|acm|conference|proceedings|isbn|issn|doi:|downloaded|authorized|copyright|©|http|www|@|\.com|\.edu|\.org|\.in|\b\d{5,6}\b|tamil\s+nadu|india|usa|china|uk|germany|canada)",
                    line,
                ):
                    continue

                cand = clean_text(line)
                if len(cand) > 1 and cand.lower() != result["paper_title"].lower():
                    author_candidates.append(cand)

            if author_candidates:
                result["paper_authors"] = clean_text(", ".join(author_candidates), max_length=250)

        # 5. Keywords Extraction (Prioritize text-based Keywords block over generic conference metadata)
        text_kw_match = re.search(
            r"(?i)(?:^|\n)\s*(?:keywords|key\s*words|index\s*terms)\s*[:\-\—\.\n]\s*(.*?)(?=\n\s*(?:(?:\d+|[IVXLCDM]+)[\.\)]\s*)?(?:[1I]\.?\s+introduction|introduction|background|1\.|\n\n)|\Z)",
            first_pages_text,
            re.DOTALL,
        )
        if text_kw_match:
            extracted_kw = clean_text(text_kw_match.group(1), max_length=300)
            if extracted_kw:
                result["paper_keywords"] = extracted_kw
        else:
            meta_keywords = clean_text(meta.get("keywords", "") or meta.get("subject", ""))
            if meta_keywords and len(meta_keywords) > 3 and not re.match(r"(?i)^(conference|proceedings|isbn|issn|doi)", meta_keywords):
                result["paper_keywords"] = meta_keywords

        # 6. Abstract Extraction
        abstract_stops = [
            "keywords", "key words", "index terms", "introduction", "background", "related work", "overview"
        ]
        abstract_text = extract_section_by_patterns(
            first_pages_text,
            ["abstract", "a\\s*b\\s*s\\s*t\\s*r\\s*a\\s*c\\s*t", "executive summary"],
            abstract_stops,
            max_len=3000,
        )
        if abstract_text:
            result["paper_abstract"] = abstract_text

        # 7. Conclusions & Future Work
        concl_stops = ["acknowledgments?", "references", "bibliography", "appendix", "author contributions", "\\[1\\]"]
        concl_text = extract_section_by_patterns(
            last_pages_text if len(last_pages_text) > 200 else full_text,
            [
                "conclusions? and future work",
                "conclusions? and future directions?",
                "summary and conclusions?",
                "concluding remarks",
                "conclusions?",
                "summary",
            ],
            concl_stops,
            max_len=3000,
        )
        if concl_text:
            result["paper_conclusions"] = concl_text

        # 8. Research Gaps / Limitations / Open Challenges
        gap_stops = [
            "conclusions? and future work", "concluding remarks", "conclusions?",
            "acknowledgments?", "references", "bibliography", "future work"
        ]
        gaps_text = extract_section_by_patterns(
            full_text,
            [
                "limitations? and research gaps?",
                "research gaps? and limitations?",
                "research gaps?",
                "limitations? and threats to validity",
                "threats to validity",
                "limitations?",
                "open challenges",
                "future work",
                "future directions?",
            ],
            gap_stops,
            max_len=2500,
        )
        if gaps_text:
            result["paper_gaps"] = gaps_text

        result["metadata_extracted"] = True
        doc.close()

    except Exception as e:
        result["metadata_extracted"] = False
        result["paper_abstract"] = f"Extraction note: Document parsed with basic properties ({str(e)})."

    return result
