from sentence_transformers import SentenceTransformer

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import numpy as np

# class Conversation(Base):
#     __tablename__ = "conversations"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     prompt = Column(String, nullable=False)
#     prompt_embedding = Column(Vector(384), nullable=False)
#     response = Column(String, nullable=False)
#     response_embedding = Column(Vector(384), nullable=False)
#     timestamp = Column(DateTime, server_default=func.now())
#
# class Memory(Base):
#     __tablename__ = "memory"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     memory = Column(String, nullable=False)
#     memory_embedding = Column(Vector(384), nullable=False)
#     timestamp = Column(DateTime, server_default=func.now())

class Rag():
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        # self.db = db_name
        # DATABASE_URL = f"postgresql://{user}@10.0.0.7:5432/{self.db}"
        # self.engine = create_engine(DATABASE_URL)
        # Session = sessionmaker(bind=self.engine)
        self.connection = connections.connect(host="10.0.0.7", port="19530")
        self.create_necessary_collections()


    def create_necessary_collections(self, replace=False):
        if utility.has_collection("conversations") and utility.has_collection("memory"):
            if replace:
                utility.drop_collection("conversations")
                utility.drop_collection("memory")
            else:
                print(f"Collection 'conversations' and 'memory' already exists. Skipping creation.")
                return
        conversations_fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="prompt_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
            FieldSchema(name="prompt", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="response_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
            FieldSchema(name="response", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="timestamp", dtype=DataType.INT64)
        ]
        conversations_collection = self.create_collection("conversations", conversations_fields)
        index_params_prompt_embedding = {
            "metric_type": "L2",
            "index_type": "GPU_IVF_FLAT",
            "params": {"nlist": 100},
        }
        conversations_collection.create_index(field_name="prompt_embedding", index_params=index_params_prompt_embedding)

        index_params_response_embedding = {
            "metric_type": "L2",
            "index_type": "GPU_IVF_FLAT",
            "params": {"nlist": 100},
        }
        conversations_collection.create_index(field_name="response_embedding", index_params=index_params_response_embedding)

        memory_fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="memory_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
            FieldSchema(name="memory", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="timestamp", dtype=DataType.INT64)
        ]
        memory_collection = self.create_collection("memory", memory_fields)

        index_params_memory_embedding = {
            "metric_type": "L2",
            "index_type": "GPU_IVF_FLAT",
            "params": {"nlist": 100},
        }

        memory_collection.create_index(field_name="memory_embedding", index_params=index_params_memory_embedding)



    def create_collection(self, collection_name, fields=None):

        # TODO: Add a description
        schema = CollectionSchema(fields=fields, description="Enter description here")
        collection = Collection(name=collection_name, schema=schema)
        return collection

    def write_conversation(self, prompt, response, collection_name="conversations"):
        collection = Collection(collection_name)
        prompt_embedding = self.model.encode(prompt)
        response_embedding = self.model.encode(response)
        print("written conversat")

        collection.insert({
            "prompt_embedding": prompt_embedding,
            "prompt": prompt,
            "response_embedding": response_embedding,
            "response": response,
            "timestamp": int(np.datetime64("now").astype(int))
        })
        






    def write_memory(self, memory, collection_name="memory"):
        collection = Collection(collection_name)
        memory_embedding = self.model.encode(memory)
        collection.insert({
            "memory_embedding": memory_embedding,
            "memory": memory,
            "timestamp" : int(np.datetime64("now").astype(int))
        })

    # TODO: Combine prompt and response into one query
    def search_conversation_by_prompt(self, query):
        collection = Collection("conversations")
        collection.load()
        query_embedding = self.model.encode(query)

        results = collection.search(
            data=[query_embedding],
            anns_field="prompt_embedding",
            param={"metric_type": "L2", "params": {"nprobe": 100}},
            limit=10,
            output_fields=["prompt", "response"],
        )

        # print(f"Results: {results}")
        #
        #
        # print(f"Results: {results[0]}")
        # print(f"Why: {len(results[0])}")
        #
        results = results[0]
        for hit in results:
            hit_id = hit.id
            score = hit.score
            prompt = hit.entity.get("prompt")
            response = hit.entity.get("response")


        RECALL_THRESHOLD = 0.5
        results = [{'prompt': hit.entity.get('prompt'), 'response': hit.entity.get('response')} for hit in results if hit.score < RECALL_THRESHOLD]

        return results

        # return results

    def get_recent_conversations(self):
        collection = Collection("conversations")
        collection.load()
        NUM_RECENT_RESPONSES = 3
        results = collection.query(
            expr="",
            output_fields=["prompt", "response", "timestamp"],
            limit=1000,
            order_by=[("timestamp", "asc")]
)
        sorted_results = sorted(results, key=lambda x: x["timestamp"], reverse=True)[:3]
        return sorted_results

    def get_memory(self):
        collection = Collection("memory")
        collection.load()
        NUM_RECENT_MEMORY = 10

        results = collection.query(
            expr="",
            output_fields=["memory"],
            limit=NUM_RECENT_MEMORY,
            order_by=[("timestamp", "desc")]
        )

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
