from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.vectorstores import InMemoryVectorStore
import numpy as np

from typing import List


MESSAGE_SYSTEM_TEMPLATE = """
    You are a data analyst tasked with answering questions based on a provided data set. Please answer the questions based on the provided context below. Make sure not to make any changes to the context, if possible, when preparing answers to provide accurate responses. If the answer cannot be found in context, just politely say that you do not know, do not try to make up an answer.
    When you receive a question from the user, answer only that one question in a concise manner. Do not elaborate with other questions.
    """

MESSAGE_AI_TEMPLATE = """
    The table information is as follows:
    {table_data}
    """

MESSAGE_USER_CONTEXT_TEMPLATE = """
    The context being provided is from a table named: {table_name}
    """

MESSAGE_USER_QUESTION_TEMPLATE = """
    {question}
    """

SIMPLE_PROMPT_TEMPLATE = f"""
    {MESSAGE_SYSTEM_TEMPLATE}

    {MESSAGE_USER_CONTEXT_TEMPLATE}

    {MESSAGE_AI_TEMPLATE}

    Question: {MESSAGE_USER_QUESTION_TEMPLATE}
    """

class QuestionRetriever(BaseRetriever):
    #https://python.langchain.com/docs/how_to/custom_retriever/
    #https://github.com/langchain-ai/langchain/issues/12304

    documents: List[Document]
    k: int = 5000

    #def __init__(self, documents: List[Document], k: int = 5000):
    #    self.documents = documents
    #    self.k = k

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Sync implementations for retriever."""
        matching_documents = []
        for document in self.documents:
            if len(matching_documents) > self.k:
                return matching_documents

            #if query.lower() in document.page_content.lower():
            #    matching_documents.append(document)
            matching_documents.append(document)
        return matching_documents

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def input_only(inpt):
    return inpt["question"]

def followup_question(user_question, question_results, question_name, question_def, embedding_model: Embeddings, chat_model: BaseChatModel, use_inmem_vectors=False, k=50):
    
    row_texts = process_question_results(question_def, question_results)
    question_documents = [Document(page_content=r, metadata={"source": "kobai"}) for r in row_texts]

    if use_inmem_vectors:
        question_retriever = InMemoryVectorStore.from_documents(question_documents, embedding=embedding_model).as_retriever(
    search_kwargs={"k": k}
)
    else:
        question_retriever = QuestionRetriever(documents=question_documents, k=k)

    output_parser = StrOutputParser()

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                MESSAGE_SYSTEM_TEMPLATE),
            HumanMessagePromptTemplate.from_template(
                MESSAGE_USER_CONTEXT_TEMPLATE),
            AIMessagePromptTemplate.from_template(MESSAGE_AI_TEMPLATE),
            HumanMessagePromptTemplate.from_template(
                MESSAGE_USER_QUESTION_TEMPLATE)
        ]
    )

    chain = (
        {"table_name": RunnablePassthrough(), "table_data": RunnableLambda(input_only) | question_retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | chat_model
        | output_parser
    )
    response = chain.invoke(
        {
            "table_name": question_name,
            "question": user_question
        }
    )

    return response

def init_question_search_index(tenant_questions, emb_model):
    
    q_ids = [q["id"] for q in tenant_questions]
    q_descs = [q["description"] for q in tenant_questions]
    q_vectors = emb_model.embed_documents(q_descs)
    return {"ids": q_ids, "descs": q_descs, "vectors": q_vectors}


def question_search(search_text: str, search_index, emb_model, k: int):
    search_vec = emb_model.embed_query(search_text)
    #search_vec = emb_model.encode(search_text)
    matches = __top_vector_matches(search_vec, search_index["vectors"], top=k)

    for mi, m in enumerate(matches):
        matches[mi]["id"] = search_index["ids"][m["index"]]
        matches[mi]["description"] = search_index["descs"][m["index"]]
    return matches

def __top_vector_matches(test_vec, options_list_vec, top=1):
    # Normalize the test vector
    test_vec_norm = test_vec / np.linalg.norm(test_vec)
    # Normalize the option vectors
    options_norm = options_list_vec / np.linalg.norm(options_list_vec, axis=1, keepdims=True)
    
    # Compute cosine similarity (dot product of normalized vectors)
    cosine_similarities = np.dot(options_norm, test_vec_norm)
    
    # Get indexes and similarity scores as dict
    scores_d = [{"index": i, "value": float(v)} for i, v in enumerate(cosine_similarities)]
    
    # Sort dict by similarity score descending
    sorted_d = sorted(scores_d, key=lambda x: x["value"], reverse=True)
    
    # Return top results
    top_d = sorted_d[:top]
    return top_d


def process_question_results(question_def, question_results):

    """
    Returns a template to format each row in Kobai JSON question output into a format readable by LLMs.

    Parameters:
    question_def (any): Kobai standard JSON definition of question.
    question_results (any): JSON representation of Kobai base question results.
    """

    concept_props = {}
    concept_rels = {}

    for ci in question_def["definition"]:
        con_name =  question_def["definition"][ci]["label"].replace("_", " ")
        con_label = question_def["definition"][ci]["label"]
        concept_props[ci] = {"name": con_name, "props": []}
        for p in question_def["definition"][ci]["properties"]:
            if p["hidden"] == False:
                if len(p["aggregates"]) > 0:
                    for a in p["aggregates"]:
                        prop_column = con_label + "_" + p["label"] + "_" + a["type"]
                        prop_name = p["label"].replace("_", " ")
                        concept_props[ci]["props"].append({"column": prop_column, "name": prop_name, "agg": a["type"]})
                else:
                    prop_column = con_label + "_" + p["label"]
                    prop_name = p["label"].replace("_", " ")
                    concept_props[ci]["props"].append({"column": prop_column, "name": prop_name, "agg": None})
        for r in question_def["definition"][ci]["relations"]:
            prop_name = question_def["definition"][ci]["relations"][r]["label"].replace("_", " ")
            for ri in question_def["definition"][ci]["relations"][r]["relationInstances"]:
                if ci not in concept_rels:
                    concept_rels[ci] = {"count": 0, "edges": []}
                concept_rels[ci]["edges"].append({"src": ci, "dst": ri["relationTypeUri"], "name": prop_name})
                concept_rels[ci]["count"] += 1


    row_texts = {}

    for ci, c in concept_props.items():
        p_texts = []
        for p in c["props"]:
            if p["agg"] is None:
                p_text = p["name"] + " " + "{" + p["column"] + "}"  
            else:
                p_text = p["agg"] + " of " + p["name"] + " " + "{" + p["column"] + "}" 
            p_texts.append(p_text)
        c_text = __get_article(c["name"]) + " " + c["name"]
        if len(c["props"]) > 0:
            c_text += " with " + __smart_comma_formatting(p_texts)
        row_texts[ci] = c_text

    max_src = ""
    max_src_count = -1

    for r in concept_rels:
        if concept_rels[r]["count"] > max_src_count:
            max_src_count = concept_rels[r]["count"]
            max_src = r


    concept_order = [max_src]
    if max_src != "":
        for t in concept_rels[max_src]["edges"]:
            concept_order.append(t["dst"])

    for c in concept_props:
        if c not in concept_order:
            concept_order.append(c)

    row_template = concept_order[0] + " is connected to " + " and connected to ".join(concept_order[1:])
    
    for c in row_texts:
        row_template = row_template.replace(c, row_texts[c])

    row_template = row_template[0].upper() + row_template[1:] + "."

    row_texts = []
    for row in question_results:
        row_text = row_template
        for col in row:
            row_text = row_text.replace("{" + col + "}", str(row[col]))
        row_texts.append(row_text)
    #data = "\n".join(row_texts)
    return row_texts
    #return data

def __smart_comma_formatting(items):
    if items == None:
        return ""
    match len(items):
        case 0:
            return ""
        case 1:
            return items[0]
        case 2:
            return items[0] + " and " + items[1]
        case _:
            return ", ".join(items[0: -1]) + " and " + items[-1]
        
def __get_article(label):
    if label[0:1].lower() in ["a", "e", "i", "o", "u"]:
        return "an"
    else:
        return "a"