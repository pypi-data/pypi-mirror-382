TEMPLATE_BASIC = '''from stagehand import Stagehand
import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

async def main():
    """Basic Stagehand browser automation example."""

    # Check all the configurations in StagehandConfig
    stagehand = Stagehand(
        env="LOCAL", # or "BROWSERBASE"
        verbose=1, # 0: silent, 1: info, 2: debug
        model_name="gpt-4.1",
        model_api_key=os.getenv("OPENAI_API_KEY"),
    )
    await stagehand.init()

    page = stagehand.page
    await page.goto("https://docs.stagehand.dev")
    result = await page.extract("In a few words, what is Stagehand?")
    print()
    print(result)
    print()

    await page.act("click on models")
    await page.act({
        "method": "click",
        "selector": "/html/body[1]/div[2]/div[2]/div[3]/div[2]/div[2]/a[1]",
        "description": "the model evaluation card",
        "args": []
    })
    elements = await page.observe("find the graph with the list of most accurate models")
    print()
    print(elements)
    print()

    class Model(BaseModel):
        name: str
        provider: str
        accuracy: float
        
    extraction = await page.extract(
        "the most accurate model",
        schema=Model
    )
    print()
    print(extraction)
    print()
if __name__ == "__main__":
    asyncio.run(main())

'''

TEMPLATE_REQUIREMENTS = '''stagehand
python-dotenv
'''

TEMPLATE_ENV = '''# Add your environment variables here
# BROWSERBASE_API_KEY=your_api_key_here
# BROWSERBASE_PROJECT_ID=your_project_id_here
# Add your LLM key
# OPENAI_API_KEY=your_api_key_here
# ANTHROPIC=your_api_key_here
# GOOGLE_API_KEY=your_api_key_here
'''

TEMPLATE_README = '''# {project_name}

A Stagehand browser automation project.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your environment variables in `.env`:
```bash
BROWSERBASE_API_KEY=your_api_key_here
BROWSERBASE_PROJECT_ID=your_project_id_here
```

3. Run the project:
```bash
python main.py
```

## About Stagehand

Stagehand is a Python library for browser automation built on Playwright. Learn more at:
- [Stagehand Documentation](https://github.com/browserbase/stagehand)
- [Browserbase](https://browserbase.com)
'''

TEMPLATE_GITIGNORE = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log
'''