import argparse
from dotenv import dotenv_values
from serpapi import Client, SerpResults
from yaspin import yaspin
from yaspin.spinners import Spinners
import string
import sys
from dataclasses import dataclass, field

# Constant key used to extract AI Overview from SERP results

AI_OVERVIEW = "ai_overview"

class SerpApiClient:
    """Handles connection and querying to SerpAPI"""
    
    def __init__(self):
        config = dotenv_values(".env")
        if 'SERP_API_KEY' not in config:
            print('ERROR: Missing field \'SERP_API_KEY\' in .env')
            sys.exit(1)
        API_KEY = config['SERP_API_KEY']
        if not API_KEY:
            print('ERROR: API Key Not Specified')
            sys.exit(1)
        self.client = Client(api_key=API_KEY)
        
    def search_query(self, query: str, location=None) -> SerpResults:
        """
        Sends a query to SerpAPI with optional location.
        
        Args:
            query: Query to search
            location: Location of search
            
        Returns:
            SerpResults object containing the search response.
        """
        params = {
            "q": query,
            "no_cache": True
        }
        if location:
            params["location"] = location
        
        search_response = self.client.search(params)
        return search_response
    
    def get_ai_overview(self, res: SerpResults) -> dict:
        """
        Extracts the AI Overview block from SerpAPI search results
        
        Args:
            results: SerpResults Object returned by the search query
            
        Returns:
            dict containing the ai_overview
        """
        if AI_OVERVIEW in res:
            if "text_blocks" in res[AI_OVERVIEW]:
                return res[AI_OVERVIEW]["text_blocks"]
            elif "page_token" in res[AI_OVERVIEW]:
                params = {
                    "page_token": res[AI_OVERVIEW]["page_token"],
                    "engine": "google_ai_overview",
                    "no_cache": True
                }
                search_response = self.client.search(params)
                if AI_OVERVIEW in search_response:
                    return search_response[AI_OVERVIEW]
                else:
                    return None
        else:
            return None
    
@dataclass
class MetricGroup:
    """Stores count and list of matched items."""
    count: int = 0
    items: list[str] = field(default_factory=list)

@dataclass
class Metrics:
    """Holds metrics grouped by type of match (headings, references, snippets)."""
    headings: MetricGroup = field(default_factory=MetricGroup)
    references: MetricGroup = field(default_factory=MetricGroup)
    snippets: int = 0

class AIOverviewAnalyzer:
    """Analyzes AI Overview blocks from SerpAPI results"""
    def __init__(self, company: str):
            self.company = company.lower()
            self.metrics = Metrics()

    def _deep_search(self, data) -> None:
        """
        Recursively search AI Overview data for matching content.
        Handles nested dictionaries and lists.
        
        Args:
            d: Data to search recursively
        """
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
        """
        Check each reference for the company name and record matching links.
        
        Args:
            references: List of references
        """
        for ref in references:
            if any(self.company in ref.get(field, "").lower() for field in ["title", "link", "snippet", "source"]):
                self.metrics.references.count += 1
                # Remove anchor from URL
                self.metrics.references.items.append(ref["link"].split('#')[0])
                    
    def _process_snippet(self, snippet: str) -> None:
        """
        Count the snippet if it contains the company name.
        
        Args:
            snippet: Snippet to search for the company
        """
        if self.company in snippet.lower():
            self.metrics.snippets += 1
                
    def _process_title(self, title: str) -> None:
        """
        Count the heading if it contains the company name.
        
        Args:
            title: Heading to search for the company
        """
        if self.company in title.lower():
            self.metrics.headings.count += 1
            self.metrics.headings.items.append(title)

    def check_overview(self, ai_overview: dict) -> None:
        """
        Analyzes AI Overview from the search results for mentions of the company.
        
        Args:
            ai_overview: dict containing the ai_overview
        """ 
        self._deep_search(ai_overview)
        
    def check_occurrence(self) -> bool:
        """
        Checks if company was found in any heading, snippet, or reference.
        
        Returns:
            True/False depending on whether it was found
        """
        return self.metrics.snippets > 0 or self.metrics.headings.count > 0 or self.metrics.references.count > 0
        
    def print_metrics(self):
        """Prints metrics of company mentions in headings and references."""
        print(f'\nHeadings containing {self.company}: {self.metrics.headings.count}')
        for heading in self.metrics.headings.items:
            print(heading.rstrip(string.punctuation))
            
        print(f'\nReferences containing {self.company}: {self.metrics.references.count}')
        for reference in self.metrics.references.items:
            print(reference)

def generate_parser() -> argparse.ArgumentParser:
    """
    Generates the CLI argument parser for the script
    """
    parser = argparse.ArgumentParser(description="Search for query")
    
    parser.add_argument("-q", "--query", required=True, help="Your search query")
    parser.add_argument("-c", "--company", required=True, help="Company name")
    parser.add_argument("-l", "--location", required=False, help="Optional location parameter")
    parser.add_argument("--metrics", action="store_true", help="Check how many times the company showed up in the AI Overview")
    return parser
    
def is_ai_overview_present(res: SerpResults) -> bool:
    """
    Checks if ai_overview and its content is present in the result.
    
    Args:
        res: SerpResults Object returned by the search query
        
    Returns:
        True/False depending if ai_overview is present
    """
    if AI_OVERVIEW in res:
        # and "text_blocks" in res[AI_OVERVIEW]
        if "text_blocks" in res[AI_OVERVIEW]:
            return True
        pass
    else:
        return False
    
def main():
    """Main function"""
    parser = generate_parser()
    args = parser.parse_args()
    found = False
    
    location = args.location or None
    serp = SerpApiClient()
    with yaspin(Spinners.earth, text="Searching the web") as sp:
        try:
            res = serp.search_query(args.query, location)
        except Exception as e:
            sp.fail("💀 ")
            print(f'An error has occured while searching: {e}')
            sys.exit(1)
        
        ai_overview = serp.get_ai_overview(res)
        if ai_overview:
            sp.ok("✅ ")
            found = True
        else:
            sp.fail("💀 ")
           
    if found:
        company = args.company
        analyzer = AIOverviewAnalyzer(company)
        try:
            analyzer.check_overview(ai_overview)
        except Exception as e:
            print(f'An error has occured while searching for the company in the results: {e}')
            sys.exit(1)
        
        if analyzer.check_occurrence():
            print('Found')
            if args.metrics:
                analyzer.print_metrics()
        else:
            print('Not Found')
    else:
        print('AI Overview Not Found')

if __name__ == "__main__":
    main()
