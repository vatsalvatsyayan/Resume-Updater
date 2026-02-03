
import json
import re
from pathlib import Path

def refine_with_maximal_allowlist(input_file: Path, output_file: Path):
    """
    Reads a JSON list of keywords and filters it using a final, greatly expanded
    allowlist to ensure all plausible technical keywords are included.
    """
    print(f"Reading keywords from: {input_file}")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    keywords_to_process = data.get("keywords", [])
    print(f"Loaded {len(keywords_to_process)} keywords to process.")

    # --- Controlled Normalization Mapping ---
    normalization_map = {
        "reactjs": "react",
        "react.js": "react",
        "react (typescript)": "react",
        "nodejs": "node.js",
        "node": "node.js",
        ", node.js": "node.js",
        "go (golang)": "golang",
        "springboot": "spring boot",
        "spring framework": "spring",
        "nextjs": "next.js",
        "angular.js": "angular",
        "angularjs": "angular",
        "vuejs": "vue",
        "tensorflow, pytorch": "tensorflow",
        "tensorflow, keras": "tensorflow",
        "amazon aws": "aws",
        "google cloud platform": "gcp",
        "microsoft azure": "azure",
        "azure cloud": "azure",
        "aws services": "aws",
        "rest api": "rest",
        "graphql apis": "graphql",
        "ci/cd pipelines": "ci/cd",
        "devops principles": "devops",
        "machine learning": "ml",
        "object-oriented": "oop",
        "version control": "git",
    }

    # --- Maximal Expanded Hard-Skill Allowlist ---
    allowlist = {
        # Programming Languages
        "python", "java", "c#", "c++", "c", "javascript", "typescript", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "perl", "bash", "shell",
        "powershell", "groovy", "haskell", "elixir", "dart", "vb", "visualbasic",
        "objective-c", "cobol", "es6", "js", "ts", "xaml",

        # Frameworks, Libraries & SDKs
        "node.js", "react", "angular", "vue", "vue.js", "next.js", "nestjs",
        "spring", "spring boot", "django", "flask", "fastapi", "laravel", "rubyonrails",
        "dotnet", ".net", "entity framework", "hibernate", "numpy", "pandas",
        "scikit-learn", "tensorflow", "pytorch", "keras", "spark", "pyspark", "hadoop",
        "jquery", "redux", "rxjs", "mobx", "threejs", "webgl", "opengl", "vulkan",
        "junit", "pytest", "xunit", "selenium", "cypress", "playwright", "webdriverio",
        "langchain", "llamaindex", "vllm", "trpc", "chartjs", "d3", "office.js",
        "react native", "flutter", "xamarin", "ionic", "swiftui", "jetpack compose",
        "express.js", "powerbi", "tableau", "sdk", "less", "sass", "emr", "airflow",
        "apache", "dbt", "lora", "posthog", "ssr", "webrtc", "wordpress", "appsec", "autocad",
        "bitwarden", "chatgpt", "codegpt", "customgpt", "docugpt", "keras",
        "tensorflow", "hugging face", "hf", "latex", "netsuite", "quickbooks",
        "sage", "salesforce", "sharepoint", "servicenow", "splunk", "workday",

        # Databases
        "sql", "mysql", "postgresql", "postgres", "mssql", "sql server", "oracle", "sqlite",
        "mariadb", "nosql", "mongodb", "redis", "cassandra", "couchdb", "dynamodb",
        "elasticsearch", "influxdb", "cockroachdb", "scylladb", "bigtable", "hbase",
        "hive", "appsync", "rds", "bigquery", "clickhouse", "duckdb", "tidb", "tiledb",
        "timescaledb", "jdbc", "sec-db", "redshift",

        # Cloud & Infrastructure
        "aws", "azure", "gcp", "google cloud", "amazon web services", "redhat", "centos",
        "ec2", "s3", "lambda", "vpc", "iam", "cloudwatch", "ecs", "eks", "fargate",
        "rds", "dynamodb", "sqs", "sns", "kinesis", "cloudfront", "route53",
        "azure functions", "azure devops", "gke", "gcs", "cloud pubsub", "vertex ai",
        "iaas", "paas", "saas", "serverless", "aks", "heroku", "digitalocean", "linode", "ovh",
        "vmware", "cloud computing",

        # AI, Data & Specialized Tools
        "agentcore", "agentic ai", "ai/ml", "amazon quicksight", "angularjs", "apache iceberg",
        "apache kafka", "apache spark", "arcgis", "autogen", "capcut", "clickup",
        "codesignal", "copilot", "github copilot", "cryoet", "dag", "deepquery",
        "deepseek", "ediscovery", "flashattention", "flexgen", "flutterflow",
        "freeswitch", "identityserver", "langgraph", "leetcode", "linux", "macos",
        "maplibre", "nemo", "pagespeed", "promptlayer", "redpajama",
        "reinforcement learning (rl)", "sagemaker", "solidworks", "spring cloud",
        "starrocks", "web services", "win32",

        # DevOps & Tools
        "docker", "kubernetes", "k8s", "ci/cd", "jenkins", "gitlab ci", "github actions",
        "circleci", "travis ci", "teamcity", "ansible", "puppet", "chef", "terraform",
        "cloudformation", "pulumi", "vagrant", "git", "svn", "clearcase", "perforce",
        "jira", "confluence", "sonarqube", "artifactory", "nexus", "gradle", "maven",
        "npm", "yarn", "webpack", "babel", "argocd", "devops", "devsecops", "mlops",
        "ide", "visual studio", "intellij", "autosys", "codepipeline", "gitlab", "github",
        "bitbucket", "pagerduty", "datadog", "new relic", "prometheus", "grafana",

        # CS Concepts & Protocols
        "api", "rest", "graphql", "grpc", "rpc", "json", "xml", "yaml", "html", "html5",
        "css", "css3", "http", "https-", "tcp", "udp", "ip", "dns", "ssh", "sftp", "ftp", "smtp",
        "oauth", "oauth2", "saml", "jwt", "sso", "ssl", "tls", "mtls",
        "oop", "data structures", "algorithms", "ai", "ml", "deep learning", "nlp", "dom",
        "computer vision", "generative ai", "llm", "rag", "gan", "transformer", "gpt",
        "microservices", "distributed systems", "event-driven", "message queue", "pubsub",
        "rabbitmq", "kafka", "activemq", "sqs", "sns",
        "orm", "mvc", "mvvm", "tdd", "bdd", "agile", "scrum", "kanban", "design patterns",
        "webassembly", "webrtc", "websockets", "cdn", "vm", "containerization", "etl", "elt",
        "data warehouse", "data lake", "data mining", "big data", "cybersecurity",
        "blockchain", "crypto", "smart contracts", "web3", "dapps", "lan", "wan", "vr", "uml",
        "backend", "frontend", "pdf", "soap", "dataframes", "cpu", "gpu", "hpc", "iot",
        "industrial iot", "firmware", "embedded", "robotics", "computer science",
        "olap", "oltp", "defi", "fintech", "edtech", "healthtech", "insurtech",
        "mobile", "ios", "android", "ipad", "iphone", "wifi", "voip", "ssr",
        "hdfs", "api gateway", "service mesh", "istio", "envoy", "linkerd",
    }

    refined_keywords = set()
    original_forms = {}

    for keyword in keywords_to_process:
        clean_kw = keyword.lower().strip(" .,;:'\"()[]{}<>/-+=")
        normalized_kw = normalization_map.get(clean_kw, clean_kw)
        
        if normalized_kw in allowlist:
            if normalized_kw not in original_forms or len(keyword) < len(original_forms[normalized_kw]):
                 original_forms[normalized_kw] = keyword
    
    sorted_refined_keywords = sorted(list(original_forms.values()), key=str.lower)

    print(f"Kept {len(sorted_refined_keywords)} keywords after applying the maximal allowlist.")

    output_data = {
        "description": "A highly-refined dictionary of technical keywords, filtered with a final, maximal allowlist.",
        "count": len(sorted_refined_keywords),
        "keywords": sorted_refined_keywords
    }

    print(f"Writing final refined dictionary to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Final refinement complete.")


def main():
    """CLI entry point."""
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "output" / "12_refined_tech_dictionary_v3.json"
    output_file = base_dir / "output" / "14_final_refined.json"

    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}")
        return

    refine_with_maximal_allowlist(input_file, output_file)


if __name__ == "__main__":
    main()
