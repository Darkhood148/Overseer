import argparse
from dotenv import dotenv_values
from serpapi import Client, SerpResults
from yaspin import yaspin
from yaspin.spinners import Spinners
import string
import sys
from dataclasses import dataclass, field

AI_OVERVIEW = "ai_overview"

class SerpApiClient:
    def __init__(self):
        config = dotenv_values(".env")
        if not 'SERP_API_KEY' in config:
            print('ERROR: Missing field \'SERP_API_KEY\' in .env')
            sys.exit(1)
        API_KEY = config['SERP_API_KEY']
        if not API_KEY:
            print('ERROR: API Key Not Specified')
            sys.exit(1)
        self.client = Client(api_key=API_KEY)
        
    def search_query(self, query: str, location=None) -> SerpResults:
        params = {
            "q": query,
        }
        if location:
            params["location"] = location
        
        search_response = self.client.search(params)
        return search_response
    
@dataclass
class MetricGroup:
    count: int = 0
    items: list[str] = field(default_factory=list)

@dataclass
class Metrics:
    headings: MetricGroup = field(default_factory=MetricGroup)
    references: MetricGroup = field(default_factory=MetricGroup)
    snippets: int = 0

class AIOverviewAnalyzer:
    def __init__(self, company: str):
            self.company = company.lower()
            self.metrics = Metrics()

    def _deep_search(self, data) -> None:
        if isinstance(data, dict):
            for k, v in data.items():
                if k == 'references':
                    self._process_references(v)
                elif k == 'snippet' and isinstance(v, str):
                    self._process_snippet(v)
                elif k == 'title' and isinstance(v, str):
                    self._process_title(v)
                elif isinstance(v, dict) or isinstance(v, list):
                    self._deep_search(v)
        elif isinstance(data, list):
            for item in data:
                self._deep_search(item)
                
    def _process_references(self, references: list) -> None:
            for ref in references:
                if any(self.company in ref.get(field, "").lower() for field in ["title", "link", "snippet", "source"]):
                    self.metrics.references.count += 1
                    # Remove anchor from URL
                    self.metrics.references.items.append(ref["link"].split('#')[0])
                    
    def _process_snippet(self, snippet: str) -> None:
            if self.company in snippet.lower():
                self.metrics.snippets += 1
                
    def _process_title(self, title: str) -> None:
        if self.company in title.lower():
            self.metrics.headings.count += 1
            self.metrics.headings.items.append(title)
                    

    @staticmethod
    def _get_ai_overview(results: SerpResults) -> dict:
        res_dict = results.as_dict()
        ai_overview = res_dict[AI_OVERVIEW]
        return ai_overview

    def check_overview(self, results: SerpResults) -> None:
        ai_overview = self._get_ai_overview(results)  
        self._deep_search(ai_overview)
        
    def print_metrics(self):
        print(f'\nHeadings containing {self.company}: {self.metrics.headings.count}')
        for heading in self.metrics.headings.items:
            print(heading.rstrip(string.punctuation))
            
        print(f'\nReferences containing {self.company}: {self.metrics.references.count}')
        for reference in self.metrics.references.items:
            print(reference)

def generate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search for query")
    
    parser.add_argument("-q", "--query", required=True, help="Your search query")
    parser.add_argument("-c", "--company", required=True, help="Company name")
    parser.add_argument("-l", "--location", required=False, help="Optional location parameter")
    parser.add_argument("--metrics", action="store_true", help="Check how many times the company showed up in the AI Overview")
    return parser
    
def is_ai_overview_present(res: SerpResults) -> bool:
    return AI_OVERVIEW in res and "text_blocks" in res[AI_OVERVIEW]

def check_occurrence(analyzer: AIOverviewAnalyzer) -> bool:
    return analyzer.metrics.snippets > 0 or analyzer.metrics.headings.count > 0 or analyzer.metrics.references.count > 0
    
def main():
    parser = generate_parser()
    args = parser.parse_args()
    found = False
    
    with yaspin(Spinners.earth, text="Searching the web") as sp:
        try:
            location = args.location or None
            serp = SerpApiClient()
            res = serp.search_query(args.query, location)
        except Exception as e:
            sp.fail("💀 ")
            print(f'An error has occured while searching: {e}')
            sys.exit(1)
        
        if is_ai_overview_present(res):
            sp.ok("✅ ")
            found = True
        else:
            sp.fail("💀 ")
           
    if found:
        company = args.company
        analyzer = AIOverviewAnalyzer(company)
        try:
            analyzer.check_overview(res)
        except Exception as e:
            print(f'An error has occured while searching for the company in the results: {e}')
            sys.exit(1)
        
        if check_occurrence(analyzer):
            print('Found')
            if args.metrics:
                analyzer.print_metrics()
        else:
            print('Not Found')
    else:
        print('AI Overview Not Found')
    

if __name__ == "__main__":
    main()
