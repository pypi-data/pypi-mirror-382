# Préparation des données pour le modèle ChatWOLF, machine conversationnelle spécialisée dans les questions relatives à WOLF.
# Les données sont principalemen extraites des fichiers rst de l'aide en ligne mais également des fichiers py de l'API.
import torch
print(torch.cuda.is_available())

# Importation des modules nécessaires
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import torch
from datasets import load_dataset, Dataset
from transformers import Trainer, TrainingArguments
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rst_directory = Path("D:/ProgrammationGitLab/HECEPython/docs/source")
py_directory = Path("D:/ProgrammationGitLab/HECEPython/wolfhece")
output_directory = Path("D:/ProgrammationGitLab/HECEPython/wolfhece/models/chatwolf")
output_directory.mkdir(parents=True, exist_ok=True)

# Fonction pour extraire le texte des fichiers rst
def extract_text_from_rst(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # Nettoyage du texte
    text = re.sub(r'\.\. _.*?:', '', text)  # Remove references
    text = re.sub(r'\.\. note::.*?\n\n', '', text, flags=re.DOTALL)  # Remove notes
    text = re.sub(r'\.\. warning::.*?\n\n', '', text, flags=re.DOTALL)  # Remove warnings
    text = re.sub(r'\.\. code-block::.*?\n\n', '', text, flags=re.DOTALL)  # Remove code blocks
    text = re.sub(r'\.\. image::.*?\n\n', '', text, flags=re.DOTALL)  # Remove images
    text = re.sub(r'\.\. figure::.*?\n\n', '', text, flags=re.DOTALL)  # Remove figures
    text = re.sub(r'\.\. table::.*?\n\n', '', text, flags=re.DOTALL)  # Remove tables
    text = re.sub(r'\.\. rubric::.*?\n\n', '', text, flags=re.DOTALL)  # Remove rubrics
    text = re.sub(r'\.\. sidebar::.*?\n\n', '', text, flags=re.DOTALL)  # Remove sidebars
    text = re.sub(r'\.\. literalinclude::.*?\n\n', '', text, flags=re.DOTALL)  # Remove literal includes
    text = re.sub(r'\.\. math::.*?\n\n', '', text, flags=re.DOTALL)  # Remove math
    text = re.sub(r'\.\. raw::.*?\n\n', '', text, flags=re.DOTALL)  # Remove raw
    text = re.sub(r'\.\. toctree::.*?\n\n', '', text, flags=re.DOTALL)  # Remove toctree
    text = re.sub(r'\.\. index::.*?\n\n', '', text, flags=re.DOTALL)  # Remove index
    text = re.sub(r'\.\. glossary::.*?\n\n', '', text, flags=re.DOTALL)  # Remove glossary
    text = re.sub(r'\.\. footnote::.*?\n\n', '', text, flags=re.DOTALL)  # Remove footnotes
    text = re.sub(r'\.\. citation::.*?\n\n', '', text, flags=re.DOTALL)  # Remove citations
    text = re.sub(r'\.\. epigraph::.*?\n\n', '', text, flags=re.DOTALL)  # Remove epigraphs
    text = re.sub(r'\.\. highlight::.*?\n\n', '', text, flags=re.DOTALL)  # Remove highlights
    text = re.sub(r'\.\. hlist::.*?\n\n', '', text, flags=re.DOTALL)  # Remove hlists
    text = re.sub(r'\.\. csv-table::.*?\n\n', '', text, flags=re.DOTALL)  # Remove csv-tables
    text = re.sub(r'\.\. list-table::.*?\n\n', '', text, flags=re.DOTALL)  # Remove list-tables
    text = re.sub(r'\.\. contents::.*?\n\n', '', text, flags=re.DOTALL)  # Remove contents
    text = re.sub(r'\.\. include::.*?\n\n', '', text, flags=re.DOTALL)  # Remove includes
    text = re.sub(r'\.\. admonition::.*?\n\n', '', text, flags=re.DOTALL)  # Remove admonitions
    text = re.sub(r'\.\. note::.*?\n\n', '', text, flags=re.DOTALL)  # Remove notes
    text = re.sub(r'\.\. tip::.*?\n\n', '', text, flags=re.DOTALL)  # Remove tips
    text = re.sub(r'\.\. important::.*?\n\n', '', text, flags=re.DOTALL)  # Remove importants
    text = re.sub(r'\.\. caution::.*?\n\n', '', text, flags=re.DOTALL)  # Remove cautions
    text = re.sub(r'\.\. seealso::.*?\n\n', '', text, flags=re.DOTALL)  # Remove seealso

    return text

def scan_files() -> List[Path]:
    # Scan all files and extract text
    documents = []
    for rst_file in rst_directory.rglob("*.rst"):
        text = extract_text_from_rst(rst_file)
        if text.strip():  # Only add non-empty documents
            documents.append(Document(page_content=text, metadata={"source": str(rst_file)}))
            logger.info(f"Extracted text from {rst_file}")
    for py_file in py_directory.rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8') as file:
            text = file.read()
            if text.strip():  # Only add non-empty documents
                documents.append(Document(page_content=text, metadata={"source": str(py_file)}))
                logger.info(f"Extracted text from {py_file}")
    logger.info(f"Total documents extracted: {len(documents)}")
    return documents

def split_and_prepare_data(documents: List[Document]) -> None:
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )
    texts = text_splitter.split_documents(documents)
    logger.info(f"Total text chunks created: {len(texts)}")
    # Save texts to JSONL for dataset creation
    jsonl_path = output_directory / "chatwolf_data.jsonl"
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for text in texts:
            json.dump({"text": text.page_content}, f)
            f.write('\n')
    logger.info(f"Saved text chunks to {jsonl_path}")
    return texts, jsonl_path

