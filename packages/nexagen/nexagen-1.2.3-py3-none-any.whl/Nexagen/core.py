import json
import subprocess
import asyncio
import os
import sys
import traceback
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from .utils import (
    call_llm,
    generate_agent_card
)
import time
from .prompt import generate_agent_cards_prompt

# 模板环境设置
TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def create_project(project_path: Path):
    """Create new project structure"""
    project_path.mkdir(exist_ok=True)
    (project_path / "__init__.py").touch()
    (project_path / "mcp_agents").mkdir(exist_ok=True)
    (project_path / "mcp.json").write_text(json.dumps({}), encoding='utf-8')
    env_data=open(f"{Path(__file__).parent}/.env","r",encoding="utf-8").read()
    (project_path / ".env").write_text(env_data, encoding='utf-8')


def build_project(project_path: Path):
    """Build the Nexagen system"""
    try:
        print("Starting Nexagen system build...")
        load_dotenv(project_path / ".env")

        # 1. 安装依赖
        print("Installing dependencies...")
        subprocess.run(["uv", "pip", "install", "a2a-sdk", "mcp", "uvicorn", "httpx", "jinja2", "python-dotenv"])

        try:
            #生成auto_find_mcp_agents
            try:
                print("Generating agent executor...")
                executor_template = env.get_template("auto_find_mcp_agents.py.j2")
                rendered_content = executor_template.render()
                (project_path / "auto_find_mcp_agents.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering auto_find_mcp_agents template: {e}")
                #traceback.print_exc()
                #raise
            #执行auto_find_mcp_agents
            os.system("python auto_find_mcp_agents.py")
            os.remove("auto_find_mcp_agents.py")
            # 2. 生成智能体卡片
            print("Generating agent cards...")

            (project_path / "agent_cards").mkdir(exist_ok=True)
            agent_cards = []

            # 读取 mcp_cards
            with open(f"{project_path}/mcp_agents/mcp_cards.json", encoding="utf-8") as fh:
                mcp_cards_data = json.load(fh)

            # 分批处理每个 agent，避免一次性发送太多数据导致超时
            for agent_name, agent_data in mcp_cards_data.items():
                try:
                    print(f"Processing agent: {agent_name}")
                    
                    # 为单个 agent 生成卡片
                    single_agent_data = {agent_name: agent_data}
                    prompt = f"{generate_agent_cards_prompt}\n{json.dumps(single_agent_data, indent=2, ensure_ascii=False)}"
                    
                    # 调用 LLM 生成单个 agent 的卡片
                    agent_response = call_llm(prompt)
                    agent_info = json.loads(agent_response.replace("```json", "").replace("```", ""))
                    
                    # 如果返回的是列表，取第一个元素
                    if isinstance(agent_info, list) and len(agent_info) > 0:
                        agent_info = agent_info[0]
                    
                    # 生成 agent card
                    card = generate_agent_card(
                        name=agent_info["name"],
                        description=agent_info["description"],
                        tools=agent_info["skills"],
                        url=agent_info["url"],
                        capabilities=agent_info["capabilities"],
                        default_input_modes=agent_info["defaultInputModes"],
                        default_output_modes=agent_info["defaultOutputModes"]
                    )

                    card_path = project_path / "agent_cards" / f"{agent_name}.json"
                    card_path.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding='utf-8')
                    agent_cards.append(str(card_path.relative_to(project_path)))
                    
                    print(f"  ✓ Generated card for {agent_name}")
                    
                    # 添加延迟避免 API 限流
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ✗ Error processing agent {agent_name}: {e}")
                    print(f"    Skipping {agent_name}...")
                    continue
            
            print(f"Build agent cards ok. Generated {len(agent_cards)} cards.")
            # 3. 生成调度Agent
            try:
                print("Generating orchestrator agent...")

                #orchestrator_template = env.get_template("orchestrator_agent.py.j2")
                #rendered_content = orchestrator_template.render()
                (project_path / "orchestrator_agent.py").write_text((TEMPLATES_DIR/"orchestrator_agent.py.j2").read_text(encoding='utf-8'), encoding='utf-8')
            except Exception as e:
                print(f"Error rendering orchestrator template: {e}")
                #traceback.print_exc()
                #raise

            # 4. 生成MCP客户端
            try:
                print("Generating MCP client...")
                mcp_client_template = env.get_template("mcp_client.py.j2")
                rendered_content = mcp_client_template.render()
                (project_path / "mcp_client.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering MCP client template: {e}")
                #traceback.print_exc()
                #raise

            # 5. 生成Agent执行器
            try:
                print("Generating agent executor...")
                executor_template = env.get_template("agent_executor.py.j2")
                rendered_content = executor_template.render()
                (project_path / "agent_executor.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering agent executor template: {e}")
                #traceback.print_exc()
                #raise
            #print()
            # 6. 生成Agent pipeline
            try:
                print("Generating Agent pipeline...")
                pipeline_template = env.get_template("pipeline.py.j2")
                rendered_content = pipeline_template.render()
                (project_path / "pipeline.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering pipeline template: {e}")
                # traceback.print_exc()
                # raise
            #print()
            # 7. 生成Demo
            try:
                print("Generating Agent Demo...")
                test_demo_template = env.get_template("test_demo.py.j2")
                rendered_content = test_demo_template.render()
                (project_path / "test_demo.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering test_demo template: {e}")
                # traceback.print_exc()
                # raise

        except Exception as err:
            print(err)

    except Exception as e:
        print(f"Build failed: {e}")
        #traceback.print_exc()
        #sys.exit(1)


