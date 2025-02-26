from sqlalchemy import create_engine, Column, Integer, String, select, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(String, nullable=False)
    prompt_embedding = Column(Vector(384), nullable=False)
    response = Column(String, nullable=False)
    response_embedding = Column(Vector(384), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

class Memory(Base):
    __tablename__ = "memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    memory = Column(String, nullable=False)
    memory_embedding = Column(Vector(384), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

class Rag():
    def __init__(self, db_name):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.db = db_name
        DATABASE_URL = f"postgresql://postgres@10.0.0.7:5432/{self.db}"
        self.engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.create_table()


    def create_table(self):
        Base.metadata.create_all(self.engine)

    def write_conversation(self, prompt, response):
        prompt_embedding = self.model.encode(prompt)
        response_embedding = self.model.encode(response)

        memory_entry = Conversation(prompt=prompt,
                                    prompt_embedding=prompt_embedding,
                                    response=response,
                                    response_embedding=response_embedding
                                 )
        self.session.add(memory_entry)
        self.session.commit()

    def write_memory(self, memory):
        memory_embedding = self.model.encode(memory)
        memory_entry = Memory(memory=memory, memory_embedding=memory_embedding)
        self.session.add(memory_entry)
        self.session.commit()

    # TODO: Combine prompt and response into one query
    def search_conversation_by_prompt(self, query):
        query_embedding = self.model.encode(query)
        query_vector = query_embedding.tolist()

        stmt = select(
                Conversation, 
                Conversation.prompt_embedding.l2_distance(query_vector).label("distance")
            ).order_by(Conversation.prompt_embedding.l2_distance(query_vector)).limit(10)

        results = self.session.execute(stmt).all()

        RECALL_THRESHOLD = 0.5
        results = [embedding[0] for embedding in results if embedding.distance < RECALL_THRESHOLD]

        return results

    def get_recent_conversations(self):
        NUM_RECENT_RESPONSES = 3
        stmt = select(Conversation).order_by(Conversation.timestamp.desc()).limit(NUM_RECENT_RESPONSES)
        results = self.session.execute(stmt).scalars().all()

        return results

    def get_memory(self):
        NUM_RECENT_MEMORY = 10
        stmt = select(Memory).order_by(Memory.timestamp.desc()).limit(NUM_RECENT_MEMORY)
        results = self.session.execute(stmt).scalars().all()

        return results




    # def search_response_embedding(self, query):
    #     query_embedding = self.model.encode(query)
    #     query_vector = query_embedding.tolist()
    #
    #     stmt = select(Embedding).order_by(Embedding.response_embedding.l2_distance(query_vector)).limit(2)
    #     results = self.session.execute(stmt).scalars().all()
    #
    #     for res in results:
    #         print(res.prompt, res.response)

    # def test_search(self, text):
    #     embedding = self.model.encode(text)
    #
    #     query_vector = embedding.tolist()
    #     stmt = select(Embedding).order_by(Embedding.vector.l2_distance(query_vector)).limit(5)
    #     results = self.session.execute(stmt).scalars().all()
    #
    #     for res in results:
    #         print(res.id, res.name)