def train_model():
    # Load dataset
    dataset = load_dataset('json', data_files=str(jsonl_path))['train']
    # Split dataset into training and validation sets
    train_test_split = dataset.train_test_split(test_size=0.1)
    train_dataset = train_test_split['train']
    eval_dataset = train_test_split['test']
    logger.info(f"Training dataset size: {len(train_dataset)}")
    logger.info(f"Validation dataset size: {len(eval_dataset)}")
    # Define model and tokenizer
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name)
    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_directory / "output",
        eval_strategy="epoch",
        num_train_epochs=3,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        save_strategy="epoch",
        logging_dir=output_directory / "logs",
        logging_steps=10,
        save_total_limit=2,
        fp16=False,  # Set to False to avoid FP16 errors on unsupported hardware
        load_best_model_at_end=True,
    )
    # Define data collator
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    eval_dataset = eval_dataset.map(tokenize_function, batched=True)
    train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])
    eval_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])
    # Define data collator for causal language modeling
    from transformers import DataCollatorForLanguageModeling
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )
    # Train the model
    trainer.train()
    # Save the fine-tuned model
    trainer.save_model(output_directory / "chatwolf_model")
    logger.info(f"Saved fine-tuned model to {output_directory / 'chatwolf_model'}")
    return model, tokenizer

def load_model_and_tokenizer():
    model = AutoModelForCausalLM.from_pretrained(output_directory / "chatwolf_model")
    tokenizer = AutoTokenizer.from_pretrained("gpt2", use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer

documents = scan_files()
texts, jsonl_path = split_and_prepare_data(documents)

if False:
    model, tokenizer = train_model()
else:
    model, tokenizer = load_model_and_tokenizer()


# Create embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(texts, embeddings)
vector_store.save_local(str(output_directory / "faiss_index"))
logger.info(f"Saved FAISS index to {output_directory / 'faiss_index'}")
# Create retrieval QA chain
llm_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512, temperature=0.7, top_p=0.9, repetition_penalty=1.2)
hf_llm = HuggingFacePipeline(pipeline=llm_pipeline)
qa_chain = RetrievalQA.from_chain_type(llm=hf_llm, chain_type="stuff", retriever=vector_store.as_retriever())
# Save the QA chain
import pickle
with open(output_directory / "qa_chain.pkl", 'wb') as f:
    pickle.dump(qa_chain, f)
logger.info(f"Saved QA chain to {output_directory / 'qa_chain.pkl'}")
# Example usage of the QA chain
def answer_question(question: str) -> str:
    return qa_chain.run(question)
example_question = "How to create a new map in WOLF?"
answer = answer_question(example_question)
logger.info(f"Question: {example_question}\nAnswer: {answer}")
