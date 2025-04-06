import os
import re
import streamlit as st
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Set your OpenAI API key
os.environ[
    "OPENAI_API_KEY"] = "Your api key"

# MongoDB details
db_host = "localhost"
db_port = 27017
db_name = "admin"
collection_name = "user_cln"

# Create a MongoDB client and connect to the database
client = MongoClient(f"mongodb://{db_host}:{db_port}/")
db = client[db_name]

# Initialize the OpenAI language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define a prompt template for rephrasing the query result
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding MongoDB query, and MongoDB result, answer the user question.

    Question: {question}
    MongoDB Query: {query}
    MongoDB Result: {result}
    Answer: """
)


# Function to generate MongoDB query
def generate_mongo_query(question: str) -> dict:
    prompt = (
        f"Generate a MongoDB query in Python dictionary format to answer this question: '{question}'.\n"
        f"Respond only with a Python dictionary. Do not include any explanations or additional text."
    )
    response = llm.invoke(prompt)
    try:
        match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if not match:
            raise ValueError("No valid query found in the response.")
        query_str = match.group(0)
        query = eval(query_str)  # Safely parse the dictionary
        if not isinstance(query, dict):
            raise ValueError("Parsed response is not a valid dictionary.")
        return query
    except Exception as e:
        raise ValueError(f"Failed to parse query: {response.content} - Error: {e}")


# Function to execute MongoDB query
def execute_mongo_query(query: dict) -> list:
    collection = db[collection_name]
    if 'aggregate' in query:
        return list(collection.aggregate(query['pipeline']))
    result = collection.find(query.get('query', {}), query.get('projection', {}))
    return list(result)


# Function to rephrase the answer using the LLM
def rephrase_answer(question: str, query: dict, result: list) -> str:
    if query is None or result is None:
        return "The query could not be generated or executed."
    result_str = str(result)
    prompt = answer_prompt.format(question=question, query=query, result=result_str)
    response = llm.invoke(prompt)
    return response.content.strip()


# MongoDB CRUD operations
def create_document(document: dict):
    collection = db[collection_name]
    result = collection.insert_one(document)
    return result.inserted_id


def update_document(query: dict, update_values: dict):
    collection = db[collection_name]
    result = collection.update_one(query, {"$set": update_values})
    return result.modified_count


def delete_document(query: dict):
    collection = db[collection_name]
    result = collection.delete_one(query)
    return result.deleted_count


# Streamlit UI
st.title("MongoDB Query Generator and Operations")

operation = st.selectbox("Select Operation", ["Query", "Create"])

if operation == "Query":
    question = st.text_input("Enter your question:")
    if st.button("Submit"):
        if question:
            try:
                query = generate_mongo_query(question)
                st.subheader("Generated MongoDB Query")
                st.code(query)
                result = execute_mongo_query(query)
                st.subheader("Query Results")
                st.write(result if result else "No results found.")
                rephrased_answer = rephrase_answer(question, query, result)
                st.subheader("Rephrased Answer")
                st.write(rephrased_answer)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter a question.")

elif operation == "Create":
    create_prompt = st.text_input("Describe the document to create:")
    if st.button("Create Document"):
        if create_prompt:
            try:
                # Generate a document dynamically based on user input
                prompt = (
                    f"Generate a JSON-like Python dictionary that represents the following user-provided data: '{create_prompt}'.\n"
                    f"Respond only with a Python dictionary. Do not include any explanations or additional text."
                )
                response = llm.invoke(prompt)
                try:
                    # Extract and parse the generated dictionary
                    match = re.search(r"\{.*\}", response.content, re.DOTALL)
                    if not match:
                        raise ValueError("No valid dictionary found in the response.")
                    document_str = match.group(0)
                    document = eval(document_str)  # Safely parse the dictionary
                    if not isinstance(document, dict):
                        raise ValueError("Parsed response is not a valid dictionary.")

                    # Insert the generated document into MongoDB
                    document_id = create_document(document)
                    st.success(f"Document created with ID: {document_id}")
                except Exception as e:
                    st.error(f"Failed to parse or insert document: {response.content} - Error: {e}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please describe the document to create.")

elif operation == "Update":
    update_prompt = st.text_input("Describe the document and changes to make:")
    if st.button("Update Document"):
        if update_prompt:
            try:
                update_query = generate_mongo_query(update_prompt)
                query, update_values = update_query.get("query"), update_query.get("update_values")
                modified_count = update_document(query, update_values)
                st.success(f"{modified_count} document(s) updated.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please describe the update.")

elif operation == "Delete":
    delete_prompt = st.text_input("Describe the document to delete:")
    if st.button("Delete Document"):
        if delete_prompt:
            try:
                delete_query = generate_mongo_query(delete_prompt)
                query = delete_query.get("query")
                deleted_count = delete_document(query)
                st.success(f"{deleted_count} document(s) deleted.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please describe the document to delete.")
