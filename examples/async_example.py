"""Asynchronous usage examples for SerpShot SDK."""

import asyncio

from serpshot import AsyncSerpShot, SerpShotError
from serpshot.models import SearchResponse

# Replace with your actual API key
API_KEY = "your-api-key-here"


async def basic_search_example():
    """Basic async search example."""
    print("=== Basic Async Search Example ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # Perform a simple search
        response = await client.search("Python async programming")
        
        print(f"Query: {response.query}")
        print(f"Total results: {response.total_results}")
        print(f"Credits used: {response.credits_used}")
        print(f"\nResults ({len(response.results)}):\n")
        
        for i, result in enumerate(response.results[:5], 1):
            print(f"{i}. {result.title}")
            print(f"   {result.link}\n")


async def get_credits_example():
    """Get available credits example."""
    print("=== Get Available Credits Example ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        credits = await client.get_available_credits()
        print(f"Available credits: {credits}")


async def batch_search_example():
    """Batch search example using search with list.
    
    This is the recommended approach when you have multiple queries
    with the same parameters. It's more efficient than using asyncio.gather
    because it makes a single API call instead of multiple separate calls.
    """
    print("=== Batch Search Example (Recommended) ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # Perform batch search (single API call for all queries)
        # This is more efficient than using asyncio.gather for same parameters
        queries = [
            "Python programming",
            "JavaScript tutorials",
            "Rust language",
            "Go programming",
        ]
        
        # Pass list to search() - single API call, returns list of responses
        responses = await client.search(queries, num=5)

        # Process results
        # Type check: responses is list[SearchResponse] when query is list[str]
        if isinstance(responses, list):
            for query, response in zip(queries, responses):
                print(f"{query}: {len(response.results)} results")
                if response.results:
                    print(f"  Top result: {response.results[0].title}\n")

async def location_search_example():
    """Search with location parameter example - using string (recommended)."""
    print("=== Location Search Example ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # Search with location parameter for local results
        # Using string format (recommended and simpler)
        response = await client.search(
            "best restaurants",
            num=10,
            gl="us",
            location="US",  # String format: 'US', 'GB', 'CN', etc.
        )
        
        print(f"Found {len(response.results)} results for '{response.query}'")
        print(f"Total results: {response.total_results}")
        print(f"Search time: {response.search_time}s")
        if response.results:
            print(f"Top result: {response.results[0].title}")
            print(f"Top result URL: {response.results[0].link}\n")
        else:
            print("No results found.\n")


async def concurrent_searches_example():
    """Concurrent searches example with different parameters."""
    print("=== Concurrent Searches Example (Different Parameters) ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # When queries need different parameters, use asyncio.gather
        # For same parameters, prefer batch_search_example() instead
        tasks = [
            client.search("Python programming", num=10, gl="us", location="US"),
            client.search("JavaScript tutorials", num=5, gl="uk", location="GB"),
            client.search("Rust language", num=20, gl="us", location="US"),
        ]
        
        # Wait for all to complete
        responses = await asyncio.gather(*tasks)
        
        # Process results
        queries = ["Python programming", "JavaScript tutorials", "Rust language"]
        for query, response in zip(queries, responses):
            if isinstance(response, SearchResponse):
                print(f"{query}: {len(response.results)} results")
                if response.results:
                    print(f"  Top result: {response.results[0].title}\n")


async def concurrent_image_searches_example():
    """Batch image searches example with location parameter."""
    print("=== Batch Image Searches Example ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # Use batch search for multiple queries with same parameters
        queries = ["cute cats", "beautiful landscapes", "modern architecture"]
        
        # Pass list to image_search() - single API call for all queries
        # Include location parameter for local results
        responses = await client.image_search(
            queries, 
            num=5,
            gl="us",
            location="US",
        )
        
        # Process results
        if isinstance(responses, list):
            for query, response in zip(queries, responses):
                print(f"{query}: {len(response.results)} images found")


async def mixed_search_types_example():
    """Mix different search types concurrently."""
    print("=== Mixed Search Types Example ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # Run different types of searches concurrently
        normal_search = client.search("Python", num=10)
        image_search = client.image_search("Python logo", num=5)
        
        # Wait for all
        normal_resp, image_resp = await asyncio.gather(
            normal_search,
            image_search,
        )
        
        print(f"Normal search: {len(normal_resp.results)} results")
        print(f"Image search: {len(image_resp.results)} images")


async def error_handling_example():
    """Error handling in async context."""
    print("=== Async Error Handling Example ===\n")
    
    try:
        async with AsyncSerpShot(api_key=API_KEY) as client:
            response = await client.search("test query")
            print(f"Success! Got {len(response.results)} results")
            
    except SerpShotError as api_error:
        print(f"API Error: {api_error.message}")
        if hasattr(api_error, 'status_code') and api_error.status_code:
            print(f"Status code: {api_error.status_code}")
    except Exception as unexpected_error:
        print(f"Unexpected error: {unexpected_error}")




async def main():
    """Run all async examples."""
    try:
        await get_credits_example()
        print("\n" + "="*50 + "\n")

        await basic_search_example()
        print("\n" + "="*50 + "\n")

        await location_search_example()
        print("\n" + "="*50 + "\n")

        await batch_search_example()
        print("\n" + "="*50 + "\n")

        # Note: concurrent_searches_example shows when to use asyncio.gather
        # (when queries need different parameters)
        await concurrent_searches_example()
        print("\n" + "="*50 + "\n")

        await concurrent_image_searches_example()
        print("\n" + "="*50 + "\n")

        await mixed_search_types_example()
        print("\n" + "="*50 + "\n")

        await error_handling_example()
        
    except Exception as main_error:
        import traceback
        print(f"Error running examples: {main_error}")
        print(f"Error type: {type(main_error).__name__}")
        traceback.print_exc()
        print("\nMake sure to set your API_KEY at the top of this file!")


if __name__ == "__main__":
    asyncio.run(main())
