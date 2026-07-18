import json
from itertools import product

FIELDS = ["industries","business_models","keywords","countries","company_sizes","job_titles","decision_makers","search_queries","negative_keywords","priority_sources"]
INTENTS = ["hiring","growth","expansion","ecommerce","subscription","payments","automation","integration","operations","platform migration","consulting","contract","partnership","technical advisor","optimization","modernization","recurring revenue","customer portal","order management","performance"]


def _clean(values):
    if not isinstance(values, list):
        return []
    return list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))


def parse_strategy_response(text):
    fence = chr(96) * 3
    value = text.strip()
    if value.startswith(fence + "json"):
        value = value[7:]
    elif value.startswith(fence):
        value = value[3:]
    if value.endswith(fence):
        value = value[:-3]
    data = json.loads(value.strip())
    if not isinstance(data, dict):
        raise ValueError("Discovery Strategy must be a JSON object.")
    strategy = {field: _clean(data.get(field)) for field in FIELDS}
    required = ["industries","business_models","keywords","countries","decision_makers"]
    missing = [field for field in required if not strategy[field]]
    if missing:
        raise ValueError("Discovery Strategy omitted: " + ", ".join(missing))
    return strategy


def expand_search_queries(strategy, minimum=100, maximum=140):
    queries = list(strategy.get("search_queries") or [])
    exclusions = " ".join(f'-"{word}"' if " " in word else f"-{word}" for word in strategy.get("negative_keywords", [])[:10])
    patterns = [
        '"{industry}" "{model}" {country} "{intent}"',
        'site:linkedin.com/company "{industry}" "{model}" {country} "{intent}"',
        '"{industry}" company {country} "{keyword}" "{intent}"',
        'site:remoteok.com "{keyword}" {country} "{intent}"',
        'site:remotive.com "{industry}" "{keyword}" "{intent}"',
    ]
    combinations = product(strategy["industries"][:8], strategy["business_models"][:6], strategy["countries"][:8], strategy["keywords"][:10], INTENTS)
    for industry, model, country, keyword, intent in combinations:
        for pattern in patterns:
            query = pattern.format(industry=industry, model=model, country=country, keyword=keyword, intent=intent)
            queries.append((query + (" " + exclusions if exclusions else "")).strip())
            if len(dict.fromkeys(queries)) >= maximum:
                break
        if len(dict.fromkeys(queries)) >= maximum:
            break
    queries = list(dict.fromkeys(query for query in queries if query))
    if len(queries) < minimum:
        raise ValueError("The strategy did not contain enough dimensions to generate 100 queries.")
    strategy["search_queries"] = queries[:maximum]
    return strategy


def generate_discovery_strategy(client, business_dna):
    prompt = f"""You are the Discovery Strategy Engine for BusinessDev OS.
Use only the supplied Business DNA. Create a precise opportunity-discovery strategy.
Favor quality and explainable relevance. Never invent experience or credentials.

BUSINESS DNA:
{json.dumps(business_dna, indent=2, default=str)}

Return only valid JSON with array fields: industries, business_models, keywords,
countries, company_sizes, job_titles, decision_makers, search_queries,
negative_keywords, priority_sources.
Provide 5-10 industries, 4-8 business models, 10-20 keywords, relevant countries,
company sizes, opportunity titles, decision makers, 15 seed queries, exclusions,
and sources selected from Company Websites, LinkedIn, RemoteOK, Remotive,
WeWorkRemotely, Himalayas, Working Nomads."""
    response = client.responses.create(model="gpt-4.1-mini", input=prompt)
    return expand_search_queries(parse_strategy_response(response.output_text))
