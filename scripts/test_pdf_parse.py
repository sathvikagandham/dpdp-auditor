import pymupdf
doc=pymupdf.open("data/raw/dpdp_act.pdf")
n=len(doc)
print(f"The number of pages are {n}")
third_page=doc[2]
text=third_page.get_text()
print(text[:500])
doc.close()