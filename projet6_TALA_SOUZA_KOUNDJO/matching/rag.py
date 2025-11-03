from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def chunk_requirements(jd_text:str, max_len:int=300)->List[str]:
    # Découpe naïve par lignes / puces
    parts = [p.strip("-• \n") for p in jd_text.split("\n") if len(p.strip())>0]
    # Regroupe pour éviter les mini-morceaux
    chunks, buf = [], ""
    for p in parts:
        if len(buf)+len(p) < max_len:
            buf = (buf + " " + p).strip()
        else:
            if buf: chunks.append(buf)
            buf = p
    if buf: chunks.append(buf)
    return chunks or [jd_text]

def retrieve_top_requirements(jd_chunks:List[str], cv_text:str, k:int=3)->List[Tuple[str,float]]:
    corpus = jd_chunks + [cv_text]
    vec = TfidfVectorizer(min_df=1, stop_words=None).fit(corpus)
    M = vec.transform(corpus)
    jd_mat = M[:-1]
    cv_vec = M[-1]
    sims = cosine_similarity(jd_mat, cv_vec)
    scored = [(jd_chunks[i], float(sims[i,0])) for i in range(len(jd_chunks))]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
