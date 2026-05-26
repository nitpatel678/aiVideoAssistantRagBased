from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.4
    )


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    llm = get_llm()

    # MAP STEP
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that summarizes video transcripts."),
        ("human", "Summarize the following transcript:\n\n{transcript}")
    ])

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    chunk_summaries = [
        map_chain.invoke({"transcript": chunk})
        for chunk in chunks
    ]

    # REDUCE STEP
    combined_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that combines summaries into a final summary."),
        ("human", "Combine the following summaries into a single concise summary:\n\n{summaries}")
    ])

    combined_chain = combined_prompt | llm | StrOutputParser()

    final_summary = combined_chain.invoke({
        "summaries": "\n\n".join(chunk_summaries)
    })

    return final_summary


def generate_title(transcript: str) -> str:
    llm = get_llm()

    title_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that generates concise video titles."),
        ("human", "Generate a concise and catchy title for a video with the following transcript:\n\n{transcript}")
    ])

    title_chain = title_prompt | llm | StrOutputParser()

    return title_chain.invoke({"transcript": transcript})
