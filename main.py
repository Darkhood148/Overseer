import argparse
from dotenv import load_dotenv
import os
from serpapi import search
from yaspin import yaspin
from yaspin.spinners import Spinners

load_dotenv()
API_KEY = os.getenv('SERP_API_KEY')

def search_query(query: str):
    print(API_KEY)
    params = {
        "q": query,
        "api_key": API_KEY,
        "location": "United States"
    }
    searchResponse = search(params)
    return searchResponse

def generate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search for query")
    parser.add_argument("query", help="Your search query")
    return parser
    

def main():
    parser = generate_parser()
    args = parser.parse_args()

    res = search_query(args.query)
    print(res)
    

if __name__ == "__main__":
    main()
