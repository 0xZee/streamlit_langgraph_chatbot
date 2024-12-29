from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
#from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage

class ChatBot:
    AVAILABLE_MODELS = {
        "llama-3.2-3b-preview": "Llama 3.2 3B",
        "llama3-8b-8192": "Llama 3 8B",
        "gemma2-9b-it": "Gemma 2 9B",
        "mixtral-8x7b-32768": "Mixtral 8x7B"
    }

    def __init__(self, groq_api_key: str, model_name: str = "llama-3.2-3b-preview"):
        self.groq_api_key = groq_api_key
        self.model_name = model_name
        self.llm = self._setup_llm()
        self.app = self._setup_workflow()

    def _setup_llm(self):
        return ChatGroq(
            temperature=0.1,
            groq_api_key=self.groq_api_key,
            model_name=self.model_name
        )

    def _setup_workflow(self):
        workflow = StateGraph(state_schema=MessagesState)
        
        def call_model(state: MessagesState):
            #sys_msg = SystemMessage(content="You are a helpful assistant ")
            response = self.llm.invoke(state["messages"])
            return {"messages": response}

        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)
        
        return workflow.compile(checkpointer=MemorySaver())

    def chat(self, message: str, thread_id: str):
        return self.app.invoke(
            {"messages": [{"role": "user", "content": message}]},
            {"configurable": {"thread_id": thread_id}}
        )

    def update_model(self, model_name: str):
        self.model_name = model_name
        self.llm = self._setup_llm()
        self.app = self._setup_workflow()
