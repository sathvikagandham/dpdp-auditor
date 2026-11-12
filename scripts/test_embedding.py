from sentence_transformers import SentenceTransformer,util
model=SentenceTransformer('all-MiniLM-L6-v2')
vec1= model.encode("We share your data with third parties for marketing")
vec2=model.encode("Personal data id transferred to external companies for promotional purposes.")
print(vec1.shape)
print(vec2.shape)

