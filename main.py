import argparse
from dotenv import load_dotenv
import os
from serpapi import Client, SerpResults
from yaspin import yaspin
from yaspin.spinners import Spinners
import string

load_dotenv()
API_KEY = os.getenv('SERP_API_KEY')
if not API_KEY:
    print('Error. API Key Not Specified')
    exit(1)
client = Client(api_key=API_KEY)

heading_counter = 0
reference_counter = 0
snippet_counter = 0
heading_list = []
reference_list = []

def deep_search(d, company: str):
    global heading_counter, reference_counter, snippet_counter, heading_list, reference_list
    if isinstance(d, dict):
        for k, v in d.items():
            if k == 'references':
                for reference in v:
                    if company.lower() in reference["title"].lower() or company.lower() in reference["link"].lower() or company.lower() in reference["snippet"].lower() or company.lower() in reference["source"].lower():
                        reference_counter += 1
                        reference_list.append(reference["link"].split('#')[0])
            elif k == 'snippet' and isinstance(v, str):
                if company.lower() in v.lower():
                    snippet_counter += 1
            elif k == 'title' and isinstance(v, str):
                if company.lower() in v.lower():
                    heading_counter += 1
                    heading_list.append(v)
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
    deep_search(ai_overview, company)
    

def search_query(query: str, location=None):
    params = {
        "q": query,
    }
    if location:
        params["location"] = location
    
    searchResponse = client.search(params)
    return searchResponse

def generate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search for query")
    
    parser.add_argument("-q", "--query", required=True, help="Your search query")
    parser.add_argument("-c", "--company", required=True, help="Company name")
    parser.add_argument("-l", "--location", required=False, help="Optional location parameter")
    parser.add_argument("--metrics", action="store_true", help="Check how many times the company showed up in the AI Overview")
    return parser
    
def check_ai_overview(res: SerpResults) -> bool:
    return "ai_overview" in res and "text_blocks" in res["ai_overview"]
    
def main():
    parser = generate_parser()
    args = parser.parse_args()
    found = False
    
    with yaspin(Spinners.earth, text="Searching the web") as sp:
        try:
            location = args.location or None
            res = search_query(args.query, location)
        except Exception as e:
            sp.fail("💀 ")
            print(f'An error has occured: {e}')
            exit(1)
        
        if check_ai_overview(res):
            sp.ok("✅ ")
            found = True
        else:
            sp.fail("💀 ")
           
    if found:
        company = args.company
        
        try:
            find_company_in_ai_overview(res, company)
        except Exception as e:
            print(f'An error has occured while searching for the company in the results: {e}')
            exit(1)
        
        if snippet_counter > 0 or heading_counter > 0 or reference_counter > 0:
            print('Found')
            if args.metrics:
                print()
                print(f'Headings containing {company}: {heading_counter}')
                for heading in heading_list:
                    print(heading.rstrip(string.punctuation))
                print()
                print(f'References containing {company}: {reference_counter}')
                for reference in reference_list:
                    print(reference)
        else:
            print('Not Found')
    else:
        print('AI Overview Not Found')
    

if __name__ == "__main__":
    main()
