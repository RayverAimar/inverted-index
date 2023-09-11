import os
import json
import nltk
import time
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from utils import create_folder, DOCS_PATH, DB_PATH

class InvertedIndex:
    def __init__(self) -> None:
        self.token_to_tokenID = {}
        self.tokenID_to_index = {}
        self.tokenID_to_token = {}
        self.docName_to_docID = {}
        self.docID_to_name = {}
        self.punctuation_characters = ['.', ',', ':', ';', '!', '?', '"', '-', '(', ')', '[', ']', '{', '}', '<', '>', '*']
        self.stop_words = set(stopwords.words('english'))
        self.importDatabase()
        self.loadDocuments()
    
    def save(self):
        print("[InvertedIndex] Saving database...")
        create_folder(DB_PATH)
        json_names = ["token_to_token_ID.json",
                      "tokenID_to_index.json",
                      "tokenID_to_token.json",
                      "docID_to_name.json",
                      "docName_to_docID.json"
                      ]
        json_names = ["/".join((DB_PATH, json_name)) for json_name in json_names]
        
        with open(json_names[0], "w") as json_file:
            json.dump(self.token_to_tokenID, json_file)
        
        with open(json_names[1], "w") as json_file:
            json.dump(self.tokenID_to_index, json_file)

        with open(json_names[2], "w") as json_file:
            json.dump(self.tokenID_to_token, json_file)

        with open(json_names[3], "w") as json_file:
            json.dump(self.docID_to_name, json_file)
        
        with open(json_names[4], "w") as json_file:
            json.dump(self.docName_to_docID, json_file)
        
        print("[InvertedIndex] Database successfully saved!\n")
    
    def importDatabase(self):
        print("[InvertedIndex] Importing previous database...")
        if not os.path.exists(DB_PATH):
            print("[InvertedIndex] No database found.")
            return
        print("[InvertedIndex] Database found!")
        json_names = ["token_to_token_ID.json",
                      "tokenID_to_index.json",
                      "tokenID_to_token.json",
                      "docID_to_name.json",
                      "docName_to_docID.json"
                      ]
        json_names = ["/".join((DB_PATH, json_name)) for json_name in json_names]

        with open(json_names[0], "r") as json_file:
            self.token_to_tokenID = json.load(json_file)

        with open(json_names[1], "r") as json_file:
            self.tokenID_to_index = json.load(json_file)

        with open(json_names[2], "r") as json_file:
            self.tokenID_to_token = json.load(json_file)

        with open(json_names[3], "r") as json_file:
            self.docID_to_name = json.load(json_file)
        
        with open(json_names[4], "r") as json_file:
            self.docName_to_docID = json.load(json_file)
        
        print("[InvertedIndex] Database successfully loaded!\n")
    
    def getDocsNames(self):
        folder_path = DOCS_PATH
        filenames = []
        if not os.path.exists(folder_path):
            print(f"Folder '{folder_path}' does not exist yet.")
            return filenames
        for item in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, item)):
                filenames.append("/".join((folder_path, item)))
        return filenames
    
    def getDocContent(self, doc_name):
        doc_content = {}
        with open(doc_name, 'r') as doc_file:
            doc_content = json.load(doc_file)
        return doc_content['content']

    def loadDocuments(self):
        start = time.time()
        docs_names = self.getDocsNames()
        if not docs_names:
            print("[InvertedIndex] No documents found!\n")
            return
        for doc_name in docs_names:
            if self.docName_to_docID.get(doc_name, -1) != -1:
                continue
            docID = len(self.docName_to_docID)
            self.docName_to_docID[str(doc_name)] = docID
            self.docID_to_name[str(docID)] = doc_name
            doc = self.getDocContent(doc_name)
            self.processDoc(doc, docID)
            print(f"[InvertedIndex] Document '{doc_name}' processed!")
        end = time.time()
        print(f"Elapsed time to process documents: {end - start} seconds!")

    def tokenize(self, doc, stemming=False):
        words = word_tokenize(doc)
        stemmer = PorterStemmer()
        tokens = []
        for word in words:
            if word.lower() in self.punctuation_characters:
                continue
            if word.lower() not in self.stop_words:
                tokens.append(stemmer.stem(word) if stemming else word)
        return tokens

    def countWords(self, tokenIDs):
        word_counts = {}
        for tokenID in tokenIDs:
            if word_counts.get(tokenID, -1) != -1:
                word_counts[tokenID]+=1
            else:
                word_counts[tokenID]=1
        return word_counts

    def convertTokensToIDs(self, tokens):
        tokenIDs = []
        for token in tokens:
            if self.token_to_tokenID.get(token, -1) != -1:
                tokenIDs.append(self.token_to_tokenID[token])
            else:
                id = len(self.token_to_tokenID)
                self.token_to_tokenID[token]=id
                self.tokenID_to_token[str(id)]=token
                tokenIDs.append(str(id))
        return tokenIDs
    
    def addToPostings(self, word_count, docID):
        for term_id in word_count.keys():
            count = word_count[term_id]
            if self.tokenID_to_index.get(str(term_id), -1) == -1:
                self.tokenID_to_index[str(term_id)] = []
            self.tokenID_to_index[str(term_id)].append(docID)
            self.tokenID_to_index[str(term_id)].append(count)
    
    def processDoc(self, doc, docID):
        tokens = self.tokenize(doc, stemming=True)
        tokenIDs = self.convertTokensToIDs(tokens)
        word_count = self.countWords(tokenIDs)
        self.addToPostings(word_count, docID)
    
    def query(self, words):
        tokens = self.tokenize(words, stemming=True)
        not_stemmed_tokens = self.tokenize(words, stemming=False)
        results = 0
        start = time.time()
        for i, token in enumerate(tokens):
            print(f'Current word: {not_stemmed_tokens[i]}')
            if self.token_to_tokenID.get(token, -1) == -1:
                print(f'\tWord not found in the database')
                continue
            ocurrences = self.tokenID_to_index[str(self.token_to_tokenID[token])]
            for idx in range(0, len(ocurrences), 2):
                results+=1
                print(f'\tDocument {self.docID_to_name[str(ocurrences[idx])]} got this word {ocurrences[idx+1]} times.')
        end = time.time()
        print(f"\nAbout {results} results ({end-start})")
            
    def run(self):
        while True:
            print("*** Inverted Index Menu ***")
            print("1. Query")
            print("2. Refresh database")
            print("3. Quit")
            option = int(input("Type your choice: "))
            if option == 1:
                os.system('cls' if os.name == 'nt' else 'clear')
                query_words = input("Enter your query: ")
                self.query(query_words)
            elif option == 2:
                self.loadDocuments()
            elif option == 3:
                os.system('cls' if os.name == 'nt' else 'clear')
                self.save()
                print('[InvertedIndex] Exiting program...')
                break
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
            

invertedIndex = InvertedIndex()
invertedIndex.run()