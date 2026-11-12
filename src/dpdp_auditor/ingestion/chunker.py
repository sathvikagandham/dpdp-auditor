import pymupdf
import re
import json
def extract_chunks(pdf_path:str) -> list[str]:
    doc=pymupdf.open(pdf_path)
    full_text=""
    for i in range(len(doc)):
        page_text=doc[i].get_text()
        full_text+=page_text
    doc.close()
    raw_chunks=re.split(r'\n(?=\d+\.\s)',full_text)

    valid_chunks=[]
    for chunk in raw_chunks:
        clean_chunk=chunk.strip()

        if len(clean_chunk)>50:
            valid_chunks.append(clean_chunk)
    with open("data/processed/chunks.json","w",encoding="utf-8") as f:
        json.dump(valid_chunks,f,indent=4)
    return valid_chunks

