"""
.用transformers库，用BertForSequenceClassification微调一个文本分类任务
"""

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import torch
import numpy as np
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
import evaluate


# ============================================================
# 1. 加载数据集
# ============================================================
dataset = load_dataset("json", data_files={"train": "yelp_test.json"})

# 数据量较大，取 5% 快速训练（和 train.py 保持一致）
small_data = dataset["train"].select(range(int(len(dataset["train"]) * 0.01)))
split_data = small_data.train_test_split(train_size=0.8, seed=42)
dataset["train"] = split_data["train"]
dataset["test"] = split_data["test"]

print(f"训练数据量: {len(dataset['train'])}")
print(f"测试数据量: {len(dataset['test'])}")

# 标签数（二分类：0 / 1）
num_labels = 2


# ============================================================
# 2. 加载分词器和模型
# ============================================================
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(
    model_name,
    num_labels=num_labels,
)


# ============================================================
# 3. 数据预处理（分词）
# ============================================================
def tokenize_function(examples):
    """文本分类只需要普通分词，不需要标签对齐"""
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=512,
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)


# ============================================================
# 4. 评估函数
# ============================================================
metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


# ============================================================
# 5. 训练参数
# ============================================================
training_args = TrainingArguments(
    output_dir="./bert_text_classification",
    per_device_train_batch_size=8,
    num_train_epochs=1,
    eval_strategy="epoch",
    learning_rate=2e-5,
    logging_steps=50,
    save_strategy="no",
)


# ============================================================
# 6. 开始训练
# ============================================================
data_collator = DataCollatorWithPadding(tokenizer)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

trainer.train()


# ============================================================
# 7. 保存模型
# ============================================================
save_path = "./bert_text_classification_saved"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"\n模型已保存到: {save_path}")


# ============================================================
# 8. 测试
# ============================================================
print("\n正在加载模型进行测试...")
tokenizer = AutoTokenizer.from_pretrained(save_path)
model = BertForSequenceClassification.from_pretrained(save_path)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.eval()
model.to(device)

test_texts = [
    "The food was amazing and the service was great!",
    "Terrible experience, will never come back.",
    "It was okay, nothing special but not bad either.",
    "I love this place, highly recommend to everyone!",
    "Worst customer service I have ever seen.",
]

print("\n" + "=" * 50)
print("BERT 文本分类模型测试结果")
print("=" * 50)
for idx, text in enumerate(test_texts, 1):
    inputs = tokenizer(text, return_tensors="pt", truncation=True).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
    pred = torch.argmax(logits, dim=-1).item()
    label_name = "好评 (1)" if pred == 1 else "差评 (0)"
    print(f"测试样例{idx}: {text}")
    print(f"  预测结果: {label_name}\n")
