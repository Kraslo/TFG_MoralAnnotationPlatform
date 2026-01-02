'''
Functions and code for runnning moral annotation pipeline.
'''

import requests
import re
import unicodedata
from uuid6 import uuid6
from passwords import FUSEKI_PASSWORD,FUSEKI_USER
from sparql import SPARQL_PREFIXES, AMOR_ENDPOINT, send_query
from pprint import pprint

TRANSLATION_API_URL = "http://127.0.0.1:5000/translate"
MORAL_API_URL = "https://moral-values-api.gsi.upm.es/predict"

MORAL_MAPPINGS = {
    "HARM": ("CARE", "Vice"),
    "CHEATING": ("FAIRNESS", "Vice"),
    "BETRAYAL": ("LOYALTY", "Vice"),
    "DEGRADATION": ("PURITY", "Vice"),
    "SUBVERSION": ("AUTHORITY", "Vice"),
    "CARE": ("HARM", "Virtue"),
    "FAIRNESS": ("CHEATING", "Virtue"),
    "LOYALTY": ("BETRAYAL", "Virtue"),
    "PURITY": ("DEGRADATION", "Virtue"),
    "AUTHORITY": ("SUBVERSION", "Virtue"),
    "NO-MORAL": ("NO-MORAL", "Neutral"),
}



MORAL_WITH_PREFIXES = {
    "CARE": "mft:Care" ,
    "FAIRNESS": "mft:Fairness" ,
    "LOYALTY": "mft:Loyalty" ,
    "AUTHORITY": "mft:Authority" ,
    "PURITY": "mft:Purity" ,
    "EQUALITY": "mft:Equality" ,
    "PROPORTIONALITY": "mft:Proportionality" ,
    "LIBERTY": "mft:Liberty" ,
    "HONOR": "mft:Honor" ,
    "OWNERSHIP": "mft:Ownership" ,
    "NO-MORAL": "amor:NonMoral , amor:Neutral"
}



OPPOSITE_MORALS = {key: value[0] for key, value in MORAL_MAPPINGS.items()}
POLARITIES = {key: value[1] for key, value in MORAL_MAPPINGS.items()}

def translate_text(text, source_lang="es", target_lang="en"):
    params = {
        'q': text,
        'source': source_lang,
        'target': target_lang,
        'format': "text",
        'api_key': ""
    }
    response = requests.post(url=TRANSLATION_API_URL, data=params)

    if response.status_code == 200:
        return response.json().get("translatedText", text)
    else:
        print("Translation error:", response.text)
        return text  # Return original text if translation fails


def to_title_case(name):
    """Converts an uppercase moral annotation to Title Case"""
    try:
        normalized_name = unicodedata.normalize('NFD', name)
    except Exception as e:
        print(name)
        raise e
    ascii_name = ''.join(c for c in normalized_name if unicodedata.category(c) != 'Mn')
    
    return re.sub(r'[^a-zA-Z0-9]', '', ascii_name.capitalize())



def analyze_moral_values(text):
    request_payload = {
        "text": text,
        "model_name": "multimoralpolarity_model"}
    
    try:
        response = requests.post(MORAL_API_URL, json=request_payload)
        response.raise_for_status()
        prediction = response.json()
        probabilities = prediction.get("Probabilities", {})
        if not probabilities:
            return "No moral values detected.",  0.0, "unknown", 0.0
        
        highest_moral = max(probabilities, key=probabilities.get)
        highest_confidence = probabilities[highest_moral]

        
        opposite_moral = OPPOSITE_MORALS.get(highest_moral, None)
        opposite_confidence = probabilities.get(opposite_moral, 0.0)
        p_intensity = highest_confidence - opposite_confidence

        polarity = POLARITIES.get(highest_moral, "unknown")
                        
        if polarity == "Vice":
            highest_moral= MORAL_MAPPINGS.get(highest_moral, [highest_moral])[0]
            p_intensity = -p_intensity

        return highest_moral, highest_confidence, polarity, p_intensity

            
    except requests.exceptions.RequestException as e:
        print("Error analyzing moral values:", e)
        return "Error", 0.0
    


def get_news_without_moral_annotation():
    
    # sparql query to select news' bodies and titles that do not have moral annotation yet   
    query = f"""
    {SPARQL_PREFIXES}

    SELECT * WHERE {{
        ?sub a schema:NewsArticle ;
            schema:headline ?headline ;
            schema:articleBody ?body .
        FILTER NOT EXISTS {{
            ?annotation a amor:MoralValueAnnotation ;
                oa:hasTarget ?sub .
        }}
    }}
    """

    results = send_query(query)

    return results["results"]["bindings"]

def add_moral_to_fuseki(moral_value, confidence , polarity, p_intensity, news_uri_last_part, moral_annotation_uri):
    
    # SPARQL update
    optional_polarity_triples = ""

    if moral_value != "NO-MORAL":
        optional_polarity_triples = f"""
            amor-mft:hasPolarity mft:{polarity} ;
            amor-mft:hasPolarityIntensity "{p_intensity}"^^xsd:float ;
        """
    
    moral_value_with_prefix = MORAL_WITH_PREFIXES.get(moral_value, None)
    
    sparql_update_query = f"""
        {SPARQL_PREFIXES}

        INSERT DATA {{
                {moral_annotation_uri} a amor:MoralValueAnnotation ;
                    amor:hasMoralValueCategory {moral_value_with_prefix} ;
                    itsrdf:taConfidence "{confidence}"^^xsd:float ;
                    {optional_polarity_triples}
                    oa:hasTarget amor-datasets:{news_uri_last_part} .
            }}
        """

    sparql_update_endpoint = f"{AMOR_ENDPOINT}/update"
    headers = {'Content-Type': 'application/sparql-update'}

    response = requests.post(sparql_update_endpoint, auth=(FUSEKI_USER,FUSEKI_PASSWORD), data=sparql_update_query, headers=headers)
    
    if str(response.status_code).startswith("2"):
        print(f"Moral annotation {moral_value} as {moral_value_with_prefix} added successfully: Status code: {response.status_code}")
    else:
        print(f"Failed to add moral annotation. Status code: {response.status_code}, Response: {response.text}")
    


def moral_annotation_pipeline(result):     
    try:
        # URI, headline and body of the news
        news_uri = result['sub']['value']
        headline_es = result['headline']['value']
        body_es = result['body']['value']
        text_es = headline_es + "\n\n" + body_es

        # Translate text
        translated_text = translate_text(text_es, source_lang="es", target_lang="en")
        
        # Analyze the moral values 
        moral_value, confidence , polarity, p_intensity = analyze_moral_values(translated_text)

        print("\n")
        print(f"News URI: {news_uri}")
        print(f"Headline: {headline_es}")
        print(f"Moral Value: {moral_value}")
        print(f"Moral Value: {moral_value}")
        print(f"Confidence: {confidence}")
        print(f"Polarity: {polarity}")
        print(f"Polarity intensity: {p_intensity}")
        news_uri_last_part = news_uri.split("#")[-1]
        print(news_uri_last_part)

        moral_annotation_uri = f"amor-datasets:moral{uuid6()}"
        add_moral_to_fuseki(moral_value, confidence , polarity, p_intensity,news_uri_last_part, moral_annotation_uri)
        
        return moral_annotation_uri
    
    except Exception as e:
        print("Error processing news:", e)
        exit()


if __name__ == "__main__":
    news_items = get_news_without_moral_annotation()
    pprint(f"- News articles without moral annotation [{len(news_items)}]")

    for item in news_items:
        moral_annotation_pipeline(item)