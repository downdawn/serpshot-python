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

async def concurrent_searches_example():
    """Concurrent searches example with different parameters."""
    print("=== Concurrent Searches Example (Different Parameters) ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # When queries need different parameters, use asyncio.gather
        # For same parameters, prefer batch_search_example() instead
        tasks = [
            client.search("Python programming", num=10, gl="us"),
            client.search("JavaScript tutorials", num=5, gl="uk"),
            client.search("Rust language", num=20, gl="us"),
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
    """Batch image searches example using queries parameter."""
    print("=== Batch Image Searches Example ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # Use batch search for multiple queries with same parameters
        queries = ["cute cats", "beautiful landscapes", "modern architecture"]
        
        # Pass list to image_search() - single API call for all queries
        responses = await client.image_search(queries, num=5)
        
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


async def batch_with_progress_example():
    """Batch processing with progress tracking."""
    print("=== Batch Processing with Progress Example ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        queries = [
            "Python tutorial",
            "JavaScript guide",
            "Rust programming",
            "Go language",
            "TypeScript basics",
        ]
        
        print(f"Processing {len(queries)} queries in batch...\n")
        
        # Use batch search for better efficiency (single API call)
        responses = await client.search(queries, num=3)
        
        # Process results
        if isinstance(responses, list):
            for i, (query, response) in enumerate(zip(queries, responses), 1):
                print(f"[{i}/{len(queries)}] {query}: {len(response.results)} results")
            
            print(f"\nCompleted! Total results: {sum(len(r.results) for r in responses)}")


async def advanced_concurrent_example():
    """Advanced example: batch vs concurrent for different scenarios."""
    print("=== Advanced Example: Batch vs Concurrent ===\n")
    
    async with AsyncSerpShot(api_key=API_KEY) as client:
        # Scenario 1: Same parameters - use batch search (more efficient)
        print("Scenario 1: Batch search (same parameters)")
        batch_queries = [f"Python topic {i}" for i in range(5)]
        batch_responses = await client.search(batch_queries, num=5)
        if isinstance(batch_responses, list):
            print(f"  ✓ Processed {len(batch_responses)} queries in 1 API call\n")
        
        # Scenario 2: Different parameters - use concurrent with semaphore
        print("Scenario 2: Concurrent search (different parameters)")
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
        
        async def search_with_limit(query, num_results):
            async with semaphore:
                return await client.search(query, num=num_results)
        
        concurrent_tasks = [
            search_with_limit(f"Query {i}", num_results=5 + i)
            for i in range(5)
        ]
        concurrent_responses = await asyncio.gather(*concurrent_tasks)
        print(f"  ✓ Processed {len(concurrent_responses)} queries with rate limiting\n")
        
        print("Tip: Use batch search when parameters are the same, "
              "use concurrent when parameters differ")


async def main():
    """Run all async examples."""
    try:
        await basic_search_example()
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

        await batch_with_progress_example()
        print("\n" + "="*50 + "\n")

        await advanced_concurrent_example()
        print("\n" + "="*50 + "\n")

        await error_handling_example()
        
    except Exception as main_error:
        print(f"Error running examples: {main_error}")
        print("\nMake sure to set your API_KEY at the top of this file!")


if __name__ == "__main__":
    asyncio.run(main())
