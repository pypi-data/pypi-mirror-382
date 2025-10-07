from ddgs import DDGS
from datetime import datetime
from git import Repo
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import trafilatura
import requests
import platform

DP_R_SYSTEM_PROMPT = """
You are DeepResearch, an advanced AI research assistant specializing in factual, multi-source synthesis. 
Your primary objective is to perform grounded, reliable research using verified public web information.

### Core Directives:
- Use Google Search grounding to find the most recent and credible sources.
- Cross-verify facts between multiple results before including them.
- If uncertain, explicitly state uncertainty.
- Never hallucinate information or fabricate citations.
- Always cite claims in Markdown footnotes or inline references (e.g., [1], [2]).
- Maintain a professional and academic tone.

### Output Format:
Produce a well-structured Markdown report with the following sections:
1. **Title**
2. **Summary (2-3 paragraphs)**
3. **Detailed Analysis**
   - Subsections covering different aspects of the topic
4. **Recent Developments** (if relevant)
5. **Conclusion**
6. **References** (numbered list of URLs)

### Style:
- Write concisely and clearly.
- Prefer factual accuracy over speculation.
- Avoid repetition.
- Do not include HTML or code unless necessary.
"""


def web_search(query: str, max_results: int = 10) -> dict:
    """Performs a web search using DuckDuckGo and returns a list of results."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=max_results)]
    return {"results": results}

def fetch(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded)
        return text
    return "Failed to fetch or extract content from the URL."

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def gemini_image_generate(prompt: str, save_to: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-image')
    response = model.generate_content(prompt)
    for image in response.candidates[0].content.parts:
        image.save_to_file(save_to)
    return "Image saved to `" + save_to + "`"

def gemini_codegen(prompt: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content(prompt, max_output_tokens=100000, temperature=0.1, top_p=0.8, candidate_count=1)
    return response.candidates[0].content.text

class GitMan:
    def __init__(self, repo_path: str):
        self.repo: Repo = Repo(repo_path)
        self.identity_set("OrewaAgent", "orewaagent@omegapy.com")
    def pull(self) -> str:
        try:
            self.repo.git.pull()
            return "Repository pulled successfully."
        except Exception as e:
            return f"Error pulling repository: {str(e)}"
    def commit(self, message: str) -> str:
        try:
            self.repo.git.add(A=True)
            self.repo.index.commit(message)
            return "Changes committed successfully."
        except Exception as e:
            return f"Error committing changes: {str(e)}"
    def identity_set(self, name: str, email: str) -> str:
        try:
            with self.repo.config_writer() as git_config:
                git_config.set_value("user", "name", name)
                git_config.set_value("user", "email", email)
            return "Git identity set successfully."
        except Exception as e:
            return f"Error setting git identity: {str(e)}"
    def push(self) -> str:
        try:
            origin = self.repo.remote(name='origin')
            origin.push()
            return "Changes pushed successfully."
        except Exception as e:
            return f"Error pushing changes: {str(e)}"
    def diff(self) -> str:
        try:
            diff = self.repo.git.diff()
            return diff if diff else "No differences found."
        except Exception as e:
            return f"Error getting diff: {str(e)}"
    def status(self) -> str:
        try:
            status = self.repo.git.status()
            return status
        except Exception as e:
            return f"Error getting status: {str(e)}"
    @staticmethod
    def clone(repo_url: str, to_path: str) -> str:
        try:
            Repo.clone_from(repo_url, to_path)
            return "Repository cloned successfully."
        except Exception as e:
            return f"Error cloning repository: {str(e)}"
    @staticmethod
    def init(repo_path: str) -> str:
        try:
            Repo.init(repo_path)
            return "Repository initialized successfully."
        except Exception as e:
            return f"Error initializing repository: {str(e)}"


def DeepResearch(topic: str, output_md_file: str, api_key: str) -> dict:
    result = {"topic": topic, "sources": [], "report_md": "", "status": "error", "error": None}
    if not topic:
        result["error"] = "Empty topic provided."
        return result
    if not api_key:
        result["error"] = "API key is required."
        return result

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        result["error"] = f"Failed to initialize GenAI client: {e}"
        return result

    try:
        google_search_tool = Tool(google_search=GoogleSearch())
        config = GenerateContentConfig(tools=[google_search_tool])

        prompt = (
            f"{DP_R_SYSTEM_PROMPT}\n\n"
            f"Research topic: **{topic}**.\n"
            f"Gather relevant information from recent, credible sources using Google Search grounding.\n"
            f"Then produce a detailed markdown report following the output format."
        )

        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
    except Exception as e:
        result["error"] = f"Error calling generate_content: {e}"
        return result

    try:
        candidates = getattr(resp, "candidates", None)
        if not candidates or len(candidates) == 0:
            raise ValueError("No candidates returned from model.")
        candidate = candidates[0]
        # Support both .content.text and .content.parts[0].text shapes
        report_md = ""
        content = getattr(candidate, "content", None)
        if content is None:
            raise ValueError("No content in candidate.")
        parts = getattr(content, "parts", None)
        if parts and len(parts) > 0 and hasattr(parts[0], "text"):
            report_md = parts[0].text
        else:
            report_md = getattr(content, "text", "") or ""
        result["report_md"] = report_md
    except Exception as e:
        result["error"] = f"Error extracting report text: {e}"
        return result

    try:
        with open(output_md_file, "w", encoding="utf-8") as f:
            f.write(result["report_md"])
    except Exception as e:
        # Don't fail completely if writing file fails; return report in memory with an error note.
        result["error"] = f"Report generated but failed to write to file '{output_md_file}': {e}"
        # still attempt to extract sources below and return report in memory
    try:
        sources = []
        grounding = getattr(candidate, "grounding_metadata", None)
        if grounding:
            grounding_chunks = getattr(grounding, "grounding_chunks", []) or []
            for chunk in grounding_chunks:
                web = getattr(chunk, "web", None)
                if web:
                    sources.append({
                        "uri": getattr(web, "uri", ""),
                        "title": getattr(web, "title", "")
                    })
        result["sources"] = sources
    except Exception:
        # Non-fatal: if extraction fails, leave sources empty and proceed
        pass

    # If there was only a file write error, keep status partial; otherwise mark success
    if result["error"] is None:
        result["status"] = "ok"
    elif result["report_md"]:
        result["status"] = "partial"
    else:
        result["status"] = "error"

    return result

# Static function
def download_file(url: str, save_to: str) -> bool:
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_to, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def download_image(url: str) -> str:
    try:
        if platform.system() == "Windows":
            save_to = "C:\\Temp\\downloaded_image.jpg"
        else:
            save_to = "/tmp/downloaded_image.jpg"
        if download_file(url, save_to):
            return save_to
        return "Error downloading image."
    except Exception as e:
        return f"Error downloading image: {str(e)}"