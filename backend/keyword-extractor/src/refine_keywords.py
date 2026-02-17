
import json
from pathlib import Path

def refine_with_strict_allowlist(input_file: Path, output_file: Path):
    """
    Reads a JSON list of keywords and filters it using a strict, hand-curated
    allowlist of hard technical skills.
    """
    print(f"Reading keywords from: {input_file}")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    keywords_to_process = data.get("keywords", [])
    print(f"Loaded {len(keywords_to_process)} keywords to process.")

    # --- Strict Hard-Skill Allowlist ---
    # This list is hand-curated based on the user's request to only keep
    # specific categories of technical skills.
    allowlist = {
        # Programming Languages
        "python", "java", "c#", "c++", "c", "javascript", "typescript", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "perl", "bash", "shell",
        "powershell", "groovy", "haskell", "elixir", "dart", "vb", "visualbasic",
        "objective-c", "cobol",

        # Frameworks, Libraries & SDKs
        "node.js", "react", "angular", "vue", "vue.js", "next.js", "nestjs",
        "spring", "spring boot", "django", "flask", "fastapi", "laravel", "rubyonrails",
        "dotnet", ".net", "entity framework", "hibernate", "numpy", "pandas",
        "scikit-learn", "tensorflow", "pytorch", "keras", "spark", "pyspark", "hadoop",
        "jquery", "redux", "rxjs", "mobx", "threejs", "webgl", "opengl", "vulkan",
        "junit", "pytest", "xunit", "selenium", "cypress", "playwright", "webdriverio",
        "langchain", "llamaindex", "vllm", "trpc", "chartjs", "d3", "office.js",
        "react native", "flutter", "xamarin", "ionic", "swiftui", "jetpack compose",

        # Databases
        "sql", "mysql", "postgresql", "postgres", "mssql", "sql server", "oracle", "sqlite",
        "mariadb", "nosql", "mongodb", "redis", "cassandra", "couchdb", "dynamodb",
        "elasticsearch", "influxdb", "cockroachdb", "scylladb", "bigtable", "hbase",
        "hive", "appsync", "rds", "bigquery", "clickhouse", "duckdb", "tidb", "tiledb",
        "timescaledb",

        # Cloud & Infrastructure
        "aws", "azure", "gcp", "google cloud", "amazon web services",
        "ec2", "s3", "lambda", "vpc", "iam", "cloudwatch", "ecs", "eks", "fargate",
        "rds", "dynamodb", "sqs", "sns", "kinesis", "cloudfront", "route53",
        "azure functions", "azure devops", "gke", "gcs", "cloud pubsub", "vertex ai",
        "iaas", "paas", "saas", "serverless",

        # DevOps & Tools
        "docker", "kubernetes", "k8s", "ci/cd", "jenkins", "gitlab ci", "github actions",
        "circleci", "travis ci", "teamcity", "ansible", "puppet", "chef", "terraform",
        "cloudformation", "pulumi", "vagrant", "git", "svn", "clearcase", "perforce",
        "jira", "confluence", "sonarqube", "artifactory", "nexus", "gradle", "maven",
        "npm", "yarn", "webpack", "babel", "argocd", "devops", "devsecops", "mlops",

        # CS Concepts & Protocols
        "api", "rest", "graphql", "grpc", "rpc", "json", "xml", "yaml", "html", "css",
        "http", "https-", "tcp", "udp", "ip", "dns", "ssh", "sftp", "ftp", "smtp",
        "oauth", "saml", "jwt", "sso", "ssl", "tls", "mtls",
        "oop", "data structures", "algorithms", "ai", "ml", "deep learning", "nlp",
        "computer vision", "generative ai", "llm", "rag", "gan", "transformer",
        "microservices", "distributed systems", "event-driven", "message queue", "pubsub",
        "rabbitmq", "kafka", "activemq", "sqs", "sns",
        "orm", "mvc", "mvvm", "tdd", "bdd", "agile", "scrum", "kanban", "design patterns",
        "webassembly", "webrtc", "websockets", "cdn", "vm", "containerization", "etl", "elt",
        "data warehouse", "data lake", "data mining", "big data", "cybersecurity",
        "blockchain", "crypto", "smart contracts", "web3", "dapps",
    }

    refined_keywords = set()
    for keyword in keywords_to_process:
        # Process and clean the keyword before checking
        # Lowercase, strip leading/trailing spaces and special characters
        clean_kw = keyword.lower().strip(" .,;:'\"()[]{}<>/-+=")
        
        if clean_kw in allowlist:
            # Add the original casing if it's a better representation
            # but use the cleaned version for matching.
            refined_keywords.add(keyword)

    sorted_refined_keywords = sorted(list(refined_keywords), key=str.lower)

    print(f"Kept {len(sorted_refined_keywords)} keywords after applying the strict hard-skill allowlist.")

    output_data = {
        "description": "A highly-refined dictionary of technical keywords, filtered with a strict hard-skill allowlist.",
        "count": len(sorted_refined_keywords),
        "keywords": sorted_refined_keywords
    }

    print(f"Writing refined dictionary to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Refinement complete.")


def main():
    """CLI entry point."""
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "output" / "7_cleaned_tech_dictionary.json"
    output_file = base_dir / "output" / "8_refined_tech_dictionary.json"

    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}")
        return

    refine_with_strict_allowlist(input_file, output_file)


if __name__ == "__main__":
    main()
