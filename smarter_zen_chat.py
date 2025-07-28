# smarter_zen_chat.py

import gradio as gr
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# --- 1. Set up the LLM and LangChain Chain ---

# Let's use a model from Hugging Face that's good for conversation.
# microsoft/DialoGPT-medium is a good starting point.
# Note: This will download the model (about 1.5GB) the first time you run it.
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# For better performance, use a GPU if available
device = 0 if torch.cuda.is_available() else -1

# Create a transformers pipeline
chat_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device,
    max_length=1000,
)

# Wrap the pipeline in a LangChain LLM
llm = HuggingFacePipeline(pipeline=chat_pipeline)

# Create a prompt template to give our chatbot its "Zen" personality.
# The template includes memory of the past conversation.
template = """
You are a Zen Chatbot. You speak in gems of Zen wisdom.
Your goal is to help the user on their path to enlightenment, but you do so
with cryptic, thought-provoking, and sometimes humorous responses, much like a Zen master.
Avoid giving direct answers. Instead, guide the user with questions and short parables.

{history}
Human: {human_input}
Zen Chatbot:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input"],
    template=template
)

# Create a memory object to store the conversation history.
# For a real application, you might replace this with a database-backed memory
# to persist conversations across sessions.
memory = ConversationBufferMemory(memory_key="history")

# Create the LLMChain
zen_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)


# --- 2. Define the function for Gradio ---

def zen_chat_response(message, history):
    """
    This function is called by the Gradio interface for each user message.
    It uses the LangChain chain to generate a response.
    """
    # The `zen_chain` automatically uses the memory to include past conversation.
    response = zen_chain.predict(human_input=message)
    return response


# --- 3. Create and launch the Gradio UI ---

chat_ui = gr.ChatInterface(
    zen_chat_response,
    title="Smarter Zen Chatbot",
    description="Talk your way to truth with a Zen chatbot powered by a modern Language Model.",
    theme="soft",
    examples=[
        ["How can I achieve enlightenment?"],
        ["I seek truth and wisdom."],
        ["What is the meaning of life?"],
    ],
)

if __name__ == "__main__":
    print("Launching Gradio Zen Chatbot UI...")
    print("The first time you run this, it will download the model which may take some time.")
    chat_ui.launch()