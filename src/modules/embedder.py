import os
import pickle
import tempfile
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import JSONLoader
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class Embedder:

    def __init__(self):
        self.PATH = "embeddings"
        self.createEmbeddingsDir()

    def createEmbeddingsDir(self):
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)

    def getFileExtension(self, uploadedFile):
        fileExtension = os.path.splitext(uploadedFile)[1].lower()
        return fileExtension

    def storeDocEmbeddings(self, file, originalFileName):
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmpFile:
            tmpFile.write(file)
            tmpFilePath = tmpFile.name

        fileExtension = self.getFileExtension(originalFileName)

        textSplitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=100,
            length_function=len
        )

        if fileExtension == ".json":
            loader = JSONLoader(file_path=tmpFilePath)
            data = loader.load()
        
        if fileExtension == ".csv":
            loader = CSVLoader(file_path=tmpFilePath, encoding="utf-8", csv_args={'delimiter': ','})
            data = loader.load()
        
        if fileExtension == ".pdf":
            loader = PyPDFLoader(file_path=tmpFilePath)
            data = loader.load_and_split(text_splitter=textSplitter)
        
        if fileExtension == ".txt":
            loader = TextLoader(file_path=tmpFilePath, encoding="utf-8")
            data = loader.load_and_split(text_splitter=textSplitter)

        embeddings = OpenAIEmbeddings()

        vectors = FAISS.from_documents(data, embeddings)
        os.remove(tmpFilePath)

        with open(f"{self.PATH}/{originalFileName}.pkl", "wb") as file:
            pickle.dump(vectors, file)

    def getDocEmbeddings(self, file, originalFileName):
        if not os.path.isfile(f"{self.PATH}/{originalFileName}.pkl"):
            self.storeDocEmbeddings(file, originalFileName)
        
        with open(f"{self.PATH}/{originalFileName}.pkl", "rb") as file:
            vectors = pickle.load(file)

        return vectors
            




        