def run_project(project_path: Path):
    """Run the Nexagen system"""
    try:
        print("Starting Nexagen system...")
        try:
            # 1. 运行A2A客户端
            print("Starting Nexagen client...")
            os.system("python test_demo.py")
        except Exception as err:
            print(err)

    except Exception as e:
        print(f"Run failed: {e}")
        #traceback.print_exc()
        #sys.exit(1)


def magic_wrap_as_mcp(project_path: Path):
    """将整个多智能体系统封装为单个 MCP Agent"""
    try:
        print("\n🪄 Starting Nexagen Magic - Wrapping as MCP Agent...")
        print("=" * 60)
        
        # 检查必要的文件是否存在
        required_files = [
            project_path / "orchestrator_agent.py",
            project_path / "agent_executor.py",
            project_path / "mcp_agents" / "mcp_cards.json",
            project_path / ".env"
        ]
        
        missing_files = [f for f in required_files if not f.exists()]
        if missing_files:
            print("\n❌ Error: Missing required files. Please run 'nexagen build' first.")
            print("Missing files:")
            for f in missing_files:
                print(f"  - {f}")
            return
        
        print("\n✓ All required files found")
        
        # 1. 生成 MCP server 文件
        print("\n📝 Generating MCP server...")
        try:
            mcp_server_template = env.get_template("mcp_server.py.j2")
            rendered_content = mcp_server_template.render()
            (project_path / "mcp_server.py").write_text(rendered_content, encoding='utf-8')
            print("✓ MCP server generated: mcp_server.py")
        except Exception as e:
            print(f"Error generating MCP server: {e}")
            raise
        
        # 2. 生成 pyproject.toml
        print("\n📝 Generating pyproject.toml...")
        try:
            pyproject_template = env.get_template("pyproject.toml.j2")
            rendered_content = pyproject_template.render()
            (project_path / "pyproject.toml").write_text(rendered_content, encoding='utf-8')
            print("✓ pyproject.toml generated")
        except Exception as e:
            print(f"Error generating pyproject.toml: {e}")
            raise
        
        # 3. 安装依赖
        print("\n📦 Installing MCP dependencies...")
        try:
            subprocess.run(
                ["uv", "pip", "install", "mcp[cli]", "python-dotenv", "requests", "jinja2"],
                check=True,
                capture_output=True
            )
            print("✓ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not install dependencies: {e}")
            print("You may need to install them manually: uv pip install mcp[cli] python-dotenv requests jinja2")
        
        # 4. 生成使用说明
        print("\n📄 Generating usage instructions...")
        usage_doc = f"""# Nexagen MCP Agent

## 🎉 Your multi-agent system has been wrapped as a single MCP Agent!

### What was created:
- `mcp_server.py`: The MCP server that wraps all your agents
- `pyproject.toml`: Project configuration for the MCP agent

### How to use:

#### 1. Start the MCP server locally:
```bash
uv run mcp_server.py
```

#### 2. Add to Claude Desktop:
Add this to your Claude Desktop MCP configuration:

```json
{{
  "mcpServers": {{
    "nexagen": {{
      "command": "uv",
      "args": [
        "--directory",
        "{project_path.absolute()}",
        "run",
        "mcp_server.py"
      ]
    }}
  }}
}}
```

#### 3. Available Tools:

The Nexagen MCP agent exposes:

- **nexagen_route**: 🎯 Smart routing - automatically splits complex tasks and dispatches to appropriate agents
- **list_available_agents**: 📋 Lists all available internal agents and their capabilities
- **All internal agent tools**: Each tool from your internal agents is exposed with namespace (e.g., `chart_draw_chart`)

#### 4. Example Usage in Claude:

"Please use nexagen to analyze Q1 sales data [120, 132, 101, 134, 90, 230] and create a visualization chart"

Claude will automatically:
1. Call the `nexagen_route` tool
2. Nexagen splits the task
3. Selects the right agents (e.g., chart agent)
4. Generates parameters
5. Executes and returns results

### Architecture:

```
Claude Desktop
    ↓
Nexagen MCP Agent (mcp_server.py)
    ↓
Orchestrator Agent
    ↓
Internal Agents (chart, data, etc.)
```

### Notes:
- All internal agents remain unchanged
- The MCP layer provides intelligent routing
- You can still call specific agent tools directly if needed
- Prompts and resources from internal agents are also exposed

### Troubleshooting:

If you encounter issues:
1. Ensure all dependencies are installed: `uv pip install mcp[cli] python-dotenv requests jinja2`
2. Check that your `.env` file has the correct API_KEY and BASE_URL
3. Verify that all internal agents are properly configured in `mcp.json`
4. Test the server locally first: `uv run mcp_server.py`

For more information, visit: https://github.com/taoxiang-org/nexagen
"""
        
        (project_path / "NEXAGEN_MCP_USAGE.md").write_text(usage_doc, encoding='utf-8')
        print("✓ Usage instructions saved: NEXAGEN_MCP_USAGE.md")
        
        # 5. 统计信息
        print("\n" + "=" * 60)
        print("📊 Nexagen MCP Agent Summary:")
        print("=" * 60)
        
        # 加载 agent 信息
        mcp_cards_path = project_path / "mcp_agents" / "mcp_cards.json"
        with open(mcp_cards_path, "r", encoding="utf-8") as f:
            mcp_cards = json.load(f)
        
        total_tools = 0
        total_prompts = 0
        total_resources = 0
        
        for agent_name, agent_info in mcp_cards.items():
            tools = len(agent_info.get("tools", []))
            prompts = len(agent_info.get("prompts", []))
            resources = len(agent_info.get("resources", []))
            
            total_tools += tools
            total_prompts += prompts
            total_resources += resources
            
            print(f"\n  Agent: {agent_name}")
            print(f"    Tools: {tools}")
            print(f"    Prompts: {prompts}")
            print(f"    Resources: {resources}")
        
        print("\n" + "-" * 60)
        print(f"  Total Internal Agents: {len(mcp_cards)}")
        print(f"  Total Tools Exposed: {total_tools + 2}")  # +2 for nexagen_route and list_available_agents
        print(f"  Total Prompts: {total_prompts + 1}")  # +1 for nexagen_example
        print(f"  Total Resources: {total_resources}")
        print("=" * 60)
        
        print("\n✨ Magic complete! Your multi-agent system is now a single MCP agent.")
        print("\n📖 Read NEXAGEN_MCP_USAGE.md for detailed usage instructions.")
        print("\n🚀 Quick start: uv run mcp_server.py\n")
        
    except Exception as e:
        print(f"\n❌ Magic failed: {e}")
        import traceback
        traceback.print_exc()