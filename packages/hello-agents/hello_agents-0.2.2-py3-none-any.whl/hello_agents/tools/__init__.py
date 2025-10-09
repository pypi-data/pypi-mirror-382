"""工具系统"""

from .base import Tool, ToolParameter
from .registry import ToolRegistry, global_registry

# 内置工具
from .builtin.search import SearchTool
from .builtin.calculator import CalculatorTool
from .builtin.memory_tool import MemoryTool
from .builtin.rag_tool import RAGTool

# 协议工具
from .builtin.protocol_tools import MCPTool, A2ATool, ANPTool

# 高级功能
from .chain import ToolChain, ToolChainManager, create_research_chain, create_simple_chain
from .async_executor import AsyncToolExecutor, run_parallel_tools, run_batch_tool, run_parallel_tools_sync, run_batch_tool_sync

__all__ = [
    # 基础工具系统
    "Tool",
    "ToolParameter",
    "ToolRegistry",
    "global_registry",

    # 内置工具
    "SearchTool",
    "CalculatorTool",
    "MemoryTool",
    "RAGTool",

    # 协议工具
    "MCPTool",
    "A2ATool",
    "ANPTool",

    # 工具链功能
    "ToolChain",
    "ToolChainManager",
    "create_research_chain",
    "create_simple_chain",

    # 异步执行功能
    "AsyncToolExecutor",
    "run_parallel_tools",
    "run_batch_tool",
    "run_parallel_tools_sync",
    "run_batch_tool_sync",
]
