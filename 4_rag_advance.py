import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from dotenv import load_dotenv

load_dotenv()

# ===================== 配置 =====================
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

VECTOR_WEIGHT = 0.6
BM25_WEIGHT = 0.4
TOP_K = 8
FINAL_TOP_K = 5  # 精排前保留多少条，混合检索后
RERANK_TOP_K = 2  # 精排后最终输出多少条

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
local_embed_path = os.path.join(BASE_DIR, "bge-large-zh-v1.5")
RERANK_MODEL_ID = "BAAI/bge-reranker-base"  # 首次运行自动从 HuggingFace 下载并缓存

# ===================== 本地 Reranker 加载 =====================
class LocalReranker:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()

    def rank(self, query, docs):
        pairs = [[query, doc.page_content] for doc in docs]
        with torch.no_grad():
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512
            )
            scores = self.model(**inputs, return_dict=True).logits.view(-1).float()
            scores = scores.tolist()

        # 按分数从高到低排序
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked]

# 全局加载一次（避免重复加载）
reranker = LocalReranker(RERANK_MODEL_ID)

# ===================== 工具函数 =====================
def get_all_docs(vectorstore):
    from langchain_core.documents import Document
    data = vectorstore.get(include=["documents", "metadatas"])
    return [Document(page_content=d, metadata=m if m else {}) for d, m in zip(data["documents"], data["metadatas"])]

def format_docs(docs):
    return "\n".join(x.page_content for x in docs)

# ===================== 混合检索 + Reranker =====================
def weighted_hybrid_retrieve(query, vectorstore):
    all_docs = get_all_docs(vectorstore)

    # 1. BM25
    bm25_retriever = BM25Retriever.from_documents(all_docs)
    bm25_retriever.k = TOP_K
    bm25_docs = bm25_retriever.invoke(query)

    # 2. 向量检索
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    vector_docs = vector_retriever.invoke(query)

    # 3. 加权融合
    bm25_scores = {d.page_content: (TOP_K - i) * BM25_WEIGHT for i, d in enumerate(bm25_docs)}
    vector_scores = {d.page_content: (TOP_K - i) * VECTOR_WEIGHT for i, d in enumerate(vector_docs)}

    all_docs_dict = {}
    for doc in bm25_docs + vector_docs:
        cnt = doc.page_content
        total = vector_scores.get(cnt, 0) + bm25_scores.get(cnt, 0)
        all_docs_dict[cnt] = (total, doc)

    sorted_docs = sorted(all_docs_dict.values(), key=lambda x: x[0], reverse=True)
    fused_docs = [doc for score, doc in sorted_docs[:FINAL_TOP_K]]

    # ===================== 【关键：本地 Reranker 重排序】 =====================
    reranked_docs = reranker.rank(query, fused_docs)
    return reranked_docs[:RERANK_TOP_K]

# ===================== RAG 主流程 =====================
def run_rag_qa(query, persist_directory="./chroma_db"):
    if not os.path.exists(persist_directory):
        print("❌ 请先构建向量数据库")
        return

    # 向量库
    embeddings = HuggingFaceEmbeddings(
        model_name=local_embed_path,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    # 检索 + 精排
    final_docs = weighted_hybrid_retrieve(query, vectorstore)

    print("\n" + "="*60)
    print(f"✅ 混合检索 + 本地Reranker完成，返回 {len(final_docs)} 条")
    print("="*60)
    for i, d in enumerate(final_docs):
        print(f"\n结果 {i+1}：\n{d.page_content}\n")

    # LLM
    llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key, base_url=base_url)

    system_prompt = (
        "你是星讯科技有限公司的内部智能人事/行政助手。\n"
        "请严格基于以下提供的公司内部文档内容回答用户问题。\n"
        "如果找不到答案，请直接说“根据提供的文档，我无法回答该问题”，不要编造。\n\n"
        "【参考文档】\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # RAG 链
    rag_chain = (
        {"context": lambda x: format_docs(final_docs), "input": lambda x: x["input"]}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("================ 问答 ================")
    print(f"问题：{query}")
    answer = rag_chain.invoke({"input": query})
    print(f"\n回答：\n{answer}")
    print("="*60)

if __name__ == "__main__":
    chroma_dir = os.path.join(BASE_DIR, "chroma_huawei")
    run_rag_qa("节日和生日福利有什么？", persist_directory=chroma_dir)