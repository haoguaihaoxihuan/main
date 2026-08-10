import os
import jieba
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

load_dotenv()
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
PDF_PATH = "./docs/华为2025年年报_0401.pdf"
LOCAL_MODEL_DIR = "./bge-large-zh"
CHROMA_DIR = "./chroma_huawei"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 5
ALPHA = 0.6

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

# PDF 加载、分块
def load_and_split(pdf_path):
    """加载单个 PDF 并用 RecursiveCharacterTextSplitter 分块"""
    loader = PDFPlumberLoader(pdf_path)
    docs = loader.load()
    print(f"PDF共 {len(docs)}页")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "；", "，", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"  分割为 {len(chunks)} 个文本块\n")
    return chunks


# bge-large-zh 本地加载
def get_embeddings():
    """本地加载 bge-large-zh"""
    if not os.path.exists(LOCAL_MODEL_DIR):
        print(f"本地模型不存在，从 hf-mirror 下载 bge-large-zh 到 {LOCAL_MODEL_DIR} ...")
        snapshot_download("BAAI/bge-large-zh", local_dir=LOCAL_MODEL_DIR)
    else:
        print(f"从本地加载模型: {LOCAL_MODEL_DIR}")
    return HuggingFaceEmbeddings(
        model_name=LOCAL_MODEL_DIR,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


# 向量库构建
def build_vectorstore(chunks, embeddings):
    print("构建向量库 ...")
    if os.path.exists(CHROMA_DIR):
        vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
        print(f"  加载已有向量库，共 {vectorstore._collection.count()} 条")
    else:
        vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
        print(f"  新建向量库，共 {len(chunks)} 条")
    return vectorstore


# BM25 索引构建
def build_bm25(chunks):
    """为所有文本块构建 BM25 索引"""
    print("构建 BM25 索引 ...")
    texts = [doc.page_content for doc in chunks]
    tokenized = [jieba.lcut(t) for t in texts]
    bm25 = BM25Okapi(tokenized)
    print(f"  BM25 索引就绪，共 {len(texts)} 条\n")
    return bm25, texts


# 5. 混合检索（③）
class HybridRetriever:
    """稀疏加稠密加权融合检索"""
    def __init__(self, vectorstore, bm25, texts, embeddings, alpha=0.6, k=5):
        self.vector_retriever = vectorstore.as_retriever(search_kwargs={"k": k * 2})
        self.bm25 = bm25
        self.texts = texts
        self.embeddings = embeddings
        self.alpha = alpha
        self.k = k

    def retrieve(self, query):
        # 向量检索
        dense_docs = self.vector_retriever.invoke(query)
        # 算余弦相似度
        q_emb = np.array(self.embeddings.embed_query(query))
        d_embs = np.array([self.embeddings.embed_query(d.page_content) for d in dense_docs])
        dense_scores = cosine_similarity([q_emb], d_embs)[0]

        # BM25 检索
        tokenized_query = jieba.lcut(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_norm = bm25_scores / (bm25_scores.max() + 1e-8)

        # 融合
        scores = {}
        for i, doc in enumerate(dense_docs):
            for j, t in enumerate(self.texts):
                if doc.page_content == t:
                    scores[j] = self.alpha * bm25_norm[j] + (1 - self.alpha) * dense_scores[i]
                    break

        # 按混合分数排序，取 top_k
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:self.k]
        return [self.texts[i] for i, _ in ranked], [s for _, s in ranked]


# 6. RAG 问答
def run_qa(hybrid_retriever, query):
    """混合检索 + LLM 生成"""
    print(f"提问: {query}")
    docs, scores = hybrid_retriever.retrieve(query)
    context = "\n\n".join(docs)
    llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key, base_url=base_url)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的年报分析助手。请严格基于以下华为年报内容回答问题。"
                   "如果找不到答案，直接说'年报中未提及'，禁止编造。\n\n【年报参考】\n{context}"),
        ("human", "{input}"),
    ])

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "input": query})

    print(f"\n检索到 {len(docs)} 个相关片段:")
    for i, (doc, score) in enumerate(zip(docs, scores)):
        print(f"  [{i+1}] 得分={score:.4f} | {doc[:80]}...")
    print(f"\n回答: {answer}")
    return answer


# 7. 主流程
if __name__ == "__main__":
    # ① 分块
    chunks = load_and_split(PDF_PATH)
    # ② 加载 bge-large-zh
    embeddings = get_embeddings()
    # 构建向量库
    vectorstore = build_vectorstore(chunks, embeddings)
    # ③ 构建 BM25 + 混合检索器
    bm25, texts = build_bm25(chunks)
    hybrid_retriever = HybridRetriever(vectorstore, bm25, texts, embeddings, alpha=ALPHA, k=TOP_K)
    # 测试问答
    queries = [
        "华为2024年销售收入是多少？",
        "华为2024年研发投入占收入的比例是多少？",
    ]
    for q in queries:
        run_qa(hybrid_retriever, q)
