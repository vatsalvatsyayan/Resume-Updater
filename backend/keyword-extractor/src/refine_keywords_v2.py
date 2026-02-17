
import json
import re
from pathlib import Path

def refine_with_louder_filter(input_file: Path, output_file: Path):
    """
    Reads a JSON list of keywords and filters it using an expanded allowlist
    and controlled normalization to improve recall of valid tech skills.
    """
    print(f"Reading keywords from: {input_file}")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    keywords_to_process = data.get("keywords", [])
    print(f"Loaded {len(keywords_to_process)} keywords to process.")

    # --- Controlled Normalization Mapping ---
    # Maps common variants to a canonical keyword form.
    normalization_map = {
        "reactjs": "react",
        "react.js": "react",
        "react (typescript)": "react",
        "nodejs": "node.js",
        "node": "node.js",
        ", node.js": "node.js",
        "go (golang)": "golang",
        "springboot": "spring boot",
        "nextjs": "next.js",
        "angular.js": "angular",
        "angularjs": "angular",
        "vuejs": "vue",
        "tensorflow, pytorch": "tensorflow", # and pytorch will be caught separately
        "tensorflow, keras": "tensorflow", # and keras will be caught separately
        "amazon aws": "aws",
        "google cloud platform": "gcp",
        "microsoft azure": "azure",
        "rest api": "rest",
        "graphql apis": "graphql",
        "ci/cd pipelines": "ci/cd",
        "devops principles": "devops",
        "machine learning": "ml",
    }

    # --- Expanded Hard-Skill Allowlist ---
    # This list is significantly larger to improve recall.
    allowlist = {
        # Programming Languages
        "python", "java", "c#", "c++", "c", "javascript", "typescript", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "perl", "bash", "shell",
        "powershell", "groovy", "haskell", "elixir", "dart", "vb", "visualbasic",
        "objective-c", "cobol", "es6", "js", "ts",

        # Frameworks, Libraries & SDKs
        "node.js", "react", "angular", "vue", "vue.js", "next.js", "nestjs",
        "spring", "spring boot", "django", "flask", "fastapi", "laravel", "rubyonrails",
        "dotnet", ".net", "entity framework", "hibernate", "numpy", "pandas",
        "scikit-learn", "tensorflow", "pytorch", "keras", "spark", "pyspark", "hadoop",
        "jquery", "redux", "rxjs", "mobx", "threejs", "webgl", "opengl", "vulkan",
        "junit", "pytest", "xunit", "selenium", "cypress", "playwright", "webdriverio",
        "langchain", "llamaindex", "vllm", "trpc", "chartjs", "d3", "office.js",
        "react native", "flutter", "xamarin", "ionic", "swiftui", "jetpack compose",
        "express.js", "powerbi", "tableau", "sdk", "less", "sass", "emr",

        # Databases
        "sql", "mysql", "postgresql", "postgres", "mssql", "sql server", "oracle", "sqlite",
        "mariadb", "nosql", "mongodb", "redis", "cassandra", "couchdb", "dynamodb",
        "elasticsearch", "influxdb", "cockroachdb", "scylladb", "bigtable", "hbase",
        "hive", "appsync", "rds", "bigquery", "clickhouse", "duckdb", "tidb", "tiledb",
        "timescaledb", "jdbc", "sec-db",

        # Cloud & Infrastructure
        "aws", "azure", "gcp", "google cloud", "amazon web services", "redhat", "centos",
        "ec2", "s3", "lambda", "vpc", "iam", "cloudwatch", "ecs", "eks", "fargate",
        "rds", "dynamodb", "sqs", "sns", "kinesis", "cloudfront", "route53",
        "azure functions", "azure devops", "gke", "gcs", "cloud pubsub", "vertex ai",
        "iaas", "paas", "saas", "serverless", "aks",

        # DevOps & Tools
        "docker", "kubernetes", "k8s", "ci/cd", "jenkins", "gitlab ci", "github actions",
        "circleci", "travis ci", "teamcity", "ansible", "puppet", "chef", "terraform",
        "cloudformation", "pulumi", "vagrant", "git", "svn", "clearcase", "perforce",
        "jira", "confluence", "sonarqube", "artifactory", "nexus", "gradle", "maven",
        "npm", "yarn", "webpack", "babel", "argocd", "devops", "devsecops", "mlops",
        "ide", "visual studio", "intellij", "autosys", "codepipeline",

        # CS Concepts & Protocols
        "api", "rest", "graphql", "grpc", "rpc", "json", "xml", "yaml", "html", "html5",
        "css", "css3", "http", "https-", "tcp", "udp", "ip", "dns", "ssh", "sftp", "ftp", "smtp",
        "oauth", "saml", "jwt", "sso", "ssl", "tls", "mtls",
        "oop", "data structures", "algorithms", "ai", "ml", "deep learning", "nlp", "dom",
        "computer vision", "generative ai", "llm", "rag", "gan", "transformer", "gpt",
        "microservices", "distributed systems", "event-driven", "message queue", "pubsub",
        "rabbitmq", "kafka", "activemq", "sqs", "sns",
        "orm", "mvc", "mvvm", "tdd", "bdd", "agile", "scrum", "kanban", "design patterns",
        "webassembly", "webrtc", "websockets", "cdn", "vm", "containerization", "etl", "elt",
        "data warehouse", "data lake", "data mining", "big data", "cybersecurity",
        "blockchain", "crypto", "smart contracts", "web3", "dapps", "lan", "wan", "vr", "uml",
        "backend", "frontend", "pdf", "soap", "dataframes",
    }

    refined_keywords = set()
    original_forms = {}

    for keyword in keywords_to_process:
        # Clean the keyword for processing
        clean_kw = keyword.lower().strip(" .,;:'\"()[]{}<>/-+=")
        
        # Apply controlled normalization
        normalized_kw = normalization_map.get(clean_kw, clean_kw)
        
        if normalized_kw in allowlist:
            # Prefer shorter, canonical forms but keep track of original
            if normalized_kw not in original_forms or len(keyword) < len(original_forms[normalized_kw]):
                 original_forms[normalized_kw] = keyword
    
    # Use the stored original forms as the final list
    sorted_refined_keywords = sorted(list(original_forms.values()), key=str.lower)

    print(f"Kept {len(sorted_refined_keywords)} keywords after applying the looser filter.")

    output_data = {
        "description": "A refined dictionary of technical keywords, filtered with an expanded allowlist and controlled normalization.",
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
    output_file = base_dir / "output" / "10_refined_tech_dictionary_v2.json"

    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}")
        return

    refine_with_louder_filter(input_file, output_file)


if __name__ == "__main__":
    main()
