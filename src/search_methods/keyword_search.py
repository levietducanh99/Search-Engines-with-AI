from src.utils.db_connect import get_supabase_client
import time
import spacy
import re


def keyword_search(query: str, page_size=1000):
    # Initialize Supabase client
    supabase = get_supabase_client()

    # Load spaCy model
    try:
        nlp = spacy.load("en_core_web_md")
    except OSError:
        print("Downloading spaCy model...")
        import subprocess
        subprocess.call(["python", "-m", "spacy", "download", "en_core_web_md"])
        nlp = spacy.load("en_core_web_md")

    start_time = time.time()

    # First check if query exactly matches a headline
    exact_headline_match = supabase.table("WebScrapData").select("headline, keywords").eq("headline", query).execute()
    if exact_headline_match.data:
        row = exact_headline_match.data[0]
        query_doc = nlp(query.lower())
        query_tokens = [token.text for token in query_doc if not token.is_stop and not token.is_punct]
        if not query_tokens:
            query_tokens = [token.text for token in query_doc]

        results = [{
            "headline": row["headline"],
            "keywords": row["keywords"],
            "percent_match": 100.0,
            "matched_count": f"{len(query_tokens)}/{len(query_tokens)}",
            "token_matches": [{"query_token": t, "matched_db_tokens": [t]} for t in query_tokens]
        }]
        return results, time.time() - start_time

    # Process query with spaCy
    query_doc = nlp(query.lower())
    query_tokens = [token.text for token in query_doc if not token.is_stop and not token.is_punct]
    if not query_tokens:
        query_tokens = [token.text for token in query_doc]

    print(f"Query tokens: {query_tokens}")

    if not query_tokens:
        return [], time.time() - start_time

    # Process in batches to handle large data
    page = 0
    results = []

    while True:
        # Fetch data in batches
        response = supabase.table("WebScrapData").select("headline, keywords").range(page * page_size, (
                    page + 1) * page_size - 1).execute()

        if not response.data:
            break

        for row in response.data:
            # Skip rows with empty keywords
            if not row.get("keywords"):
                continue

            # Split keywords and normalize
            db_keywords = row["keywords"].lower()
            db_tokens = [keyword.strip() for keyword in db_keywords.split(',')]

            # Count matching tokens and track matches
            matched_tokens = 0
            token_matches = []

            for query_token in query_tokens:
                match_found = False
                matching_db_tokens = []

                for db_token in db_tokens:
                    if query_token == db_token:
                        match_found = True
                        matching_db_tokens.append(db_token)

                if match_found:
                    matched_tokens += 1
                    token_matches.append({
                        "query_token": query_token,
                        "matched_db_tokens": matching_db_tokens
                    })

            # Calculate percent match
            if len(query_tokens) > 0:
                percent_match = (matched_tokens / len(query_tokens)) * 100

                if percent_match > 0:
                    results.append({
                        "headline": row["headline"],
                        "keywords": row["keywords"],
                        "percent_match": percent_match,
                        "matched_count": f"{matched_tokens}/{len(query_tokens)}",
                        "token_matches": token_matches
                    })

        page += 1

        # Exit if we've processed all data
        if len(response.data) < page_size:
            break

    # Sort results by percent match
    results.sort(key=lambda x: x["percent_match"], reverse=True)

    # Limit to top 10
    results = results[:10]

    return results, time.time() - start_time


if __name__ == "__main__":
    query = "Health Benefits Of Friends It's Healthy To Spend Time With Loved Ones"
    results, execution_time = keyword_search(query)

    print("\nKeyword Search Results from WebScrapData:")
    for result in results:
        print(f"Headline: {result['headline']}")
        print(f"Keywords: {result['keywords']}")
        print(f"Matched: {result['matched_count']} tokens")
        print(f"Percent Match: {result['percent_match']:.2f}%")
        print("Token Matches:")
        for match in result['token_matches']:
            print(f"  Query token '{match['query_token']}' matched with: {', '.join(match['matched_db_tokens'])}")
        print("-" * 50)
    print(f"Execution Time: {execution_time:.4f} seconds")