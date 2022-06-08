import json
from tokenize import group
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from textblob import TextBlob
import spacy
import pandas as pd
import plotly.express as px

# Spacy is a NLP library in Python. 
# Load English tokenizer, tagger, parser and NER
nlp = spacy.load('en_core_web_sm')

def preprocess(filename):
    # Opening the JSON file.
    file = open(filename)
    data = json.load(file)

    # Iterate and get the text of each article in the JSON file.
    preprocess_df = pd.DataFrame(columns=["Article Id","Sentences"])
    for article in tqdm(data["articles"]):
        # Get the html body of the articles
        response_ = requests.get(article['article_link'])
        # print(response_.text)
        html_body = response_.text

        # Create a Beautiful soup object from the html body
        bs = BeautifulSoup(html_body,
                           features="html.parser")
        text = bs.get_text(strip=True)
        # print(text)
        # The extracted information only contains text.
        # We can move to pre-process the extracted text information.

        sentences = []
        tokens =  nlp(text)
        for string in tokens.sents:
            sentences.append(string.text.strip())
            if sentences[-1].startswith(("Schedule",
                                         "UsCode",
                                         "FinderTV",
                                         "Source",
                                         "\"Source",
                                         "Al",
                                        )):
                sentences.pop(-1)

        temp = {"Article Id":[article['article_id'] for _ in range(len(sentences))],
                "Sentences": sentences
               }
        temp_df = pd.DataFrame(temp)
        preprocess_df = pd.concat([preprocess_df,temp_df])

    return preprocess_df

def get_sentiment(text):
    result = TextBlob(text)
    return pd.Series([result.sentiment.polarity,result.sentiment.subjectivity])

def compute_sentiment(df):
    # print(df.head())
    df[["Polarity","Subjectivity"]] = df["Sentences"].apply(get_sentiment)
    return df
    
def visualize(df):
    polartiy_df = df.groupby(["Article Id"])["Polarity"].mean()
    subjectivity_df = df.groupby(["Article Id"])["Subjectivity"].mean()
    fig = px.bar(polartiy_df)
    fig.write_image('pic1.jpg')
    # print(subjectivity_df)
    fig1 = px.bar(subjectivity_df)
    fig1.write_image('pic2.jpg')
    # fig = px.histogram(df, x='Article Id',y='Polarity')
    # fig.show()
    return


        

        
        
        

text_df = preprocess('articles.json')
sentiment_df = compute_sentiment(text_df)
visualize(sentiment_df)



