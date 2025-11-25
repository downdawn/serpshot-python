"""Synchronous usage examples for SerpShot SDK."""

from serpshot import LocationType, SerpShot, SerpShotError
from serpshot.models import SearchResponse

# Replace with your actual API key
API_KEY = "your-api-key-here"


def basic_search_example():
    """Basic search example."""
    print("=== Basic Search Example ===\n")
    
    with SerpShot(api_key=API_KEY) as client:
        # Perform a simple search
        response = client.search("Python programming tutorials")
        
        print(f"Query: {response.query}")
        print(f"Total results: {response.total_results}")
        print(f"Credits used: {response.credits_used}")
        print(f"\nResults ({len(response.results)}):\n")
        
        for i, result in enumerate(response.results, 1):
            print(f"{i}. {result.title}")
            print(f"   {result.link}")
            if result.snippet:
                print(f"   {result.snippet[:100]}...")
            print()


def advanced_search_example():
    """Advanced search with parameters."""
    print("=== Advanced Search Example ===\n")
    
    with SerpShot(api_key=API_KEY) as client:
        # Search with additional parameters
        response = client.search(
            "best restaurants",
            num=20,
            gl="us",
            hl="en",
            lr="en",
            location=LocationType.US,
        )
        
        print(f"Found {len(response.results)} results for '{response.query}'")
        print(f"Search time: {response.search_time}s")
        print(f"Total results: {response.total_results}")


def image_search_example():
    """Image search example."""
    print("=== Image Search Example ===\n")
    
    with SerpShot(api_key=API_KEY) as client:
        response = client.image_search(
            "cute puppies",
            num=10,
        )
        
        print(f"Found {len(response.results)} images\n")
        
        for i, img in enumerate(response.results[:5], 1):
            print(f"{i}. {img.title}")
            print(f"   Image URL: {img.link}")
            print(f"   Thumbnail: {img.thumbnail}")
            print(f"   Size: {img.width}x{img.height}")
            print()


def pagination_example():
    """Pagination example."""
    print("=== Pagination Example ===\n")
    
    with SerpShot(api_key=API_KEY) as client:
        query = "artificial intelligence"
        
        # Get first page
        page1 = client.search(query, num=10, page=1)
        print(f"Page 1: {len(page1.results)} results")
        
        # Get second page
        page2 = client.search(query, num=10, page=2)
        print(f"Page 2: {len(page2.results)} results")
        
        # Get third page
        page3 = client.search(query, num=10, page=3)
        print(f"Page 3: {len(page3.results)} results")


def error_handling_example():
    """Error handling example."""
    print("=== Error Handling Example ===\n")
    
    try:
        # Without context manager for explicit error handling
        client = SerpShot(api_key=API_KEY)
        
        try:
            response = client.search("test query")
            print(f"Success! Got {len(response.results)} results")
            
        except SerpShotError as api_error:
            print(f"API Error: {api_error.message}")
            if hasattr(api_error, 'status_code') and api_error.status_code:
                print(f"Status code: {api_error.status_code}")
                
        finally:
            client.close()
            
    except Exception as unexpected_error:
        print(f"Unexpected error: {unexpected_error}")


def batch_search_example():
    """Batch search example.
    
    This is the recommended approach when you have multiple queries
    with the same parameters. It makes a single API call instead of
    multiple separate calls, which is more efficient.
    """
    print("=== Batch Search Example (Recommended) ===\n")
    
    with SerpShot(api_key=API_KEY) as client:
        queries = ["Python", "JavaScript", "Rust"]
        # Pass list to search() - single API call, returns list of responses
        responses = client.search(queries, num=5)
        
        # Type check: responses is list[SearchResponse] when query is list[str]
        if isinstance(responses, list):
            for query, response in zip(queries, responses):
                if isinstance(response, SearchResponse):
                    print(f"{query}: {len(response.results)} results")
                    if response.results:
                        print(f"  Top: {response.results[0].title}\n")


if __name__ == "__main__":
    # Run all examples
    try:
        basic_search_example()
        print("\n" + "="*50 + "\n")
        
        advanced_search_example()
        print("\n" + "="*50 + "\n")
        
        image_search_example()
        print("\n" + "="*50 + "\n")
        
        pagination_example()
        print("\n" + "="*50 + "\n")
        
        batch_search_example()
        print("\n" + "="*50 + "\n")
        
        error_handling_example()
        
    except Exception as main_error:
        print(f"Error running examples: {main_error}")
        print("\nMake sure to set your API_KEY at the top of this file!")
