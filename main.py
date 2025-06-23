import argparse
from dotenv import load_dotenv
import os
from serpapi import Client, SerpResults
from yaspin import yaspin
from yaspin.spinners import Spinners
import time

# TODO: Add logging

load_dotenv()
API_KEY = os.getenv('SERP_API_KEY')
client = Client(api_key=API_KEY)

def deep_search(d: dict, company: str):
    if isinstance(d, dict):
        for k, v in d.items():
            if k == 'references':
                # TODO: Search references??
                pass
            elif k == 'snippet':
                if company in v:
                    # TODO: add analytics
                    pass
            elif k == 'heading':
                if company in v:
                    # TODO: add analytics
                    pass
            elif isinstance(v, dict) or isinstance(v, list):
                deep_search(v, company=company)
    elif isinstance(d, list):
        for item in d:
            deep_search(item, company=company)

def get_ai_overview(results: SerpResults):
    resDict = results.as_dict()
    ai_overview = resDict["ai_overview"]
    return ai_overview

def find_company_in_ai_overview(results: SerpResults, company: str):
    ai_overview = get_ai_overview(results)
    deep_search(ai_overview, 'lmao')
    

def search_query(query: str):
    params = {
        "q": query,
        "location": "United States"
    }
    searchResponse = client.search(params)
    return searchResponse

def generate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search for query")
    
    # TODO: Add location parameter
    parser.add_argument("-q", "--query", required=True, help="Your search query")
    parser.add_argument("-c", "--company", required=True, help="Company name")
    return parser
    

def main():
    if not API_KEY:
        print('Error. API Key Not Specified')
        exit(1)
        
    parser = generate_parser()
    args = parser.parse_args()
    
    with yaspin(Spinners.earth, text="Searching the web") as sp:
        res = search_query(args.query)
        
        # TODO: Check for error and non present ai_overview
        if res:
            sp.ok("✅ ")
        else:
            sp.fail("💀 ")
           
    company = args.company
    find_company_in_ai_overview(res, company)
    

if __name__ == "__main__":
    main()
