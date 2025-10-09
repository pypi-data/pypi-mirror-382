<h1 align="center">
  <a href="https://www.statamcp.com">
    <img src="https://example-data.statamcp.com/logo_with_name.jpg" alt="logo" width="300"/>
  </a>
</h1>

<h1 align="center">Stata-MCP</h1>

<p align="center"> Let LLM help you achieve your regression analysis with Stata ✨</p>

[![en](https://img.shields.io/badge/lang-English-red.svg)](README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](source/docs/README/cn/README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](source/docs/README/fr/README.md)
[![sp](https://img.shields.io/badge/Idioma-Español-green.svg)](source/docs/README/sp/README.md)
[![PyPI version](https://img.shields.io/pypi/v/stata-mcp.svg)](https://pypi.org/project/stata-mcp/)
[![PyPI Downloads](https://static.pepy.tech/badge/stata-mcp)](https://pepy.tech/projects/stata-mcp)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/SepineTam/stata-mcp)

---
**News**: Now you can use Stata-MCP with agent mode, more information [here](./agent_examples/README.md).

Finding our **newest research**? Click [here](source/reports/README.md) or visit [reports website](https://www.statamcp.com/reports).

> Looking for others?
>
> - [Trace DID](https://github.com/asjadnaqvi/DiD): If you want to fetch the newest information about DID (Difference-in-Difference), click [here](https://asjadnaqvi.github.io/DiD/). Now there is a Chinese translation by [Sepine Tam](https://github.com/sepine) and [StataMCP-Team](https://github.com/statamcp-team) 🎉
> - Jupyter Lab Usage (Important: Stata 17+) [here](source/docs/JupyterStata.md)
> - [NBER-MCP](https://github.com/sepinetam/NBER-MCP) & [AER-MCP](https://github.com/sepinetam/AER-MCP) 🔧 under construction
> - [Econometrics-Agent](https://github.com/FromCSUZhou/Econometrics-Agent)
> - [TexIV](https://github.com/sepinetam/TexIV): A machine learning-driven framework that transforms text data into usable variables for empirical research using advanced NLP and ML techniques
> - A VScode or Cursor integrated [here](https://github.com/hanlulong/stata-mcp). Confused it? 💡 [Difference](source/docs/Difference.md)

## 💡 Quick Start
### Agent Mode
The details of agent mode find [here](agent_examples/README.md).

```bash
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

uv sync
uv pip install -e .

stata-mcp --version  # for test whether stata-mcp is installed successfully.
stata-mcp --agent  # now you have enjoy your stata-mcp agent mode.
```

or you can directly use it with `uvx`:
```bash
uvx stata-mcp --version  # for test whether it could be used on your computer.
uvx stata-mcp --agent
```

You can edit the task in `agent_examples/openai/main.py` for variable `model_instructions` and `task_message`, [click me](agent_examples/openai/main.py) #L37 and #L68

### AI Chat-Bot Client Mode
> Standard config requires: please make sure the stata is installed at the default path, and the stata cli (for macOS and Linux) exists.

The standard config json as follows, you can DIY your config via add envs.
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": [
        "stata-mcp"
      ]
    }
  }
}
```

For more detailed usage information, visit the [Usage guide](source/docs/Usages/Usage.md). 

And some advanced usage, visit the [Advanced guide](source/docs/Usages/Advanced.md)

### Prerequisites
- [uv](https://github.com/astral-sh/uv) - Package installer and virtual environment manager
- Claude, Cline, ChatWise, or other LLM service
- Stata License
- Your API-KEY from LLM

> Notes:
> 1. If you are located in China, a short uv usage document you can find [here](source/docs/ChinaUsers/uv.md).
> 2. Claude is the best choice for Stata-MCP, for Chinese, I recommend to use DeepSeek as your model provider as it is cheap and powerful, also the score is highest in China provider, if you are increased in it, visit the report [How to use StataMCP improve your social science research](https://reports.statamcp.com/202509/how_to_use_statamcp_improve_your_social_science_research).

### Installation
For the new version, you don't need to install the `stata-mcp` package again, you can just use the following command to check whether your computer can use stata-mcp.
```bash
uvx stata-mcp --usable
uvx stata-mcp --version
```

If you want to use it locally, you can install it via pip or download the source code.

**Download via pip**
```bash
pip install stata-mcp
```

**Download source code and compile**
```bash
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

uv build
```
Then you can find the compiled `stata-mcp` binary in the `dist` directory. You can use it directly or add it to your PATH.

For example:
```bash
uvx /path/to/your/whl/stata_mcp-1.7.4-py3-non-any.whl  # here is the wheel file name, you can change it to your version
```

## 📝 Documentation
- For more detailed usage information, visit the [Usage guide](source/docs/Usages/Usage.md).
- Advanced Usage, visit the [Advanced](source/docs/Usages/Advanced.md)
- Some questions, visit the [Questions](source/docs/Usages/Questions.md)
- Difference with [Stata-MCP@hanlulong](https://github.com/hanlulong/stata-mcp), visit the [Difference](source/docs/Difference.md)

## 💡 Questions
- [Cherry Studio 32000 wrong](source/docs/Usages/Questions.md#cherry-studio-32000-wrong)
- [Cherry Studio 32000 error](source/docs/Usages/Questions.md#cherry-studio-32000-error)
- [Windows Support](source/docs/Usages/Questions.md#windows-supports)
- [Network Errors When Running Stata-MCP](source/docs/Usages/Questions.md#network-errors-when-running-stata-mcp)

## 🚀 Roadmap
- [x] macOS support
- [x] Windows support
- [ ] Additional LLM integrations
- [ ] Performance optimizations

## ⚠️ Disclaimer
This project is for research purposes only. I am not responsible for any damage caused by this project. Please ensure you have proper licensing to use Stata.

For more information, refer to the [Statement](source/docs/Rights/Statement.md).

## 🐛 Report Issues
If you encounter any bugs or have feature requests, please [open an issue](https://github.com/sepinetam/stata-mcp/issues/new).

## 📄 License
[Apache License 2.0](LICENSE)

## 📚 Citation
If you use Stata-MCP in your research, please cite this repository using one of the following formats:

### BibTeX
```bibtex
@software{sepinetam2025stata,
  author = {Song Tan},
  title = {Stata-MCP: Let LLM help you achieve your regression analysis with Stata},
  year = {2025},
  url = {https://github.com/sepinetam/stata-mcp},
  version = {1.7.4}
}
```

### APA
```
Song Tan. (2025). Stata-MCP: Let LLM help you achieve your regression analysis with Stata (Version 1.7.4) [Computer software]. https://github.com/sepinetam/stata-mcp
```

### Chicago
```
Song Tan. 2025. "Stata-MCP: Let LLM help you achieve your regression analysis with Stata." Version 1.7.4. https://github.com/sepinetam/stata-mcp.
```

## 📬 Contact
Email: [sepinetam@gmail.com](mailto:sepinetam@gmail.com)

Or contribute directly by submitting a [Pull Request](https://github.com/sepinetam/stata-mcp/pulls)! We welcome contributions of all kinds, from bug fixes to new features.

## ❤️ Acknowledgements
The author sincerely thanks the Stata official team for their support and the Stata License for authorizing the test development.

## ✨ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)

