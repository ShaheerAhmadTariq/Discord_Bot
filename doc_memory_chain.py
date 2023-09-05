from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI as LangChainOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document

from database import connect_to_db
def chain_setup(user_id, user_name):
    # get history msg and add it to memory
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")

    _, message_history, _, _ = connect_to_db()

    conv = message_history.find_one({'user_id': user_id})

    chat_history = ""

    if conv:
        messages = conv['messages']
        for message in messages[-5:]:
            if 'user' in message:
                chat_history += f"Student: {message['user']}\n"
            elif 'bot' in message:
                chat_history += f"Professor: {message['bot']}\n"
    else:
        print("No previous conversation history found for this user.")

    # Context from your database or any other source
    context = "This is the context that ChatGPT should consider."

    template = f"""
    You are a chatbot having a conversation with a student.

    Given the following extracted parts of a long document and a question, create a final answer.
    {{context}}


    {{chat_history}}
    Student: {{human_input}}
    Professor:
    """

    prompt = PromptTemplate(input_variables=["chat_history", "human_input", "context"], template=template)

    chat = load_qa_chain(LangChainOpenAI(temperature=0.5), chain_type="stuff", memory=memory, prompt=prompt)

    return chat, chat_history

def get_chain_response(user_id, user_text, user_name):
    conv_chain, chat_history = chain_setup(user_id=user_id, user_name=user_name)

    # Assuming `docs` is extracted from somewhere as relevant context.
    # For the sake of this example, let's keep it empty.
    docs = ["Beyond just offering life advice, Google's AI tool aims to provide assistance across 21 different life skills that range from specialized medical fields to hobby suggestions. The planner function can even create customized financial budgets.\n", '\n', '\n', '\n', '\n']
    doc = Document(page_content="Beyond just offering life advice, Google's AI tool aims to provide assistance across 21 different life skills that range from specialized medical fields to hobby suggestions. The planner function can even create customized financial budgets.\n", metadata={"some_key": "some_value"})

    response = conv_chain({"input_documents": doc, "human_input": user_text}, return_only_outputs=True)
    return response['output_text']

# You can now use `get_chain_response` to obtain chatbot responses.
