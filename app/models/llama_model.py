
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_experimental.chat_models import Llama2Chat
from langchain_community.llms import HuggingFaceTextGenInference
from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

template_messages = [
    SystemMessage(content="You are a helpful assistant."),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{text}"),
]
prompt_template = ChatPromptTemplate.from_messages(template_messages)

llm = HuggingFaceTextGenInference(
    inference_server_url="http://127.0.0.1:8080/",
    max_new_tokens=512,
    top_k=50,
    temperature=0.1,
    repetition_penalty=1.03,
)

model = Llama2Chat(llm=llm)

# Set up conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create the LLMChain
chain = LLMChain(llm=model, prompt=prompt_template, memory=memory)

# Run the chain with an initial question
response_1 = chain.run(
    text="What can I see in Vienna? Propose a few locations. Names only, no details."
)
print(response_1)

# Run the chain with a follow-up question
response_2 = chain.run(text="Tell me more about #2.")
print(response_2)
