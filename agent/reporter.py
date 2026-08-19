# agent/reporter.py
import datetime
import os
import subprocess

from openai import OpenAI  # Or your framework's custom wrapper


def get_git_metadata():
    """Extracts recent activity directly from the repository environment."""
    try:
        commits = subprocess.check_output(
            ["git", "log", "--since=24 hours ago", "--oneline"]
        ).decode("utf-8")
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1", "HEAD"]
        ).decode("utf-8")[:2000] # Cap to prevent context blowing up
        return commits, diff
    except (OSError, subprocess.CalledProcessError):
        return "No recent commits found or shallow clone.", ""

def generate_daily_log():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    commits, diff = get_git_metadata()
    date_str = datetime.datetime.now(datetime.timezone.utc).date().strftime("%Y-%m-%d")
    
    prompt = f"""
    You are an autonomous MLOps & System Hygiene Agent responsible for maintaining HelixAgent.
    Analyze the following repository changes from the last 24 hours and write a professional system summary for today's log entry.
    
    Date: {date_str}
    Recent Commits:
    {commits}
    
    Recent Code Changes snippet:
    {diff}
    
    Generate a markdown section containing:
    1. **System Health & Metrics**: Summary of code state, stability adjustments, or optimization changes.
    2. **Agent Execution Highlights**: Deduce which components (API, Agent core, Infrastructure) were affected and summarize progress.
    3. **Automated TODOs**: List technical debt or testing gaps discovered from the diff/commits.
    
    Format output cleanly as markdown. Do not include markdown block wrapping (```markdown).
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    
    log_content = response.choices[0].message.content
    
    # Prepend or Append to DAILYLOG.md
    log_file = "DAILYLOG.md"
    existing_content = ""
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            existing_content = f.read()
            
    header = "# HelixAgent Autonomous Logs\n\n" if not existing_content else ""
    
    new_entry = f"## Log Entry: {date_str}\n\n{log_content}\n\n---\n\n"
    
    with open(log_file, "w") as f:
        f.write(header + new_entry + existing_content.replace("# HelixAgent Autonomous Logs\n\n", ""))

if __name__ == "__main__":
    generate_daily_log()
