from supabase import create_client
from dotenv import load_dotenv
import os
import time
from tabulate import tabulate
import spacy
import nltk
from nltk.corpus import wordnet

#create a supabase client
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)
def new_supabase():
    return create_client(url, key)

#Initiate the spacy model
nlp = spacy.load("en_core_web_md")

#Function to get synonyms for keywords
def get_synonyms(keywords):
    synonyms = set()
    for keyword in keywords:
        for syn in wordnet.synsets(keyword):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
    
    return synonyms
    

#Take headlines without keywords
def get_headlines_without_keywords():
    # while True:
        responses = supabase.rpc("get_headlines_without_keywords").execute()
        for response in responses.data:
            headline = response["headline"]
            short_description = response["short_description"]
            doc = nlp(headline)
            keywords = []
            
            #Extract keywords from the headline + lemmanize the keywords
            keywords_proper_nouns = [token.text.lower() for token in doc if token.pos_ == "PROPN"]
            keywords = [token.lemma_.lower() for token in doc if token.pos_ != "PROPN" and not token.is_stop and not token.is_punct]
            
            #In case no keywords are found in the headline, use the short description
            if (not keywords_proper_nouns) and (not keywords):
                doc = nlp(short_description)
                keywords_proper_nouns = [token.text.lower() for token in doc if token.pos_ == "PROPN"]
                keywords = [token.lemma_.lower() for token in doc if token.pos_ != "PROPN" and not token.is_stop and not token.is_punct]

            # print("Keywords: ", keywords)
            #Upsert proper nouns keywords to the database
            if (keywords_proper_nouns):
                supabase.table("WebScrapData").upsert({"id": response["id"], "keywords_proper_nouns": keywords_proper_nouns}).execute()
            
            #Find synonyms for the keywords and upsert them to the database
            keywords_and_synonyms = get_synonyms(keywords)
            # print("Keywords and synonyms: ", keywords_and_synonyms)
            supabase.table("WebScrapData").upsert({"id": response["id"], "keywords": list(keywords_and_synonyms)}).execute()
             
if __name__ == "__main__":
    get_headlines_without_keywords()