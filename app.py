import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()

st.set_page_config(page_title="LinkedIn BD Agent", layout="wide")


def get_secret(name):
    value = os.getenv(name)
    if value:
        return value

    try:
        return st.secrets.get(name)
    except FileNotFoundError:
        return None


openai_api_key = get_secret("OPENAI_API_KEY")
tavily_api_key = get_secret("TAVILY_API_KEY")

missing_secrets = [
    name
    for name, value in {
        "OPENAI_API_KEY": openai_api_key,
        "TAVILY_API_KEY": tavily_api_key,
    }.items()
    if not value
]

if missing_secrets:
    st.error(
        "Missing required Streamlit secrets: " + ", ".join(missing_secrets)
    )
    st.info(
        "Open Manage app > Settings > Secrets, add the missing keys, save, and reboot the app."
    )
    st.stop()

client = OpenAI(api_key=openai_api_key)
tavily_client = TavilyClient(api_key=tavily_api_key)


def extract_json(text):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()

    if text.startswith("```"):
        text = text.replace("```", "", 1).strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


st.title("LinkedIn BD Agent")

with st.sidebar:
    st.header("Private business context")
    st.caption(
        "This information stays in your current session and is not stored in the repository."
    )
    user_profile = st.text_area(
        "Your professional profile",
        height=220,
        placeholder="Describe your experience, services, strengths, and relevant proof.",
    )
    ideal_leads = st.text_area(
        "Your ideal leads",
        height=180,
        placeholder="Describe target roles, businesses, industries, problems, and exclusions.",
    )
tab1, tab2 = st.tabs(["Analyze Lead", "Business Discovery"])


with tab1:
    st.subheader("Analyze LinkedIn Lead")
    lead_text = st.text_area("LinkedIn Lead Text", height=300)

    if st.button("Analyze Lead"):
        if not lead_text.strip():
            st.warning("Please paste LinkedIn profile/company text first.")
        else:
            prompt = f"""
You are a LinkedIn business development assistant for the user.

Analyze whether this LinkedIn lead is a good business opportunity.

User Profile:
{user_profile}

Ideal Leads:
{ideal_leads}

LinkedIn Lead Text:
{lead_text}

Return:

1. Lead Match Score out of 100
2. Lead Type
3. Why this lead is relevant
4. Possible pain points
5. How the user can help
6. Red flags
7. Suggested connection message under 250 characters
8. Suggested follow-up message
9. Suggested service angle
"""

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            st.markdown(response.output_text)



