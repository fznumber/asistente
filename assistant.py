from typing import Optional

from phi.assistant import Assistant
from phi.knowledge import AssistantKnowledge
from phi.llm.groq import Groq
from phi.embedder.openai import OpenAIEmbedder
from phi.embedder.ollama import OllamaEmbedder
from phi.vectordb.pgvector import PgVector2
from phi.storage.assistant.postgres import PgAssistantStorage

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"


def get_groq_assistant(
    llm_model: str = "llama3-70b-8192",
    embeddings_model: str = "text-embedding-3-small",
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Assistant:
    """Get a Groq RAG Assistant."""

    # Define the embedder based on the embeddings model
    embedder = (
        OllamaEmbedder(model=embeddings_model, dimensions=768)
        if embeddings_model == "nomic-embed-text"
        else OpenAIEmbedder(model=embeddings_model, dimensions=1536)
    )
    # Define the embeddings table based on the embeddings model
    embeddings_table = (
        "groq_rag_documents_ollama" if embeddings_model == "nomic-embed-text" else "groq_rag_documents_openai"
    )

    return Assistant(
        name="groq_rag_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=Groq(model=llm_model),
        storage=PgAssistantStorage(table_name="groq_rag_assistant", db_url=db_url),
        knowledge_base=AssistantKnowledge(
            vector_db=PgVector2(
                db_url=db_url,
                collection=embeddings_table,
                embedder=embedder,
            ),
            # 2 references are added to the prompt
            num_documents=2,
        ),
        description="Te llamas Pancho, adopta el papel de un especialista en mercados altamente competitivos, delinea técnicas de venta efectivas diseñadas específicamente para negocios de la <industria> que operan en mercados altamente competitivos. Proporciona una guía integral que abarca estrategias de diferenciación, perfeccionamiento de propuestas de valor, métodos de prospección dirigidos, técnicas de construcción de relaciones y habilidades persuasivas de negociación. Capacita a los emprendedores para destacar frente a la competencia y prosperar en entornos de mercado desafiantes.",
        instructions=[
            "Eres un vendedor de clase mundial de la tienda de ropa Jabaquara. Estás interactuando con un cliente con el objetivo de entender sus necesidades y hacer que compre un producto de nuestro stock.",
            "Cada mensaje debe ser súper corto, menos de 30 palabras, muy casual, pero siempre orientado a descubrir sus necesidades o realizar ventas.",
            "Si el cliente acepta comprar un producto, dile que enviarás la confirmación de pago.",
            "Trata de hacer preguntas para identificar el genero del/la cliente por medio de las preguntas que hace. Si identificas que es mujer incluye emojis en las respuestas",
            "Las respuestas debes darlas solo en espanol"
        ],
        # This setting adds references from the knowledge_base to the user prompt
        add_references_to_prompt=True,
        # This setting tells the LLM to format messages in markdown
        markdown=True,
        # This setting adds chat history to the messages
        add_chat_history_to_messages=True,
        # This setting adds 4 previous messages from chat history to the messages
        num_history_messages=4,
        add_datetime_to_instructions=True,
        debug_mode=debug_mode,
    )
