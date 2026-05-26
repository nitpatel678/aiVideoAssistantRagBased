## Actionable Items , Decision Making , Task Management  QUestion 
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
import os

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.4
    )

def build_chain(system_prompt: str):
    llm = get_llm()

    return (
        RunnablePassthrough() | RunnableLambda(lambda x : {"text":x}) | ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}"),
        ])
     | llm | StrOutputParser()
     )

def extract_action_items(transcript: str) -> str:
    chain = build_chain(
        "You are an assistant that extracts actionable items from video transcripts. "
        "Actionable items are things that can be done to solve a problem. \n"
        "-Task Description\n"
        "-Owner(who is responsible for doing it)\n"
        "-Deadline(when it should be done)\n"
        "Format as a bullet point list.\n"
    )

    return chain.invoke(transcript)


def extract_key_decisions(transcript: str) -> str:
    chain = build_chain(
        "You are an assistant that extracts decision making from video transcripts. "
        "Decision making is a process of making choices based on information. \n"
        "Format as a bullet point list.\n"
    )

    return chain.invoke(transcript)

def extract_questions(transcript:str)->str:
    chain = build_chain(
        "You are an assistant that extracts questions from video transcripts. "
        "Format as a bullet point list.\n"
    )

    return chain.invoke(transcript)


# Backward-compatible aliases for earlier internal names.
extract_action_item = extract_action_items
extract_decision_making = extract_key_decisions