with tab2:
    st.subheader("Discover Public Business Leads")
    st.write(
        "Discover product businesses, subscription businesses, delivery companies, and ecommerce brands that may benefit from WooCommerce, subscriptions, automation, and operational improvements."
    )

    discovery_industry = st.text_input(
        "Target Industry",
        placeholder="Example: dairy delivery, grocery subscription, meal delivery, wellness",
        key="discovery_industry"
    )

    discovery_location = st.text_input(
        "Target Location",
        placeholder="Example: Europe, USA, Australia, Netherlands",
        key="discovery_location"
    )

    discovery_business_type = st.text_input(
        "Business Type",
        placeholder="Example: subscription commerce, recurring delivery, farm-to-customer",
        key="discovery_business_type"
    )

    max_results = st.slider(
        "Results per query",
        min_value=3,
        max_value=10,
        value=5
    )

    if st.button("Business Discovery"):
        if not discovery_industry.strip() and not discovery_business_type.strip():
            st.warning("Please enter at least Industry or Business Type.")
        else:
            query_prompt = f"""
You are a lead discovery specialist.

Your goal is to find BUSINESS COMPANIES, not IT professionals.

Target Industry:
{discovery_industry}

Target Location:
{discovery_location}

Business Type:
{discovery_business_type}

Ideal Business Types:
- Dairy delivery
- Grocery delivery
- Farm fresh delivery
- Farm-to-customer businesses
- Meal subscription companies
- Wellness subscription companies
- Water delivery businesses
- Direct-to-consumer brands
- Ecommerce subscription businesses
- Recurring delivery businesses

Avoid:
- Agencies
- Software companies
- IT consulting firms
- Freelancers
- Developers
- Research organizations
- Payment companies
- SaaS vendors

Rules:
- Focus primarily on LinkedIn company pages and company websites.
- Use site:linkedin.com/company where useful.
- Search for actual businesses that sell products/services.
- Add exclusion keywords when helpful:
  -agency
  -software
  -consulting
  -consultant
  -developer
  -freelancer
  -research
  -payment
  -SaaS

Return exactly 5 search queries.
Only return the queries.
No explanations.
"""

            query_response = client.responses.create(
                model="gpt-4.1-mini",
                input=query_prompt
            )

            queries = [
                q.strip("- ").strip()
                for q in query_response.output_text.split("\n")
                if q.strip()
            ]

            st.markdown("## Generated Search Queries")
            for q in queries:
                st.code(q)

            all_results = []

            with st.spinner("Searching public web results..."):
                for query in queries:
                    try:
                        search_response = tavily_client.search(
                            query=query,
                            search_depth="basic",
                            max_results=max_results
                        )

                        for item in search_response.get("results", []):
                            all_results.append({
                                "query": query,
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "content": item.get("content", "")
                            })

                    except Exception as e:
                        st.error(f"Search failed for query: {query}")
                        st.error(str(e))

            if not all_results:
                st.warning("No results found.")
            else:
                seen_urls = set()
                unique_results = []

                for result in all_results:
                    if result["url"] not in seen_urls:
                        unique_results.append(result)
                        seen_urls.add(result["url"])

                scoring_prompt = f"""
You are evaluating discovered companies for the user.

User Profile:
{user_profile}

Ideal Leads:
{ideal_leads}

Search Results:
{unique_results}

Important:

The user is NOT looking for:
- Developers
- CTOs without business ownership
- Freelancers
- Agencies
- IT consultants
- Software vendors
- Payment providers
- Research organizations

The user IS looking for:
- Product businesses
- Subscription businesses
- Ecommerce brands
- Delivery businesses
- Direct-to-consumer brands
- Businesses with recurring operations
- Businesses likely using ecommerce systems

Strong Matches:
- Dairy delivery company
- Grocery delivery company
- Farm fresh delivery company
- Meal subscription company
- Wellness subscription company
- Water delivery company
- D2C ecommerce brand
- Subscription commerce business

Return ONLY valid JSON.

Format:
{{
  "leads": [
    {{
      "company_name": "Company name here",
      "url": "https://example.com",
      "lead_type": "Delivery Business",
      "match_score": 85,
      "why_relevant": "Short reason",
      "possible_business_pain_point": "Short pain point",
      "suggested_next_action": "Find founder or operations leader on LinkedIn"
    }}
  ]
}}

Rules:
- Return only useful business leads.
- Sort by match_score descending.
- Do not include markdown.
- Do not include explanations outside JSON.
- Do not include software companies.
- Do not include agencies.
- Do not include freelancer profiles.
"""

                score_response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=scoring_prompt
                )

                st.markdown("## Ranked Business Leads")

                try:
                    parsed = json.loads(extract_json(score_response.output_text))
                    leads = parsed.get("leads", [])

                    if not leads:
                        st.warning("No useful business leads found.")
                    else:
                        st.session_state["discovered_leads"] = leads
                        st.session_state.pop("selected_company", None)
                        st.session_state.pop("decision_people", None)

                except Exception as e:
                    st.error("Could not parse company response as JSON.")
                    st.code(score_response.output_text)
                    st.error(str(e))

    leads = st.session_state.get("discovered_leads", [])

    if leads:
        for index, lead in enumerate(leads):
            with st.container(border=True):
                st.subheader(
                    f"{lead.get('company_name', 'Unknown Company')} — Score {lead.get('match_score', 0)}/100"
                )

                st.write(f"**Type:** {lead.get('lead_type', '')}")
                st.write(f"**URL:** {lead.get('url', '')}")
                st.write(f"**Why Relevant:** {lead.get('why_relevant', '')}")
                st.write(
                    f"**Possible Pain Point:** {lead.get('possible_business_pain_point', '')}"
                )
                st.write(f"**Next Action:** {lead.get('suggested_next_action', '')}")

                if st.button(
                    "Find People + Generate Message",
                    key=f"find_people_{index}"
                ):
                    st.session_state["selected_company"] = lead
                    st.session_state.pop("decision_people", None)

    if "selected_company" in st.session_state:
        company = st.session_state["selected_company"]

        st.markdown("---")
        st.markdown(f"## Decision Makers for {company.get('company_name')}")

        if "decision_people" not in st.session_state:
            people_queries = [
                f'site:linkedin.com/in "Founder" "{company.get("company_name")}"',
                f'site:linkedin.com/in "Co-Founder" "{company.get("company_name")}"',
                f'site:linkedin.com/in "CEO" "{company.get("company_name")}"',
                f'site:linkedin.com/in "COO" "{company.get("company_name")}"',
                f'site:linkedin.com/in "Head of Operations" "{company.get("company_name")}"',
                f'site:linkedin.com/in "Head of Ecommerce" "{company.get("company_name")}"',
            ]

            st.markdown("### People Search Queries")
            for pq in people_queries:
                st.code(pq)

            people_results = []

            with st.spinner("Finding public LinkedIn decision makers..."):
                for pq in people_queries:
                    try:
                        people_search = tavily_client.search(
                            query=pq,
                            search_depth="basic",
                            max_results=5
                        )

                        for item in people_search.get("results", []):
                            people_results.append({
                                "query": pq,
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "content": item.get("content", "")
                            })

                    except Exception as e:
                        st.error(f"People search failed: {pq}")
                        st.error(str(e))

            seen_people_urls = set()
            unique_people_results = []

            for result in people_results:
                if result["url"] not in seen_people_urls:
                    unique_people_results.append(result)
                    seen_people_urls.add(result["url"])

            decision_prompt = f"""
You are helping the user identify the best LinkedIn decision makers inside a target company.

Company:
{company}

People Search Results:
{unique_people_results}

User Profile:
{user_profile}

Rules:
- Prefer Founder, Co-founder, CEO, COO, Head of Operations, Head of Ecommerce.
- Avoid developers, engineers, recruiters, unrelated consultants, agencies, and people with no clear connection to the company.
- Return only useful people connected to this company.
- Messages should sound human, simple, and specific.
- Do not sound like a sales template.
- Do not overclaim.
- Mention the user's relevant experience only when supported by the supplied profile.
- Keep connection message under 250 characters.

Return ONLY valid JSON:

{{
  "people": [
    {{
      "name": "Person name",
      "role": "Role/title",
      "linkedin_url": "https://linkedin.com/in/...",
      "match_score": 90,
      "why_this_person": "Short reason",
      "connection_message": "Natural connection request under 250 characters",
      "follow_up_message": "Short human follow-up message"
    }}
  ]
}}
"""

            decision_response = client.responses.create(
                model="gpt-4.1-mini",
                input=decision_prompt
            )

            try:
                people_data = json.loads(extract_json(decision_response.output_text))
                st.session_state["decision_people"] = people_data.get("people", [])

            except Exception as e:
                st.error("Could not parse people response as JSON.")
                st.code(decision_response.output_text)
                st.error(str(e))

        people = st.session_state.get("decision_people", [])

        if not people:
            st.warning("No strong decision makers found from public search.")
        else:
            for p_index, person in enumerate(people):
                with st.container(border=True):
                    st.subheader(
                        f"{person.get('name', 'Unknown')} — {person.get('role', '')}"
                    )

                    st.write(f"**LinkedIn:** {person.get('linkedin_url', '')}")
                    st.write(f"**Score:** {person.get('match_score', 0)}/100")
                    st.write(f"**Why:** {person.get('why_this_person', '')}")

                    st.markdown("**Connection Message**")
                    st.code(person.get("connection_message", ""))

                    st.markdown("**Follow-up Message**")
                    st.code(person.get("follow_up_message", ""))