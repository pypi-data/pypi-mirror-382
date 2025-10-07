class Config:
    """Configuration for a weaver project"""
    def __init__(self):
        self.project_name = ""
        self.project_slug = ""
        self.description = ""
        self.author_name = ""
        self.author_email = ""
        self.data_sources = []
        self.database = ""
        self.search_engine = ""
        self.orchestrator = ""
        self.api_framework = ""
        self.include_api_scraping = False
        self.include_web_scraping = False
        self.include_vector_search = False
        self.include_nlp = False
        self.use_docker = False
        self.use_pytest = False

def create_config(project_name, project_slug, description, author_name, author_email, data_sources,
                  database, search_engine, orchestrator, api_framework, include_api_scraping,
                  include_web_scraping, include_vector_search, include_nlp, use_docker, use_pytest) -> Config:
    config = Config()
    config.project_name = project_name
    config.project_slug = project_slug
    config.description = description
    config.author_name = author_name
    config.author_email = author_email
    config.data_sources = data_sources
    config.database = database
    config.search_engine = search_engine
    config.orchestrator = orchestrator
    config.api_framework = api_framework
    config.include_api_scraping = include_api_scraping
    config.include_web_scraping = include_web_scraping
    config.include_vector_search = include_vector_search
    config.include_nlp = include_nlp
    config.use_docker = use_docker
    config.ues_pytest = use_pytest
    return config



TEMPLATES = {
    "advanced-search": {
        "name": "Pokémon Team Builder with Vector Search",
        "description": "Build optimal Pokémon teams using hybrid search",
        "data_sources": ["api", "datasets", "web_scraping"],
        "database": "postgresql",
        "search_engine": "vector_hybrid",
        "orchestrator": "prefect",
        "api_framework": "fastapi",
        "include_nlp": "no",
        "use_docker": "yes",
        "include_vector_search": "yes",
    },
    "knowledge-graph": {
        "name": "AI Company Knowledge Graph",
        "description": "Track relationships between AI companies and technologies",
        "data_sources": ["web_scraping", "api", "github"],
        "database": "neo4j",
        "search_engine": "elasticsearch",
        "orchestrator": "prefect",
        "api_framework": "fastapi",
        "include_nlp": "yes",
        "use_docker": "yes",
        "include_vector_search": "no"
    },
    "news-analyzer": {
        "name": "News Aggregator with Bias Analysis",
        "description": "Aggregate news with political bias detection",
        "data_sources": ["rss", "web_scraping", "social_media"],
        "database": "postgresql",
        "search_engine": "elasticsearch",
        "orchestrator": "prefect",
        "api_framework": "fastapi",
        "include_nlp": "yes",
        "use_docker": "yes",
        "include_vector_search": "yes"
    }
}
