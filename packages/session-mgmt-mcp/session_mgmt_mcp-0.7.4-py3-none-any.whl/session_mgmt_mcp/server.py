#!/usr/bin/env python3
"""Claude Session Management MCP Server - FastMCP Version.

A dedicated MCP server that provides session management functionality
including initialization, checkpoints, and cleanup across all projects.

This server can be included in any project's .mcp.json file to provide
automatic access to /session-init, /session-checkpoint,
and /session-end slash commands.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import warnings
from contextlib import asynccontextmanager, suppress
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

# Suppress transformers warnings about PyTorch/TensorFlow for cleaner CLI output
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
warnings.filterwarnings("ignore", message=".*PyTorch.*TensorFlow.*Flax.*")

try:
    import tomli
except ImportError:
    tomli = None  # type: ignore[assignment]


# Configure structured logging
class SessionLogger:
    """Structured logging for session management with context."""

    def __init__(self, log_dir: Path) -> None:
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = (
            log_dir / f"session_management_{datetime.now().strftime('%Y%m%d')}.log"
        )

        # Configure logger
        self.logger = logging.getLogger("session_management")
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            # File handler with structured format
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.INFO)

            # Console handler for errors
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.ERROR)

            # Structured formatter
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def debug(self, message: str, **context: Any) -> None:
        """Log debug with optional context."""
        if context:
            message = f"{message} | Context: {json.dumps(context)}"
        self.logger.debug(message)

    def info(self, message: str, **context: Any) -> None:
        """Log info with optional context."""
        if context:
            message = f"{message} | Context: {json.dumps(context)}"
        self.logger.info(message)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning with optional context."""
        if context:
            message = f"{message} | Context: {json.dumps(context)}"
        self.logger.warning(message)

    def error(self, message: str, **context: Any) -> None:
        """Log error with optional context."""
        if context:
            message = f"{message} | Context: {json.dumps(context)}"
        self.logger.error(message)

    def exception(self, message: str, **context: Any) -> None:
        """Log exception with optional context."""
        if context:
            message = f"{message} | Context: {json.dumps(context)}"
        self.logger.exception(message)


# Initialize logger
claude_dir = Path.home() / ".claude"
session_logger = SessionLogger(claude_dir / "logs")

try:
    from fastmcp import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    # Check if we're in a test environment
    if "pytest" in sys.modules or "test" in sys.argv[0].lower():
        print(
            "Warning: FastMCP not available in test environment, using mock",
            file=sys.stderr,
        )

        # Create a minimal mock FastMCP for testing
        class MockFastMCP:
            def __init__(self, name: str) -> None:
                self.name = name
                self.tools: dict[str, Any] = {}
                self.prompts: dict[str, Any] = {}

            def tool(
                self, *args: Any, **kwargs: Any
            ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
                def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                    return func

                return decorator

            def prompt(
                self, *args: Any, **kwargs: Any
            ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
                def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                    return func

                return decorator

            def run(self, *args: Any, **kwargs: Any) -> None:
                pass

        FastMCP = MockFastMCP  # type: ignore[no-redef]
        MCP_AVAILABLE = False
    else:
        print("FastMCP not available. Install with: uv add fastmcp", file=sys.stderr)
        sys.exit(1)

# Import session management core
try:
    from session_mgmt_mcp.core.session_manager import SessionLifecycleManager

    SESSION_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    print(f"Session management core import failed: {e}", file=sys.stderr)
    SESSION_MANAGEMENT_AVAILABLE = False

# Import reflection tools
try:
    from session_mgmt_mcp.reflection_tools import (
        ReflectionDatabase,
        get_current_project,
        get_reflection_database,
    )

    REFLECTION_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Reflection tools import failed: {e}", file=sys.stderr)
    REFLECTION_TOOLS_AVAILABLE = False

# Import enhanced search tools
try:
    # EnhancedSearchEngine will be imported when needed
    import session_mgmt_mcp.search_enhanced

    ENHANCED_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced search import failed: {e}", file=sys.stderr)
    ENHANCED_SEARCH_AVAILABLE = False

# Import utility functions
try:
    from session_mgmt_mcp.tools.search_tools import _optimize_search_results_impl
    from session_mgmt_mcp.utils.format_utils import _format_session_statistics

    UTILITY_FUNCTIONS_AVAILABLE = True
except ImportError as e:
    print(f"Utility functions import failed: {e}", file=sys.stderr)
    UTILITY_FUNCTIONS_AVAILABLE = False

# Global feature instances (initialized on-demand)
multi_project_coordinator: Any = None
advanced_search_engine: Any = None
app_config: Any = None
current_project: str | None = None

# Import multi-project coordination tools
try:
    from session_mgmt_mcp.multi_project_coordinator import MultiProjectCoordinator

    MULTI_PROJECT_AVAILABLE = True
except ImportError as e:
    print(f"Multi-project coordinator import failed: {e}", file=sys.stderr)
    MULTI_PROJECT_AVAILABLE = False

# Import advanced search engine
try:
    from session_mgmt_mcp.advanced_search import AdvancedSearchEngine

    ADVANCED_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Advanced search engine import failed: {e}", file=sys.stderr)
    ADVANCED_SEARCH_AVAILABLE = False

# Import configuration management
try:
    from session_mgmt_mcp.config import get_config

    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Configuration management import failed: {e}", file=sys.stderr)
    CONFIG_AVAILABLE = False

# Import auto-context loading tools
try:
    # AutoContextLoader will be imported when needed
    import session_mgmt_mcp.context_manager

    AUTO_CONTEXT_AVAILABLE = True
except ImportError as e:
    print(f"Auto-context loading import failed: {e}", file=sys.stderr)
    AUTO_CONTEXT_AVAILABLE = False

# Import memory optimization tools
try:
    # MemoryOptimizer will be imported when needed
    import session_mgmt_mcp.memory_optimizer

    MEMORY_OPTIMIZER_AVAILABLE = True
except ImportError as e:
    print(f"Memory optimizer import failed: {e}", file=sys.stderr)
    MEMORY_OPTIMIZER_AVAILABLE = False

# Import application monitoring tools
try:
    from session_mgmt_mcp.app_monitor import ApplicationMonitor

    APP_MONITOR_AVAILABLE = True
except ImportError as e:
    print(f"Application monitoring import failed: {e}", file=sys.stderr)
    APP_MONITOR_AVAILABLE = False

# Import LLM providers
try:
    from session_mgmt_mcp.llm_providers import LLMManager

    LLM_PROVIDERS_AVAILABLE = True
except ImportError as e:
    print(f"LLM providers import failed: {e}", file=sys.stderr)
    LLM_PROVIDERS_AVAILABLE = False

# Import serverless mode
try:
    from session_mgmt_mcp.serverless_mode import (
        ServerlessConfigManager,
        ServerlessSessionManager,
    )

    SERVERLESS_MODE_AVAILABLE = True
except ImportError as e:
    print(f"Serverless mode import failed: {e}", file=sys.stderr)
    SERVERLESS_MODE_AVAILABLE = False

# Import Crackerjack integration tools
try:
    # CrackerjackIntegration will be imported when needed
    import session_mgmt_mcp.crackerjack_integration

    CRACKERJACK_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"Crackerjack integration import failed: {e}", file=sys.stderr)
    CRACKERJACK_INTEGRATION_AVAILABLE = False


class SessionPermissionsManager:
    """Manages session permissions to avoid repeated prompts for trusted operations."""

    _instance: SessionPermissionsManager | None = None
    _session_id: str | None = None
    _initialized: bool = False

    def __new__(cls, claude_dir: Path) -> Self:  # type: ignore[misc]
        """Singleton pattern to ensure consistent session ID across tool calls."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        # Type checker knows this is Self from the annotation above
        return cls._instance  # type: ignore[return-value]

    def __init__(self, claude_dir: Path) -> None:
        if self._initialized:
            return
        self.claude_dir = claude_dir
        self.permissions_file = claude_dir / "sessions" / "trusted_permissions.json"
        self.permissions_file.parent.mkdir(exist_ok=True)
        self.trusted_operations: set[str] = set()
        # Use class-level session ID to persist across instances
        if SessionPermissionsManager._session_id is None:
            SessionPermissionsManager._session_id = self._generate_session_id()
        self.session_id = SessionPermissionsManager._session_id
        self._load_permissions()
        self._initialized = True

    def _generate_session_id(self) -> str:
        """Generate unique session ID based on current time and working directory."""
        session_data = f"{datetime.now().isoformat()}_{Path.cwd()}"
        return hashlib.md5(session_data.encode(), usedforsecurity=False).hexdigest()[
            :12
        ]

    def _load_permissions(self) -> None:
        """Load previously granted permissions."""
        if self.permissions_file.exists():
            try:
                with self.permissions_file.open() as f:
                    data = json.load(f)
                    self.trusted_operations.update(data.get("trusted_operations", []))
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_permissions(self) -> None:
        """Save current trusted permissions."""
        data = {
            "trusted_operations": list(self.trusted_operations),
            "last_updated": datetime.now().isoformat(),
            "session_id": self.session_id,
        }
        with self.permissions_file.open("w") as f:
            json.dump(data, f, indent=2)

    def is_operation_trusted(self, operation: str) -> bool:
        """Check if an operation is already trusted."""
        return operation in self.trusted_operations

    def trust_operation(self, operation: str, description: str = "") -> None:
        """Mark an operation as trusted to avoid future prompts."""
        self.trusted_operations.add(operation)
        self._save_permissions()

    def get_permission_status(self) -> dict[str, Any]:
        """Get current permission status."""
        return {
            "session_id": self.session_id,
            "trusted_operations_count": len(self.trusted_operations),
            "trusted_operations": list(self.trusted_operations),
            "permissions_file": str(self.permissions_file),
        }

    def revoke_all_permissions(self) -> None:
        """Revoke all trusted permissions (for security reset)."""
        self.trusted_operations.clear()
        if self.permissions_file.exists():
            self.permissions_file.unlink()

    # Common trusted operations
    TRUSTED_UV_OPERATIONS = "uv_package_management"
    TRUSTED_GIT_OPERATIONS = "git_repository_access"
    TRUSTED_FILE_OPERATIONS = "project_file_access"
    TRUSTED_SUBPROCESS_OPERATIONS = "subprocess_execution"
    TRUSTED_NETWORK_OPERATIONS = "network_access"
    # TRUSTED_WORKSPACE_OPERATIONS removed - no longer needed


# Create global permissions manager instance
permissions_manager = SessionPermissionsManager(claude_dir)


# Utility Functions
def _detect_other_mcp_servers() -> dict[str, bool]:
    """Detect availability of other MCP servers by checking common paths and processes."""
    detected = {}

    # Check for crackerjack MCP server
    try:
        # Try to import crackerjack to see if it's available
        result = subprocess.run(
            ["crackerjack", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        detected["crackerjack"] = result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        detected["crackerjack"] = False

    return detected


def _generate_server_guidance(detected_servers: dict[str, bool]) -> list[str]:
    """Generate guidance messages based on detected servers."""
    guidance = []

    if detected_servers.get("crackerjack", False):
        guidance.extend(
            [
                "💡 CRACKERJACK INTEGRATION DETECTED:",
                "   Enhanced commands available for better development experience:",
                "   • Use /session-mgmt:crackerjack-run instead of /crackerjack:run",
                "   • Gets memory, analytics, and intelligent insights automatically",
                "   • View trends with /session-mgmt:crackerjack-history",
                "   • Analyze patterns with /session-mgmt:crackerjack-patterns",
            ],
        )

    return guidance


def _load_mcp_config() -> dict[str, Any]:
    """Load MCP server configuration from pyproject.toml."""
    # Look for pyproject.toml in the current project directory
    pyproject_path = Path.cwd() / "pyproject.toml"

    # If not found in cwd, look in parent directories (up to 3 levels)
    if not pyproject_path.exists():
        for parent in Path.cwd().parents[:3]:
            potential_path = parent / "pyproject.toml"
            if potential_path.exists():
                pyproject_path = potential_path
                break

    if not pyproject_path.exists() or not tomli:
        return {
            "http_port": 8678,
            "http_host": "127.0.0.1",
            "websocket_monitor_port": 8677,
            "http_enabled": False,
        }

    try:
        with pyproject_path.open("rb") as f:
            pyproject_data = tomli.load(f)

        session_config = pyproject_data.get("tool", {}).get("session-mgmt-mcp", {})

        return {
            "http_port": session_config.get("mcp_http_port", 8678),
            "http_host": session_config.get("mcp_http_host", "127.0.0.1"),
            "websocket_monitor_port": session_config.get(
                "websocket_monitor_port", 8677
            ),
            "http_enabled": session_config.get("http_enabled", False),
        }
    except Exception as e:
        print(
            f"Warning: Failed to load MCP config from pyproject.toml: {e}",
            file=sys.stderr,
        )
        return {
            "http_port": 8678,
            "http_host": "127.0.0.1",
            "websocket_monitor_port": 8677,
            "http_enabled": False,
        }


# Import required components for automatic lifecycle
from session_mgmt_mcp.core import SessionLifecycleManager
from session_mgmt_mcp.utils.git_operations import get_git_root, is_git_repository

# Global session manager for lifespan handlers
lifecycle_manager = SessionLifecycleManager()

# Global connection info for notification display
_connection_info = None


# Lifespan handler for automatic session management
@asynccontextmanager
async def session_lifecycle(app: Any) -> AsyncGenerator[None]:
    """Automatic session lifecycle for git repositories only."""
    current_dir = Path.cwd()

    # Only auto-initialize for git repositories
    if is_git_repository(current_dir):
        try:
            git_root = get_git_root(current_dir)
            session_logger.info(f"Git repository detected at {git_root}")

            # Run the same logic as the start tool but with connection notification
            result = await lifecycle_manager.initialize_session(str(current_dir))
            if result["success"]:
                session_logger.info("✅ Auto-initialized session for git repository")

                # Store connection info for display via tools
                global _connection_info
                _connection_info = {
                    "connected_at": "just connected",
                    "project": result["project"],
                    "quality_score": result["quality_score"],
                    "previous_session": result.get("previous_session"),
                    "recommendations": result["quality_data"].get(
                        "recommendations", []
                    ),
                }
            else:
                session_logger.warning(f"Auto-init failed: {result['error']}")
        except Exception as e:
            session_logger.warning(f"Auto-init failed (non-critical): {e}")
    else:
        # Not a git repository - no auto-initialization
        session_logger.debug("Non-git directory - skipping auto-initialization")

    yield  # Server runs normally

    # On disconnect - cleanup for git repos only
    if is_git_repository(current_dir):
        try:
            result = await lifecycle_manager.end_session()
            if result["success"]:
                session_logger.info("✅ Auto-ended session for git repository")
            else:
                session_logger.warning(f"Auto-cleanup failed: {result['error']}")
        except Exception as e:
            session_logger.warning(f"Auto-cleanup failed (non-critical): {e}")


# Load configuration and initialize FastMCP 2.0 server with lifespan
_mcp_config = _load_mcp_config()

# Initialize MCP server with lifespan
mcp = FastMCP("session-mgmt-mcp", lifespan=session_lifecycle)

# Register extracted tool modules following crackerjack architecture patterns
# Import session command definitions
from .tools import (
    register_crackerjack_tools,
    register_llm_tools,
    register_monitoring_tools,
    register_prompt_tools,
    register_search_tools,
    register_serverless_tools,
    register_session_tools,
    register_team_tools,
)

# Import utility functions
from .utils import (
    _analyze_quality_trend,
    _build_search_header,
    _cleanup_session_logs,
    _cleanup_temp_files,
    _cleanup_uv_cache,
    _extract_quality_scores,
    _format_efficiency_metrics,
    _format_no_data_message,
    _format_search_results,
    _format_statistics_header,
    _generate_quality_trend_recommendations,
    _get_intelligence_error_result,
    _get_time_based_recommendations,
    _optimize_git_repository,
    validate_claude_directory,
)

# Register all extracted tool modules
register_search_tools(mcp)
register_crackerjack_tools(mcp)
register_llm_tools(mcp)
register_monitoring_tools(mcp)
register_prompt_tools(mcp)
register_serverless_tools(mcp)
register_session_tools(mcp)
register_team_tools(mcp)

# Register slash commands as MCP prompts (not resources!)


async def auto_setup_git_working_directory() -> None:
    """Auto-detect and setup git working directory for enhanced DX."""
    try:
        # Get current working directory
        current_dir = Path.cwd()

        # Import git utilities
        from session_mgmt_mcp.utils.git_operations import (
            get_git_root,
            is_git_repository,
        )

        # Try to find git root from current directory
        git_root = None
        if is_git_repository(current_dir):
            git_root = get_git_root(current_dir)

        if git_root and git_root.exists():
            # Log the auto-setup action for Claude to see
            session_logger.info(f"🔧 Auto-detected git repository: {git_root}")
            session_logger.info(
                f"💡 Recommend: Use `mcp__git__git_set_working_dir` with path='{git_root}'"
            )

            # Also log to stderr for immediate visibility
            print(f"📍 Git repository detected: {git_root}", file=sys.stderr)
            print(
                f"💡 Tip: Auto-setup git working directory with: git_set_working_dir('{git_root}')",
                file=sys.stderr,
            )
        else:
            session_logger.debug(
                "No git repository detected in current directory - skipping auto-setup"
            )

    except Exception as e:
        # Graceful fallback - don't break server startup
        session_logger.debug(f"Git auto-setup failed (non-critical): {e}")


# Register init prompt
async def initialize_new_features() -> None:
    """Initialize multi-project coordination and advanced search features."""
    global multi_project_coordinator, advanced_search_engine, app_config

    # Auto-setup git working directory for enhanced DX
    await auto_setup_git_working_directory()

    # Load configuration
    if CONFIG_AVAILABLE:
        app_config = get_config()

    # Initialize reflection database for new features
    if REFLECTION_TOOLS_AVAILABLE:
        from contextlib import suppress

        with suppress(Exception):
            db = await get_reflection_database()

            # Initialize multi-project coordinator
            if MULTI_PROJECT_AVAILABLE:
                multi_project_coordinator = MultiProjectCoordinator(db)

            # Initialize advanced search engine
            if ADVANCED_SEARCH_AVAILABLE:
                advanced_search_engine = AdvancedSearchEngine(db)


async def analyze_project_context(project_dir: Path) -> dict[str, bool]:
    """Analyze project structure and context with enhanced error handling."""
    try:
        # Ensure project_dir exists and is accessible
        if not project_dir.exists():
            return {
                "python_project": False,
                "git_repo": False,
                "has_tests": False,
                "has_docs": False,
                "has_requirements": False,
                "has_uv_lock": False,
                "has_mcp_config": False,
            }

        return {
            "python_project": (project_dir / "pyproject.toml").exists(),
            "git_repo": (project_dir / ".git").exists(),
            "has_tests": any(project_dir.glob("test*"))
            or any(project_dir.glob("**/test*")),
            "has_docs": (project_dir / "README.md").exists()
            or any(project_dir.glob("docs/**")),
            "has_requirements": (project_dir / "requirements.txt").exists(),
            "has_uv_lock": (project_dir / "uv.lock").exists(),
            "has_mcp_config": (project_dir / ".mcp.json").exists(),
        }
    except (OSError, PermissionError) as e:
        # Log error but return safe defaults
        print(
            f"Warning: Could not analyze project context for {project_dir}: {e}",
            file=sys.stderr,
        )
        return {
            "python_project": False,
            "git_repo": False,
            "has_tests": False,
            "has_docs": False,
            "has_requirements": False,
            "has_uv_lock": False,
            "has_mcp_config": False,
        }


def _setup_claude_directory(output: list[str]) -> dict[str, Any]:
    """Setup Claude directory and return validation results."""
    output.append("\n📋 Phase 1: Claude directory setup...")

    claude_validation = validate_claude_directory()
    output.append("✅ Claude directory structure ready")

    # Show component status
    for component, status in claude_validation["component_status"].items():
        output.append(f"   {status} {component}")

    return claude_validation


def _setup_uv_dependencies(output: list[str], current_dir: Path) -> None:
    """Setup UV dependencies and package management."""
    output.append("\n🔧 Phase 2: UV dependency management & session setup...")

    uv_available = shutil.which("uv") is not None
    output.append(
        f"🔍 UV package manager: {'✅ AVAILABLE' if uv_available else '❌ NOT FOUND'}",
    )

    # Check UV permissions
    uv_trusted = permissions_manager.is_operation_trusted(
        permissions_manager.TRUSTED_UV_OPERATIONS,
    )
    if uv_trusted:
        output.append("🔐 UV operations: ✅ TRUSTED (no prompts needed)")
    else:
        output.append("🔐 UV operations: ⚠️ Will require permission prompts")

    if not uv_available:
        output.append("💡 Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return

    _handle_uv_operations(output, current_dir, uv_trusted)


def _handle_uv_operations(
    output: list[str],
    current_dir: Path,
    uv_trusted: bool,
) -> None:
    """Handle UV operations for dependency management."""
    project_has_pyproject = (current_dir / "pyproject.toml").exists()

    if not project_has_pyproject:
        output.append("⚠️ No pyproject.toml found - skipping UV operations")
        output.append("💡 Create pyproject.toml to enable UV dependency management")
        return

    original_cwd = Path.cwd()
    try:
        os.chdir(current_dir)
        output.append(f"📁 Working in: {current_dir}")

        # Trust UV operations if first successful run
        if not uv_trusted:
            output.append("🔓 Trusting UV operations for this session...")
            permissions_manager.trust_operation(
                permissions_manager.TRUSTED_UV_OPERATIONS,
                "UV package management operations",
            )
            output.append("✅ UV operations now trusted - no more prompts needed")

        _run_uv_sync_and_compile(output, current_dir)

    except Exception as e:
        output.append(f"⚠️ UV operation error: {e}")
    finally:
        os.chdir(original_cwd)


def _run_uv_sync_and_compile(output: list[str], current_dir: Path) -> None:
    """Run UV sync and compile operations."""
    # Sync dependencies
    sync_result = subprocess.run(
        ["uv", "sync"], check=False, capture_output=True, text=True
    )
    if sync_result.returncode == 0:
        output.append("✅ UV sync completed successfully")

        # Generate requirements.txt if needed
        if not (current_dir / "requirements.txt").exists():
            compile_result = subprocess.run(
                [
                    "uv",
                    "pip",
                    "compile",
                    "pyproject.toml",
                    "--output-file",
                    "requirements.txt",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if compile_result.returncode == 0:
                output.append("✅ Requirements.txt generated from UV dependencies")
            else:
                output.append(
                    f"⚠️ Requirements compilation warning: {compile_result.stderr}",
                )
        else:
            output.append("✅ Requirements.txt already exists")
    else:
        output.append(f"⚠️ UV sync issues: {sync_result.stderr}")


def _setup_session_management(output: list[str]) -> None:
    """Setup session management functionality."""
    output.append("\n🔧 Phase 3: Session management setup...")
    output.append("✅ Session management functionality ready")
    output.append("   📊 Conversation memory system enabled")
    output.append("   🔍 Semantic search capabilities available")

    output.append("\n🧠 Phase 4: Integrated MCP services initialization...")
    output.append("\n📊 Integrated MCP Services Status:")
    output.append("✅ Session Management - Active (conversation memory enabled)")


async def _analyze_project_structure(
    output: list[str],
    current_dir: Path,
    current_project: str,
) -> tuple[dict[str, Any], int]:
    """Analyze project structure and add information to output."""
    output.append(f"\n🎯 Phase 5: Project context analysis for {current_project}...")

    project_context = await analyze_project_context(current_dir)
    context_score = sum(1 for detected in project_context.values() if detected)

    output.append("🔍 Project structure analysis:")
    for context_type, detected in project_context.items():
        status = "✅" if detected else "➖"
        output.append(f"   {status} {context_type.replace('_', ' ').title()}")

    output.append(
        f"\n📊 Project maturity: {context_score}/{len(project_context)} indicators",
    )
    if context_score >= len(project_context) - 1:
        output.append("🌟 Excellent project structure - well-organized codebase")
    elif context_score >= len(project_context) // 2:
        output.append("👍 Good project structure - solid foundation")
    else:
        output.append("💡 Basic project - consider adding structure")

    return project_context, context_score


def _add_final_summary(
    output: list[str],
    current_project: str,
    context_score: int,
    project_context: dict[str, Any],
    claude_validation: dict[str, Any],
) -> None:
    """Add final summary information to output."""
    output.append("\n" + "=" * 60)
    output.append(f"🎯 {current_project.upper()} SESSION INITIALIZATION COMPLETE")
    output.append("=" * 60)

    output.append(f"📅 Initialized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"🗂️ Project: {current_project}")
    output.append(f"📊 Structure score: {context_score}/{len(project_context)}")

    missing_files = claude_validation.get("missing_files", [])
    if context_score >= len(project_context) // 2 and not missing_files:
        output.append("✅ Ready for productive session - all systems optimal")
    else:
        output.append("⚠️ Session ready with minor setup opportunities identified")

    _add_permissions_and_tools_summary(output, current_project)


def _add_permissions_and_tools_summary(output: list[str], current_project: str) -> None:
    """Add permissions summary and available tools."""
    # Permissions Summary
    permissions_status = permissions_manager.get_permission_status()
    output.append("\n🔐 Session Permissions Summary:")
    output.append(
        f"   📊 Trusted operations: {permissions_status['trusted_operations_count']}",
    )

    if permissions_status["trusted_operations_count"] > 0:
        output.append("   ✅ Future operations will have reduced permission prompts")
    else:
        output.append("   💡 Operations will be trusted automatically on first use")

    # Server Detection and Guidance
    detected_servers = _detect_other_mcp_servers()
    server_guidance = _generate_server_guidance(detected_servers)

    if server_guidance:
        output.append("\n" + "\n".join(server_guidance))

    output.append("\n📋 AVAILABLE MCP TOOLS:")
    output.append("📊 Session Management:")
    output.append("• checkpoint - Mid-session quality assessment")
    output.append("• end - Complete session cleanup")
    output.append("• status - Current session status")
    output.append("• permissions - Manage trusted operations")
    output.append("• Built-in conversation memory with semantic search")

    output.append(f"\n✨ {current_project} session initialization complete via MCP!")


async def calculate_quality_score() -> dict[str, Any]:
    """Calculate session quality score using V2 algorithm.

    V2 measures actual code quality (test coverage, lint, types, complexity)
    instead of superficial file existence checks.
    """
    current_dir = Path(os.environ.get("PWD", Path.cwd()))

    # Import V2 quality scoring (late import to avoid circular dependencies)
    from session_mgmt_mcp.utils.quality_utils_v2 import (
        _metrics_cache,
        calculate_quality_score_v2,
    )

    # Clear metrics cache to ensure fresh coverage data
    _metrics_cache.clear()

    # Get V2 quality score with actual code metrics
    permissions_count = len(permissions_manager.trusted_operations)

    # Count available development tools for trust score
    tool_count = 0
    if shutil.which("uv"):
        tool_count += 1
    if shutil.which("git"):
        tool_count += 1
    if shutil.which("python"):
        tool_count += 1
    if shutil.which("pytest"):
        tool_count += 1

    v2_score = await calculate_quality_score_v2(
        project_dir=current_dir,
        permissions_count=permissions_count,
        session_available=SESSION_MANAGEMENT_AVAILABLE,
        tool_count=tool_count,
    )

    # Return V2 format directly - no compatibility wrapper needed
    return {
        "total_score": int(v2_score.total_score),
        "version": "2.0",
        "breakdown": {
            "code_quality": v2_score.code_quality.total,
            "project_health": v2_score.project_health.total,
            "dev_velocity": v2_score.dev_velocity.total,
            "security": v2_score.security.total,
        },
        "trust_score": {
            "total": v2_score.trust_score.total,
            "breakdown": {
                "trusted_operations": v2_score.trust_score.trusted_operations,
                "session_availability": v2_score.trust_score.session_availability,
                "tool_ecosystem": v2_score.trust_score.tool_ecosystem,
            },
        },
        "recommendations": v2_score.recommendations,
        "details": {
            "code_quality": v2_score.code_quality.details,
            "project_health": v2_score.project_health.details,
            "dev_velocity": v2_score.dev_velocity.details,
            "security": v2_score.security.details,
        },
    }


def _generate_quality_recommendations(
    score: int,
    project_context: dict[str, Any],
    permissions_count: int,
    uv_available: bool,
) -> list[str]:
    """Generate quality improvement recommendations based on score factors."""
    recommendations = []

    if score < 50:
        recommendations.append(
            "Session needs attention - multiple areas for improvement",
        )
    elif score < 75:
        recommendations.append("Good session health - minor optimizations available")
    else:
        recommendations.append("Excellent session quality - maintain current practices")

    # Project-specific recommendations
    if not project_context.get("has_tests"):
        recommendations.append("Consider adding tests to improve project structure")
    if not project_context.get("has_docs"):
        recommendations.append("Documentation would enhance project maturity")

    # Permissions recommendations
    if permissions_count == 0:
        recommendations.append(
            "No trusted operations yet - permissions will be granted on first use",
        )
    elif permissions_count > 5:
        recommendations.append(
            "Many trusted operations - consider reviewing for security",
        )

    # Tools recommendations
    if not uv_available:
        recommendations.append(
            "Install UV package manager for better dependency management",
        )

    return recommendations


def _count_significant_files(current_dir: Path) -> int:
    """Count significant files in project as a complexity indicator."""
    file_count = 0
    with suppress(Exception):
        for file_path in current_dir.rglob("*"):
            if (
                file_path.is_file()
                and not any(part.startswith(".") for part in file_path.parts)
                and file_path.suffix
                in {
                    ".py",
                    ".js",
                    ".ts",
                    ".jsx",
                    ".tsx",
                    ".go",
                    ".rs",
                    ".java",
                    ".cpp",
                    ".c",
                    ".h",
                }
            ):
                file_count += 1
                if file_count > 50:  # Stop counting after threshold
                    break
    return file_count


def _check_git_activity(current_dir: Path) -> tuple[int, int] | None:
    """Check for active development via git and return (recent_commits, modified_files)."""
    git_dir = current_dir / ".git"
    if not git_dir.exists():
        return None

    try:
        # Check number of recent commits as activity indicator
        result = subprocess.run(
            ["git", "log", "--oneline", "-20", "--since='24 hours ago'"],
            check=False,
            capture_output=True,
            text=True,
            cwd=current_dir,
            timeout=5,
        )
        if result.returncode == 0:
            recent_commits = len(
                [line for line in result.stdout.strip().split("\\n") if line.strip()],
            )
        else:
            recent_commits = 0

        # Check for large number of modified files
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=False,
            capture_output=True,
            text=True,
            cwd=current_dir,
            timeout=5,
        )
        if status_result.returncode == 0:
            modified_files = len(
                [
                    line
                    for line in status_result.stdout.strip().split("\\n")
                    if line.strip()
                ],
            )
        else:
            modified_files = 0

        return recent_commits, modified_files

    except (subprocess.TimeoutExpired, Exception):
        return None


def _evaluate_large_project_heuristic(file_count: int) -> tuple[bool, str]:
    """Evaluate if the project is large enough to benefit from compaction."""
    if file_count > 50:
        return (
            True,
            "Large codebase with 50+ source files detected - context compaction recommended",
        )
    return False, ""


def _evaluate_git_activity_heuristic(
    git_activity: tuple[int, int] | None,
) -> tuple[bool, str]:
    """Evaluate if git activity suggests compaction would be beneficial."""
    if git_activity:
        recent_commits, modified_files = git_activity

        if recent_commits >= 3:
            return (
                True,
                f"High development activity ({recent_commits} commits in 24h) - compaction recommended",
            )

        if modified_files >= 10:
            return (
                True,
                f"Many modified files ({modified_files}) detected - context optimization beneficial",
            )

    return False, ""


def _evaluate_python_project_heuristic(current_dir: Path) -> tuple[bool, str]:
    """Evaluate if this is a Python project that might benefit from compaction."""
    if (current_dir / "tests").exists() and (current_dir / "pyproject.toml").exists():
        return (
            True,
            "Python project with tests detected - compaction may improve focus",
        )
    return False, ""


def _get_default_compaction_reason() -> str:
    """Get the default reason when no strong indicators are found."""
    return "Context appears manageable - compaction not immediately needed"


def _get_fallback_compaction_reason() -> str:
    """Get fallback reason when evaluation fails."""
    return "Unable to assess context complexity - compaction may be beneficial as a precaution"


def should_suggest_compact() -> tuple[bool, str]:
    """Determine if compacting would be beneficial and provide reasoning.
    Returns (should_compact, reason).

    Note: High complexity is necessary for comprehensive heuristic analysis
    of project state, git activity, and development patterns.
    """
    # Heuristics for when compaction might be needed:
    # 1. Large projects with many files
    # 2. Active development (recent git activity)
    # 3. Complex task sequences
    # 4. Session duration indicators

    try:
        current_dir = Path(os.environ.get("PWD", Path.cwd()))

        # Count significant files in project as a complexity indicator
        file_count = _count_significant_files(current_dir)

        # Large project heuristic
        should_compact, reason = _evaluate_large_project_heuristic(file_count)
        if should_compact:
            return should_compact, reason

        # Check for active development via git
        git_activity = _check_git_activity(current_dir)
        should_compact, reason = _evaluate_git_activity_heuristic(git_activity)
        if should_compact:
            return should_compact, reason

        # Check for common patterns suggesting complex session
        should_compact, reason = _evaluate_python_project_heuristic(current_dir)
        if should_compact:
            return should_compact, reason

        # Default to not suggesting unless we have clear indicators
        return False, _get_default_compaction_reason()

    except Exception:
        # If we can't determine, err on the side of suggesting compaction for safety
        return True, _get_fallback_compaction_reason()


async def _optimize_reflection_database() -> str:
    """Optimize the reflection database."""
    try:
        from .reflection_tools import get_reflection_database

        db = await get_reflection_database()
        await db.get_stats()
        db_size_before = (
            Path(db.db_path).stat().st_size if Path(db.db_path).exists() else 0
        )

        if db.conn:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: db.conn.execute("VACUUM"),
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: db.conn.execute("ANALYZE"),
            )

        db_size_after = (
            Path(db.db_path).stat().st_size if Path(db.db_path).exists() else 0
        )
        space_saved = db_size_before - db_size_after

        return f"🗄️ Database: {'Optimized reflection DB, saved ' + str(space_saved) + ' bytes' if space_saved > 0 else 'Reflection DB already optimized'}"

    except ImportError:
        return "ℹ️ Database: Reflection tools not available"
    except Exception as e:
        return f"⚠️ Database: Optimization skipped - {str(e)[:50]}"


async def _analyze_context_compaction() -> list[str]:
    """Analyze and recommend context compaction."""
    results = []

    try:
        should_compact, reason = should_suggest_compact()
        results.append("\n🔍 Context Compaction Analysis")
        results.append(f"📊 {reason}")

        if should_compact:
            results.extend(
                [
                    "",
                    "🔄 RECOMMENDATION: Run /compact to optimize context",
                    "📝 Benefits of compaction:",
                    "   • Improved response speed and accuracy",
                    "   • Better focus on current development context",
                    "   • Reduced memory usage for complex sessions",
                    "   • Cleaner conversation flow",
                    "",
                    "💡 WORKFLOW: After this checkpoint completes, run: /compact",
                    "🔄 Context compaction should be applied for optimal performance",
                ],
            )
        else:
            results.append("✅ Context appears well-optimized for current session")

        results.append(
            "💡 This checkpoint includes intelligent conversation summarization",
        )

        # Store conversation summary
        conversation_summary = await summarize_current_conversation()

        if conversation_summary["key_topics"]:
            key_topics_summary = (
                f"Session focus: {', '.join(conversation_summary['key_topics'][:3])}"
            )
            results.append(f"📋 {key_topics_summary}")

        if conversation_summary["decisions_made"]:
            key_decision = conversation_summary["decisions_made"][0]
            results.append(f"✅ Key decision: {key_decision}")

        # Store context summary for post-compaction retrieval
        await _store_context_summary(conversation_summary)
        results.append("💾 Context summary stored for post-compaction retrieval")

    except Exception as e:
        results.append(f"⚠️ Context summary storage failed: {str(e)[:50]}")

    return results


async def _store_context_summary(conversation_summary: dict[str, Any]) -> None:
    """Store comprehensive context summary."""
    try:
        db = await get_reflection_database()
        context_summary = f"Pre-compaction context summary: {', '.join(conversation_summary['key_topics'])}. "
        context_summary += (
            f"Decisions: {', '.join(conversation_summary['decisions_made'])}. "
        )
        context_summary += (
            f"Next steps: {', '.join(conversation_summary['next_steps'])}"
        )

        await db.store_reflection(
            context_summary,
            [
                "pre-compaction",
                "context-summary",
                "checkpoint",
                current_project or "unknown-project",
            ],
        )
    except Exception as e:
        msg = f"Context summary storage failed: {str(e)[:50]}"
        raise Exception(msg)


async def perform_strategic_compaction() -> list[str]:
    """Perform strategic compaction and optimization tasks."""
    results = []
    current_dir = Path(os.environ.get("PWD", Path.cwd()))

    # Database optimization
    results.append(await _optimize_reflection_database())

    # Log cleanup
    results.append(_cleanup_session_logs())

    # Temp file cleanup
    results.append(_cleanup_temp_files(current_dir))

    # Git optimization
    results.extend(_optimize_git_repository(current_dir))

    # UV cache cleanup
    results.append(_cleanup_uv_cache())

    # Context compaction analysis
    results.extend(await _analyze_context_compaction())

    # Summary
    total_operations = len([r for r in results if not r.startswith(("ℹ️", "⚠️", "⏱️"))])
    results.extend(
        [
            f"\n📊 Strategic compaction complete: {total_operations} optimization tasks performed",
            "🎯 Recommendation: Conversation context should be compacted automatically",
        ],
    )

    return results


async def _generate_basic_insights(
    quality_score: float,
    conversation_summary: dict[str, Any],
) -> list[str]:
    """Generate basic session insights from quality score and conversation summary."""
    insights = []

    insights.append(
        f"Session checkpoint completed with quality score: {quality_score}/100",
    )

    if conversation_summary["key_topics"]:
        insights.append(
            f"Key discussion topics: {', '.join(conversation_summary['key_topics'][:3])}",
        )

    if conversation_summary["decisions_made"]:
        insights.append(
            f"Important decisions: {conversation_summary['decisions_made'][0]}",
        )

    if conversation_summary["next_steps"]:
        insights.append(
            f"Next steps identified: {conversation_summary['next_steps'][0]}",
        )

    return insights


async def _add_project_context_insights(insights: list[str]) -> None:
    """Add project context analysis to insights."""
    current_dir = Path(os.environ.get("PWD", Path.cwd()))
    project_context = await analyze_project_context(current_dir)
    context_items = [k for k, v in project_context.items() if v]
    if context_items:
        insights.append(f"Active project context: {', '.join(context_items)}")


def _add_session_health_insights(insights: list[str], quality_score: float) -> None:
    """Add session health indicators to insights."""
    if quality_score >= 80:
        insights.append("Excellent session progress with optimal workflow patterns")
    elif quality_score >= 60:
        insights.append("Good session progress with minor optimization opportunities")
    else:
        insights.append(
            "Session requires attention - potential workflow improvements needed",
        )


def _generate_session_tags(quality_score: float) -> list[str]:
    """Generate contextual tags for session reflection storage."""
    tags = ["checkpoint", "session-summary", current_project or "unknown-project"]
    if quality_score >= 80:
        tags.append("excellent-session")
    elif quality_score < 60:
        tags.append("needs-attention")
    return tags


async def _capture_flow_analysis(db: Any, tags: list[str], results: list[str]) -> None:
    """Capture conversation flow insights."""
    flow_analysis = await analyze_conversation_flow()
    flow_summary = f"Session pattern: {flow_analysis['pattern_type']}. "
    if flow_analysis["recommendations"]:
        flow_summary += f"Key recommendation: {flow_analysis['recommendations'][0]}"

    flow_id = await db.store_reflection(
        flow_summary,
        [*tags, "flow-analysis", "phase3"],
    )
    results.append(f"🔄 Flow analysis stored: {flow_id[:12]}...")


async def _capture_intelligence_insights(
    db: ReflectionDatabase,
    tags: list[str],
    results: list[str],
) -> None:
    """Capture session intelligence insights."""
    intelligence = await generate_session_intelligence()
    if intelligence["priority_actions"]:
        intel_summary = f"Session intelligence: {intelligence['intelligence_level']}. "
        intel_summary += f"Priority: {intelligence['priority_actions'][0]}"

        intel_id = await db.store_reflection(
            intel_summary,
            [*tags, "intelligence", "proactive"],
        )
        results.append(f"🧠 Intelligence insights stored: {intel_id[:12]}...")


def _check_session_management_availability() -> bool:
    """Check if session management is available."""
    return SESSION_MANAGEMENT_AVAILABLE


async def _attempt_checkpoint_session() -> dict[str, Any] | None:
    """Attempt to get checkpoint session data."""
    try:
        if not SESSION_MANAGEMENT_AVAILABLE:
            return None

        session_manager = SessionLifecycleManager()
        working_directory = os.environ.get("PWD", str(Path.cwd()))
        result = await session_manager.checkpoint_session(working_directory)
        if isinstance(result, dict):
            return result
        return None
    except Exception:
        return None


def _extract_session_stats(checkpoint_result: dict[str, Any]) -> dict[str, Any] | None:
    """Extract session statistics from checkpoint result."""
    session_stats = checkpoint_result.get("session_stats", {})
    return session_stats or None


def _format_metrics_summary(session_stats: dict[str, Any]) -> str:
    """Format session metrics summary."""
    detail_summary = (
        f"Session metrics - Duration: {session_stats.get('duration_minutes', 0)}min, "
    )
    detail_summary += f"Success rate: {session_stats.get('success_rate', 0):.1f}%, "
    detail_summary += f"Checkpoints: {session_stats.get('total_checkpoints', 0)}"
    return detail_summary


async def _capture_session_metrics(
    db: Any, tags: list[str], results: list[str]
) -> None:
    """Capture additional session metrics if available."""
    # Check if session management is available
    if not _check_session_management_availability():
        return

    try:
        # Attempt to get checkpoint session data
        checkpoint_result = await _attempt_checkpoint_session()
        if not checkpoint_result:
            return

        # Extract session statistics
        session_stats = _extract_session_stats(checkpoint_result)
        if not session_stats:
            return

        # Format metrics summary
        detail_summary = _format_metrics_summary(session_stats)

        # Store in database
        detail_id = await db.store_reflection(
            detail_summary,
            [*tags, "session-metrics"],
        )
        results.append(f"📊 Session metrics stored: {detail_id[:12]}...")

    except Exception as e:
        results.append(f"⚠️ Session metrics capture failed: {str(e)[:50]}...")


async def capture_session_insights(quality_score: float) -> list[str]:
    """Phase 1 & 3: Automatically capture and store session insights with conversation summarization."""
    results = []

    if not REFLECTION_TOOLS_AVAILABLE:
        results.append(
            "⚠️ Reflection storage not available - install dependencies: pip install duckdb transformers",
        )
        return results

    try:
        # Phase 3: AI-Powered Conversation Summarization
        conversation_summary = await summarize_current_conversation()

        # Generate comprehensive session summary
        insights = await _generate_basic_insights(quality_score, conversation_summary)
        await _add_project_context_insights(insights)
        _add_session_health_insights(insights, quality_score)

        # Store main session reflection
        session_summary = ". ".join(insights)
        tags = _generate_session_tags(quality_score)

        db = await get_reflection_database()
        reflection_id = await db.store_reflection(session_summary, tags)

        results.append("✅ Session insights automatically captured and stored")
        results.append(f"🆔 Reflection ID: {reflection_id[:12]}...")
        results.append(f"📝 Summary: {session_summary[:80]}...")
        results.append(f"🏷️ Tags: {', '.join(tags)}")

        # Phase 3A: Enhanced insight capture with advanced intelligence
        try:
            await _capture_flow_analysis(db, tags, results)
            await _capture_intelligence_insights(db, tags, results)
        except Exception as e:
            results.append(f"⚠️ Phase 3 insight capture failed: {str(e)[:50]}...")

        # Store additional detailed context
        await _capture_session_metrics(db, tags, results)

    except Exception as e:
        results.append(f"❌ Insight capture failed: {str(e)[:60]}...")
        results.append(
            "💡 Manual reflection storage still available via store_reflection tool",
        )

    return results


def _create_empty_summary() -> dict[str, Any]:
    """Create empty conversation summary structure."""
    return {
        "key_topics": [],
        "decisions_made": [],
        "next_steps": [],
        "problems_solved": [],
        "code_changes": [],
    }


def _extract_topics_from_content(content: str) -> set[str]:
    """Extract topics from reflection content."""
    topics = set()
    if "project context:" in content:
        context_part = content.split("project context:")[1].split(".")[0]
        topics.update(word.strip() for word in context_part.split(","))
    return topics


def _extract_decisions_from_content(content: str) -> list[str]:
    """Extract decisions from reflection content."""
    decisions = []
    if "excellent" in content:
        decisions.append("Maintaining productive workflow patterns")
    elif "attention" in content:
        decisions.append("Identified areas needing workflow optimization")
    elif "good progress" in content:
        decisions.append("Steady development progress confirmed")
    return decisions


def _extract_next_steps_from_content(content: str) -> list[str]:
    """Extract next steps from reflection content."""
    next_steps = []
    if "priority:" in content:
        priority_part = content.split("priority:")[1].split(".")[0]
        if priority_part.strip():
            next_steps.append(priority_part.strip())
    return next_steps


async def _process_recent_reflections(db: Any, summary: dict[str, Any]) -> None:
    """Process recent reflections to extract conversation insights."""
    recent_reflections = await db.search_reflections("checkpoint", limit=5)

    if not recent_reflections:
        return

    topics = set()
    decisions = []
    next_steps = []

    for reflection in recent_reflections:
        content = reflection["content"].lower()

        topics.update(_extract_topics_from_content(content))
        decisions.extend(_extract_decisions_from_content(content))
        next_steps.extend(_extract_next_steps_from_content(content))

    summary["key_topics"] = list(topics)[:5]
    summary["decisions_made"] = decisions[:3]
    summary["next_steps"] = next_steps[:3]


def _add_current_session_context(summary: dict[str, Any]) -> None:
    """Add current session context to summary."""
    current_dir = Path(os.environ.get("PWD", Path.cwd()))
    if (current_dir / "session_mgmt_mcp").exists():
        summary["key_topics"].append("session-mgmt-mcp development")


def _ensure_summary_defaults(summary: dict[str, Any]) -> None:
    """Ensure summary has default values if empty."""
    if not summary["key_topics"]:
        summary["key_topics"] = [
            "session management",
            "workflow optimization",
        ]

    if not summary["decisions_made"]:
        summary["decisions_made"] = ["Proceeding with current development approach"]

    if not summary["next_steps"]:
        summary["next_steps"] = ["Continue with regular checkpoint monitoring"]


def _get_fallback_summary() -> dict[str, Any]:
    """Get fallback summary when reflection processing fails."""
    return {
        "key_topics": ["development session", "workflow management"],
        "decisions_made": ["Maintaining current session approach"],
        "next_steps": ["Continue monitoring session quality"],
        "problems_solved": ["Session management optimization"],
        "code_changes": ["Enhanced checkpoint functionality"],
    }


def _get_error_summary(error: Exception) -> dict[str, Any]:
    """Get error summary when conversation analysis fails."""
    return {
        "key_topics": ["session analysis"],
        "decisions_made": ["Continue current workflow"],
        "next_steps": ["Regular quality monitoring"],
        "problems_solved": [],
        "code_changes": [],
        "error": str(error),
    }


async def summarize_current_conversation() -> dict[str, Any]:
    """Phase 3: AI-Powered Conversation Summarization."""
    try:
        summary = _create_empty_summary()

        if REFLECTION_TOOLS_AVAILABLE:
            try:
                db = await get_reflection_database()
                await _process_recent_reflections(db, summary)
                _add_current_session_context(summary)
                _ensure_summary_defaults(summary)
            except Exception:
                summary = _get_fallback_summary()

        return summary

    except Exception as e:
        return _get_error_summary(e)


def _check_workflow_drift(quality_scores: list[float]) -> tuple[list[str], bool]:
    """Check for workflow drift indicators."""
    quality_alerts = []
    recommend_checkpoint = False

    if len(quality_scores) >= 4:
        variance = max(quality_scores) - min(quality_scores)
        if variance > 30:
            quality_alerts.append(
                "High quality variance detected - workflow inconsistency",
            )
            recommend_checkpoint = True

    return quality_alerts, recommend_checkpoint


async def _perform_quality_analysis() -> tuple[str, list[str], bool]:
    """Perform quality analysis with reflection data."""
    quality_alerts = []
    quality_trend = "stable"
    recommend_checkpoint = False

    try:
        db = await get_reflection_database()
        recent_reflections = await db.search_reflections("quality score", limit=5)
        quality_scores = _extract_quality_scores(recent_reflections)

        if quality_scores:
            trend, trend_alerts, trend_checkpoint = _analyze_quality_trend(
                quality_scores,
            )
            quality_trend = trend
            quality_alerts.extend(trend_alerts)
            recommend_checkpoint = recommend_checkpoint or trend_checkpoint

            drift_alerts, drift_checkpoint = _check_workflow_drift(quality_scores)
            quality_alerts.extend(drift_alerts)
            recommend_checkpoint = recommend_checkpoint or drift_checkpoint

    except Exception:
        quality_alerts.append("Quality monitoring analysis unavailable")

    return quality_trend, quality_alerts, recommend_checkpoint


def _get_quality_error_result(error: Exception) -> dict[str, Any]:
    """Get error result for quality monitoring failure."""
    return {
        "quality_trend": "unknown",
        "alerts": ["Quality monitoring failed"],
        "recommend_checkpoint": False,
        "monitoring_active": False,
        "error": str(error),
    }


async def monitor_proactive_quality() -> dict[str, Any]:
    """Phase 3: Proactive Quality Monitoring with Early Warning System."""
    try:
        quality_alerts = []
        quality_trend = "stable"
        recommend_checkpoint = False

        if REFLECTION_TOOLS_AVAILABLE:
            (
                quality_trend,
                quality_alerts,
                recommend_checkpoint,
            ) = await _perform_quality_analysis()

        return {
            "quality_trend": quality_trend,
            "alerts": quality_alerts,
            "recommend_checkpoint": recommend_checkpoint,
            "monitoring_active": True,
        }

    except Exception as e:
        return _get_quality_error_result(e)


async def analyze_advanced_context_metrics() -> dict[str, Any]:
    """Phase 3A: Advanced context metrics analysis."""
    return {
        "estimated_tokens": 0,  # Placeholder for actual token counting
        "context_density": "moderate",
        "conversation_depth": "active",
    }


async def analyze_token_usage_patterns() -> dict[str, Any]:
    """Phase 3A: Intelligent token usage analysis with smart triggers."""
    try:
        conv_stats = await _get_conversation_statistics()
        analysis = _analyze_context_usage_patterns(conv_stats)
        return _finalize_token_analysis(analysis)

    except Exception as e:
        return {
            "needs_attention": False,
            "status": "analysis_failed",
            "estimated_length": "unknown",
            "recommend_compact": False,
            "recommend_clear": False,
            "error": str(e),
        }


async def _get_conversation_statistics() -> dict[str, int]:
    """Get conversation statistics from memory system."""
    from contextlib import suppress

    conv_stats: dict[str, int] = {
        "total_conversations": 0,
        "recent_activity": 0,
    }

    if REFLECTION_TOOLS_AVAILABLE:
        with suppress(Exception):
            db = await get_reflection_database()
            stats = await db.get_stats()
            conv_stats["total_conversations"] = stats.get("conversations_count", 0)

    return conv_stats


def _analyze_context_usage_patterns(conv_stats: dict[str, int]) -> dict[str, Any]:
    """Analyze context usage patterns and generate recommendations."""
    estimated_length = "moderate"
    needs_attention = False
    recommend_compact = False
    recommend_clear = False

    total_conversations = conv_stats["total_conversations"]

    # Progressive thresholds based on conversation count
    if total_conversations > 3:
        estimated_length = "extensive"
        needs_attention = True
        recommend_compact = True

    if total_conversations > 10:
        estimated_length = "very long"
        needs_attention = True
        recommend_compact = True

    if total_conversations > 20:
        estimated_length = "extremely long"
        needs_attention = True
        recommend_compact = True
        recommend_clear = True

    return {
        "estimated_length": estimated_length,
        "needs_attention": needs_attention,
        "recommend_compact": recommend_compact,
        "recommend_clear": recommend_clear,
    }


def _finalize_token_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    """Finalize token analysis with checkpoint override."""
    # Override: ALWAYS recommend compaction during checkpoints
    analysis["recommend_compact"] = True
    analysis["needs_attention"] = True

    if analysis["estimated_length"] == "moderate":
        analysis["estimated_length"] = "checkpoint-session"

    analysis["status"] = (
        "optimal" if not analysis["needs_attention"] else "needs optimization"
    )

    return analysis


async def analyze_conversation_flow() -> dict[str, Any]:
    """Phase 3A: Analyze conversation patterns and flow."""
    try:
        # Analyze recent reflection patterns to understand session flow

        if REFLECTION_TOOLS_AVAILABLE:
            try:
                db = await get_reflection_database()

                # Search recent reflections for patterns
                recent_reflections = await db.search_reflections(
                    "session checkpoint",
                    limit=5,
                )

                if recent_reflections:
                    # Analyze pattern based on recent reflections
                    if any(
                        "excellent" in r["content"].lower() for r in recent_reflections
                    ):
                        pattern_type = "productive_development"
                        recommendations = [
                            "Continue current productive workflow",
                            "Consider documenting successful patterns",
                            "Maintain current checkpoint frequency",
                        ]
                    elif any(
                        "attention" in r["content"].lower() for r in recent_reflections
                    ):
                        pattern_type = "optimization_needed"
                        recommendations = [
                            "Review recent workflow changes",
                            "Consider more frequent checkpoints",
                            "Use search tools to find successful patterns",
                        ]
                    else:
                        pattern_type = "steady_progress"
                        recommendations = [
                            "Maintain current workflow patterns",
                            "Consider periodic workflow evaluation",
                        ]
                else:
                    pattern_type = "new_session"
                    recommendations = [
                        "Establish workflow patterns through regular checkpoints",
                    ]

            except Exception:
                pattern_type = "analysis_unavailable"
                recommendations = [
                    "Use regular checkpoints to establish workflow patterns",
                ]
        else:
            pattern_type = "basic_session"
            recommendations = ["Enable reflection tools for advanced flow analysis"]

        return {
            "pattern_type": pattern_type,
            "recommendations": recommendations,
            "confidence": "pattern_based",
        }

    except Exception as e:
        return {
            "pattern_type": "analysis_failed",
            "recommendations": ["Use basic workflow patterns"],
            "error": str(e),
        }


async def analyze_memory_patterns(db: Any, conv_count: int) -> dict[str, Any]:
    """Phase 3A: Advanced memory pattern analysis."""
    try:
        # Analyze conversation history for intelligent insights
        if conv_count == 0:
            return {
                "summary": "New session - no historical patterns yet",
                "proactive_suggestions": [
                    "Start building conversation history for better insights",
                ],
            }
        if conv_count < 5:
            return {
                "summary": f"{conv_count} conversations stored - building pattern recognition",
                "proactive_suggestions": [
                    "Continue regular checkpoints to build session intelligence",
                    "Use store_reflection for important insights",
                ],
            }
        if conv_count < 20:
            return {
                "summary": f"{conv_count} conversations stored - developing patterns",
                "proactive_suggestions": [
                    "Use reflect_on_past to leverage growing knowledge base",
                    "Search previous solutions before starting new implementations",
                ],
            }
        return {
            "summary": f"{conv_count} conversations - rich pattern recognition available",
            "proactive_suggestions": [
                "Leverage extensive history with targeted searches",
                "Consider workflow optimization based on successful patterns",
                "Use conversation history to accelerate problem-solving",
            ],
        }

    except Exception as e:
        return {
            "summary": "Memory analysis unavailable",
            "proactive_suggestions": [
                "Use basic memory tools for conversation tracking",
            ],
            "error": str(e),
        }


async def analyze_project_workflow_patterns(current_dir: Path) -> dict[str, Any]:
    """Phase 3A: Project-specific workflow pattern analysis."""
    try:
        project_characteristics = _detect_project_characteristics(current_dir)
        workflow_recommendations = _generate_workflow_recommendations(
            project_characteristics
        )

        return {
            "workflow_recommendations": workflow_recommendations,
            "project_characteristics": project_characteristics,
        }

    except Exception as e:
        return {
            "workflow_recommendations": ["Use basic project workflow patterns"],
            "error": str(e),
        }


def _detect_project_characteristics(current_dir: Path) -> dict[str, bool]:
    """Detect project characteristics from directory structure."""
    return {
        "has_tests": (current_dir / "tests").exists()
        or (current_dir / "test").exists(),
        "has_git": (current_dir / ".git").exists(),
        "has_python": (current_dir / "pyproject.toml").exists()
        or (current_dir / "requirements.txt").exists(),
        "has_node": (current_dir / "package.json").exists(),
        "has_docker": (current_dir / "Dockerfile").exists()
        or (current_dir / "docker-compose.yml").exists(),
    }


def _generate_workflow_recommendations(characteristics: dict[str, bool]) -> list[str]:
    """Generate workflow recommendations based on project characteristics."""
    recommendations = []

    if characteristics["has_tests"]:
        recommendations.extend(
            [
                "Use targeted test commands for specific test scenarios",
                "Consider test-driven development workflow with regular testing",
            ]
        )

    if characteristics["has_git"]:
        recommendations.extend(
            [
                "Leverage git context for branch-specific development",
                "Use commit messages to track progress patterns",
            ]
        )

    if characteristics["has_python"] and characteristics["has_tests"]:
        recommendations.append(
            "Python+Testing: Consider pytest workflows with coverage analysis"
        )

    if characteristics["has_node"]:
        recommendations.append(
            "Node.js project: Leverage npm/yarn scripts in development workflow"
        )

    if characteristics["has_docker"]:
        recommendations.append(
            "Containerized project: Consider container-based development workflows"
        )

    # Default recommendations if no specific patterns detected
    if not recommendations:
        recommendations.append(
            "Establish project-specific workflow patterns through regular checkpoints"
        )

    return recommendations


async def _analyze_reflection_based_intelligence() -> list[str]:
    """Analyze recent reflections for intelligence recommendations."""
    if not REFLECTION_TOOLS_AVAILABLE:
        return []

    try:
        db = await get_reflection_database()
        recent_reflections = await db.search_reflections("checkpoint", limit=3)

        if recent_reflections:
            recent_scores = _extract_quality_scores(recent_reflections)
            return _generate_quality_trend_recommendations(recent_scores)

    except Exception:
        return ["Enable reflection analysis for session trend intelligence"]

    return []


async def generate_session_intelligence() -> dict[str, Any]:
    """Phase 3A: Generate proactive session intelligence and priority actions."""
    try:
        current_time = datetime.now()

        # Gather all recommendation sources
        priority_actions = []
        priority_actions.extend(_get_time_based_recommendations(current_time.hour))
        priority_actions.extend(await _analyze_reflection_based_intelligence())
        priority_actions = _ensure_default_recommendations(priority_actions)

        return {
            "priority_actions": priority_actions,
            "intelligence_level": "proactive",
            "timestamp": current_time.isoformat(),
        }

    except Exception as e:
        return _get_intelligence_error_result(e)


async def _analyze_token_usage_recommendations(results: list[str]) -> None:
    """Analyze token usage and add recommendations."""
    token_analysis = await analyze_token_usage_patterns()
    if token_analysis["needs_attention"]:
        results.append(f"⚠️ Context usage: {token_analysis['status']}")
        results.append(
            f"   Estimated conversation length: {token_analysis['estimated_length']}",
        )

        # Smart compaction triggers - PRIORITY RECOMMENDATIONS
        if token_analysis["recommend_compact"]:
            results.append(
                "🚨 CRITICAL AUTO-RECOMMENDATION: Context compaction required",
            )
            results.append(
                "🔄 This checkpoint has prepared conversation summary for compaction",
            )
            results.append(
                "💡 Compaction should be applied automatically after this checkpoint",
            )

        if token_analysis["recommend_clear"]:
            results.append(
                "🆕 AUTO-RECOMMENDATION: Consider /clear for fresh context after compaction",
            )
    else:
        results.append(f"✅ Context usage: {token_analysis['status']}")


async def _analyze_conversation_flow_recommendations(results: list[str]) -> None:
    """Analyze conversation flow and add recommendations."""
    flow_analysis = await analyze_conversation_flow()
    results.append(f"📊 Session flow: {flow_analysis['pattern_type']}")

    if flow_analysis["recommendations"]:
        results.append("🎯 Flow-based recommendations:")
        for rec in flow_analysis["recommendations"][:3]:
            results.append(f"   • {rec}")


async def _analyze_memory_recommendations(results: list[str]) -> None:
    """Analyze memory patterns and add recommendations."""
    if REFLECTION_TOOLS_AVAILABLE:
        try:
            db = await get_reflection_database()
            stats = await db.get_stats()
            conv_count = stats.get("conversations_count", 0)

            # Advanced memory analysis
            memory_insights = await analyze_memory_patterns(db, conv_count)
            results.append(f"📚 Memory insights: {memory_insights['summary']}")

            if memory_insights["proactive_suggestions"]:
                results.append("💡 Proactive suggestions:")
                for suggestion in memory_insights["proactive_suggestions"][:2]:
                    results.append(f"   • {suggestion}")

        except Exception:
            results.append("📚 Memory system available for conversation search")


async def _analyze_project_workflow_recommendations(results: list[str]) -> None:
    """Analyze project workflow patterns and add recommendations."""
    current_dir = Path(os.environ.get("PWD", Path.cwd()))
    project_insights = await analyze_project_workflow_patterns(current_dir)

    if project_insights["workflow_recommendations"]:
        results.append("🚀 Workflow optimizations:")
        for opt in project_insights["workflow_recommendations"][:2]:
            results.append(f"   • {opt}")


async def _analyze_session_intelligence_recommendations(results: list[str]) -> None:
    """Analyze session intelligence and add recommendations."""
    session_intelligence = await generate_session_intelligence()
    if session_intelligence["priority_actions"]:
        results.append("\n🧠 Session Intelligence:")
        for action in session_intelligence["priority_actions"][:3]:
            results.append(f"   • {action}")


async def _analyze_quality_monitoring_recommendations(results: list[str]) -> None:
    """Analyze quality monitoring and add recommendations."""
    quality_monitoring = await monitor_proactive_quality()
    if quality_monitoring["monitoring_active"]:
        results.append(f"\n📊 Quality Trend: {quality_monitoring['quality_trend']}")

        if quality_monitoring["alerts"]:
            results.append("⚠️ Quality Alerts:")
            for alert in quality_monitoring["alerts"][:2]:
                results.append(f"   • {alert}")

        if quality_monitoring["recommend_checkpoint"]:
            results.append("🔄 PROACTIVE RECOMMENDATION: Consider immediate checkpoint")


async def _add_fallback_recommendations(results: list[str], error: Exception) -> None:
    """Add fallback recommendations when analysis fails."""
    results.append(f"❌ Advanced context analysis failed: {str(error)[:60]}...")
    results.append("💡 Falling back to basic context management recommendations")

    # Fallback to basic recommendations
    results.append("🎯 Basic context actions:")
    results.append("   • Use /compact for conversation summarization")
    results.append("   • Use /clear for fresh context on new topics")
    results.append("   • Use search tools to retrieve relevant discussions")


async def analyze_context_usage() -> list[str]:
    """Phase 2 & 3A: Advanced context analysis with intelligent recommendations."""
    results = []

    try:
        results.append("🔍 Advanced context analysis and optimization...")

        # Phase 3A: Advanced Context Intelligence
        await analyze_advanced_context_metrics()

        # Run all analysis components
        await _analyze_token_usage_recommendations(results)
        await _analyze_conversation_flow_recommendations(results)
        await _analyze_memory_recommendations(results)
        await _analyze_project_workflow_recommendations(results)
        await _analyze_session_intelligence_recommendations(results)
        await _analyze_quality_monitoring_recommendations(results)

    except Exception as e:
        await _add_fallback_recommendations(results, e)

    return results


async def _perform_quality_assessment() -> tuple[int, dict[str, Any]]:
    """Perform quality assessment and return score and data."""
    quality_data = await calculate_quality_score()
    quality_score = quality_data["total_score"]
    return quality_score, quality_data


async def _format_quality_results(
    quality_score: int,
    quality_data: dict[str, Any],
    checkpoint_result: dict[str, Any] | None = None,
) -> list[str]:
    """Format quality assessment results for display."""
    output = []

    # Quality status with version indicator
    version = quality_data.get("version", "1.0")
    if quality_score >= 80:
        output.append(
            f"✅ Session quality: EXCELLENT (Score: {quality_score}/100) [V{version}]"
        )
    elif quality_score >= 60:
        output.append(
            f"✅ Session quality: GOOD (Score: {quality_score}/100) [V{version}]"
        )
    else:
        output.append(
            f"⚠️ Session quality: NEEDS ATTENTION (Score: {quality_score}/100) [V{version}]",
        )

    # Quality breakdown - V2 format (actual code quality metrics)
    output.append("\n📈 Quality breakdown (code health metrics):")
    breakdown = quality_data["breakdown"]
    output.append(f"   • Code quality: {breakdown['code_quality']:.1f}/40")
    output.append(f"   • Project health: {breakdown['project_health']:.1f}/30")
    output.append(f"   • Dev velocity: {breakdown['dev_velocity']:.1f}/20")
    output.append(f"   • Security: {breakdown['security']:.1f}/10")

    # Trust score (separate from quality)
    if "trust_score" in quality_data:
        trust = quality_data["trust_score"]
        output.append(f"\n🔐 Trust score: {trust['total']:.0f}/100 (separate metric)")
        output.append(
            f"   • Trusted operations: {trust['breakdown']['trusted_operations']:.0f}/40"
        )
        output.append(
            f"   • Session features: {trust['breakdown']['session_availability']:.0f}/30"
        )
        output.append(
            f"   • Tool ecosystem: {trust['breakdown']['tool_ecosystem']:.0f}/30"
        )

    # Recommendations
    recommendations = quality_data["recommendations"]
    if recommendations:
        output.append("\n💡 Recommendations:")
        for rec in recommendations[:3]:
            output.append(f"   • {rec}")

    # Session management specific results
    if checkpoint_result:
        strengths = checkpoint_result.get("strengths", [])
        if strengths:
            output.append("\n🌟 Session strengths:")
            for strength in strengths[:3]:
                output.append(f"   • {strength}")

        session_stats = checkpoint_result.get("session_stats", {})
        if session_stats:
            output.append("\n⏱️ Session progress:")
            output.append(
                f"   • Duration: {session_stats.get('duration_minutes', 0)} minutes",
            )
            output.append(
                f"   • Checkpoints: {session_stats.get('total_checkpoints', 0)}",
            )
            output.append(
                f"   • Success rate: {session_stats.get('success_rate', 0):.1f}%",
            )

    return output


async def _perform_git_checkpoint(
    current_dir: Path, quality_score: int, project_name: str
) -> list[str]:
    """Handle git operations for checkpoint commit."""
    output = []
    output.append("\n" + "=" * 50)
    output.append("📦 Git Checkpoint Commit")
    output.append("=" * 50)

    # Use the proper checkpoint commit function from git_operations
    from session_mgmt_mcp.utils.git_operations import create_checkpoint_commit

    success, result, commit_output = create_checkpoint_commit(
        current_dir, project_name, quality_score
    )

    # Add the commit output to our output
    output.extend(commit_output)

    if success and result != "clean":
        output.append(f"✅ Checkpoint commit created: {result}")
    elif not success:
        output.append(f"⚠️ Failed to stage files: {result}")

    return output


async def health_check() -> dict[str, Any]:
    """Comprehensive health check for MCP server and toolkit availability."""
    health_status: dict[str, Any] = {
        "overall_healthy": True,
        "checks": {},
        "warnings": [],
        "errors": [],
    }

    # MCP Server health
    try:
        # Test FastMCP availability
        health_status["checks"]["mcp_server"] = "✅ Active"
    except Exception as e:
        health_status["checks"]["mcp_server"] = "❌ Error"
        health_status["errors"].append(f"MCP server issue: {e}")
        health_status["overall_healthy"] = False

    # Session management toolkit health
    health_status["checks"]["session_toolkit"] = (
        "✅ Available" if SESSION_MANAGEMENT_AVAILABLE else "⚠️ Limited"
    )
    if not SESSION_MANAGEMENT_AVAILABLE:
        health_status["warnings"].append(
            "Session management toolkit not fully available",
        )

    # UV package manager health
    uv_available = shutil.which("uv") is not None
    health_status["checks"]["uv_manager"] = (
        "✅ Available" if uv_available else "❌ Missing"
    )
    if not uv_available:
        health_status["warnings"].append("UV package manager not found")

    # Claude directory health
    validate_claude_directory()
    health_status["checks"]["claude_directory"] = "✅ Valid"

    # Permissions system health
    try:
        permissions_status = permissions_manager.get_permission_status()
        health_status["checks"]["permissions_system"] = "✅ Active"
        health_status["checks"]["session_id"] = (
            f"Active ({permissions_status['session_id']})"
        )
    except Exception as e:
        health_status["checks"]["permissions_system"] = "❌ Error"
        health_status["errors"].append(f"Permissions system issue: {e}")
        health_status["overall_healthy"] = False

    # Crackerjack integration health
    health_status["checks"]["crackerjack_integration"] = (
        "✅ Available" if CRACKERJACK_INTEGRATION_AVAILABLE else "⚠️ Not Available"
    )
    if not CRACKERJACK_INTEGRATION_AVAILABLE:
        health_status["warnings"].append(
            "Crackerjack integration not available - quality monitoring disabled",
        )

    # Log health check results
    session_logger.info(
        "Health check completed",
        overall_healthy=health_status["overall_healthy"],
        warnings_count=len(health_status["warnings"]),
        errors_count=len(health_status["errors"]),
    )

    return health_status


async def _add_basic_status_info(output: list[str], current_dir: Path) -> None:
    """Add basic status information to output."""
    global current_project
    current_project = current_dir.name

    output.append(f"📁 Current project: {current_project}")
    output.append(f"🗂️ Working directory: {current_dir}")
    output.append("🌐 MCP server: Active (Claude Session Management)")


async def _add_health_status_info(output: list[str]) -> None:
    """Add health check information to output."""
    health_status = await health_check()

    output.append(
        f"\n🏥 System Health: {'✅ HEALTHY' if health_status['overall_healthy'] else '⚠️ ISSUES DETECTED'}",
    )

    # Display health check results
    for check_name, status in health_status["checks"].items():
        friendly_name = check_name.replace("_", " ").title()
        output.append(f"   • {friendly_name}: {status}")

    # Show warnings and errors
    if health_status["warnings"]:
        output.append("\n⚠️ Health Warnings:")
        for warning in health_status["warnings"][:3]:  # Limit to 3 warnings
            output.append(f"   • {warning}")

    if health_status["errors"]:
        output.append("\n❌ Health Errors:")
        for error in health_status["errors"][:3]:  # Limit to 3 errors
            output.append(f"   • {error}")


async def _get_project_context_info(
    current_dir: Path,
) -> tuple[dict[str, Any], int, int]:
    """Get project context information and scores."""
    project_context = await analyze_project_context(current_dir)
    context_score = sum(1 for detected in project_context.values() if detected)
    max_score = len(project_context)
    return project_context, context_score, max_score


def _format_project_maturity_section(context_score: int, max_score: int) -> list[str]:
    """Format the project maturity section."""
    return [f"\n\x75 Project maturity: {context_score}/{max_score}"]


def _format_git_worktree_header() -> str:
    """Format the git worktree information header."""
    return "\n\x72 Git Worktree Information:"


def _format_current_worktree_info(worktree_info: Any) -> list[str]:
    """Format current worktree information."""
    output = []
    if worktree_info.is_main_worktree:
        output.append(
            f"   \x73 Current: Main repository on '{worktree_info.branch}'",
        )
    else:
        output.append(f"   \x73 Current: Worktree on '{worktree_info.branch}'")
        output.append(f"   \x72 Path: {worktree_info.path}")
    return output


def _format_worktree_count_info(all_worktrees: list[Any]) -> list[str]:
    """Format worktree count information."""
    output = []
    if len(all_worktrees) > 1:
        output.append(f"   \x74 Total worktrees: {len(all_worktrees)}")
    return output


def _format_other_branches_info(
    all_worktrees: list[Any], worktree_info: Any
) -> list[str]:
    """Format information about other branches."""
    output = []
    other_branches = [
        wt.branch for wt in all_worktrees if wt.path != worktree_info.path
    ]
    if other_branches:
        output.append(
            f"   \x75 Other branches: {', '.join(other_branches[:3])}",
        )
        if len(other_branches) > 3:
            output.append(f"   ... and {len(other_branches) - 3} more")
    return output


def _format_worktree_suggestions(all_worktrees: list[Any]) -> list[str]:
    """Format worktree-related suggestions."""
    output = []
    if len(all_worktrees) > 1:
        output.append("   \x74 Use 'git_worktree_list' to see all worktrees")
    else:
        output.append(
            "   \x74 Use 'git_worktree_add <branch> <path>' to create parallel worktrees",
        )
    return output


def _format_detached_head_warning(worktree_info: Any) -> list[str]:
    """Format detached HEAD warning if applicable."""
    output = []
    if worktree_info.is_detached:
        output.append("   \x77 Detached HEAD - consider checking out a branch")
    return output


async def _add_project_context_info(output: list[str], current_dir: Path) -> None:
    """Add project context information to output."""
    from .utils.git_operations import get_worktree_info, list_worktrees

    # Get project context information
    _project_context, context_score, max_score = await _get_project_context_info(
        current_dir
    )
    output.extend(_format_project_maturity_section(context_score, max_score))

    # Add worktree information
    from contextlib import suppress

    with suppress(Exception):
        worktree_info = get_worktree_info(current_dir)
        if worktree_info:
            all_worktrees = list_worktrees(current_dir)

            output.append(_format_git_worktree_header())
            output.extend(_format_current_worktree_info(worktree_info))

            output.extend(_format_worktree_count_info(all_worktrees))

            if len(all_worktrees) > 1:
                output.extend(_format_other_branches_info(all_worktrees, worktree_info))
                output.extend(_format_worktree_suggestions(all_worktrees))
            else:
                output.extend(_format_worktree_suggestions(all_worktrees))

            output.extend(_format_detached_head_warning(worktree_info))


def _add_permissions_info(output: list[str]) -> None:
    """Add permissions information to output."""
    permissions_status = permissions_manager.get_permission_status()
    output.append("\n🔐 Session Permissions:")
    output.append(
        f"   📊 Trusted operations: {permissions_status['trusted_operations_count']}",
    )
    if permissions_status["trusted_operations"]:
        for op in permissions_status["trusted_operations"]:
            output.append(f"   ✅ {op.replace('_', ' ').title()}")
    else:
        output.append("   ⚠️ No trusted operations yet - will prompt for permissions")


def _add_basic_tools_info(output: list[str]) -> None:
    """Add basic MCP tools information to output."""
    output.append("\n🛠️ Available MCP Tools:")
    output.append("• init - Full session initialization")
    output.append("• checkpoint - Quality monitoring")
    output.append("• end - Complete cleanup")
    output.append("• status - This status report with health checks")
    output.append("• permissions - Manage trusted operations")
    output.append("• git_worktree_list - List all git worktrees")
    output.append("• git_worktree_add - Create new worktrees")
    output.append("• git_worktree_remove - Remove worktrees")
    output.append("• git_worktree_status - Comprehensive worktree status")
    output.append("• git_worktree_prune - Clean up stale references")


def _add_feature_status_info(output: list[str]) -> None:
    """Add feature status information to output."""
    # Token Optimization Status
    if TOKEN_OPTIMIZER_AVAILABLE:
        output.append("\n⚡ Token Optimization:")
        output.append("• get_cached_chunk - Retrieve chunked response data")
        output.append("• get_token_usage_stats - Token usage and savings metrics")
        output.append("• optimize_memory_usage - Consolidate old conversations")
        output.append("• Built-in response chunking and truncation")

    # Multi-Project Coordination Status
    if MULTI_PROJECT_AVAILABLE:
        output.append("\n🔗 Multi-Project Coordination:")
        output.append("• create_project_group - Create project groups for coordination")
        output.append("• add_project_dependency - Define project relationships")
        output.append(
            "• search_across_projects - Search conversations across related projects",
        )
        output.append("• get_project_insights - Cross-project activity analysis")

    # Advanced Search Status
    if ADVANCED_SEARCH_AVAILABLE:
        output.append("\n🔍 Advanced Search:")
        output.append("• advanced_search - Faceted search with filtering")
        output.append("• search_suggestions - Auto-completion suggestions")
        output.append("• get_search_metrics - Search activity analytics")
        output.append("• Built-in full-text indexing and highlighting")


def _add_configuration_info(output: list[str]) -> None:
    """Add configuration information to output."""
    if CONFIG_AVAILABLE:
        output.append("\n⚙️ Configuration:")
        output.append("• pyproject.toml configuration support")
        output.append("• Environment variable overrides")
        output.append("• Configurable database, search, and optimization settings")

        # Show current optimization stats if available
        from contextlib import suppress

        with suppress(Exception):
            from .token_optimizer import get_token_optimizer

            optimizer = get_token_optimizer()
            usage_stats = optimizer.get_usage_stats(hours=24)

            if usage_stats["status"] == "success" and usage_stats["total_requests"] > 0:
                savings = usage_stats.get("estimated_cost_savings", {})
                if savings.get("savings_usd", 0) > 0:
                    output.append(
                        f"• Last 24h savings: ${savings['savings_usd']:.4f} USD, {savings['estimated_tokens_saved']:,} tokens",
                    )

            cache_size = len(optimizer.chunk_cache)
            if cache_size > 0:
                output.append(f"• Active cached chunks: {cache_size}")
    else:
        output.append("\n❌ Token optimization not available (install tiktoken)")


def _add_crackerjack_integration_info(output: list[str]) -> None:
    """Add Crackerjack integration information to output."""
    if CRACKERJACK_INTEGRATION_AVAILABLE:
        output.append("\n🔧 Crackerjack Integration (Enhanced):")
        output.append("\n🎯 RECOMMENDED COMMANDS (Enhanced with Memory & Analytics):")
        output.append(
            "• /session-mgmt:crackerjack-run <command> - Smart execution with insights",
        )
        output.append("• /session-mgmt:crackerjack-history - View trends and patterns")
        output.append("• /session-mgmt:crackerjack-metrics - Quality metrics over time")
        output.append("• /session-mgmt:crackerjack-patterns - Test failure analysis")
        output.append("• /session-mgmt:crackerjack-help - Complete command guide")

        # Detect if basic crackerjack is also available
        detected_servers = _detect_other_mcp_servers()
        if detected_servers.get("crackerjack", False):
            output.append("\n📋 Basic Commands (Raw Output Only):")
            output.append(
                "• /crackerjack:run <command> - Simple execution without memory",
            )
            output.append(
                "💡 Use enhanced commands above for better development experience",
            )

        output.append("\n🧠 Enhanced Features:")
        output.append("• Automatic conversation memory integration")
        output.append("• Quality metrics tracking and trends")
        output.append("• Intelligent insights and recommendations")
        output.append("• Test failure pattern detection")
    else:
        output.append("\n⚠️ Crackerjack Integration: Not available")


# Token optimization imports
try:
    # get_token_optimizer will be imported when needed
    import session_mgmt_mcp.token_optimizer  # noqa: F401

    TOKEN_OPTIMIZER_AVAILABLE = True
except ImportError:
    TOKEN_OPTIMIZER_AVAILABLE = False


# Reflection Tools


async def _perform_main_search(
    query: str,
    limit: int,
    min_score: float,
    current_proj: str | None,
) -> list[dict[str, Any]]:
    """Perform the main conversation search."""
    db = await get_reflection_database()
    return await db.search_conversations(
        query=query,
        limit=limit,
        min_score=min_score,
        project=current_proj,
    )


async def _retry_search_with_cleanup(
    query: str,
    limit: int,
    min_score: float,
    project: str | None,
) -> str:
    """Retry search after database cleanup."""
    try:
        from session_mgmt_mcp.reflection_tools import cleanup_reflection_database

        cleanup_reflection_database()
        db = await get_reflection_database()
        current_proj = project or get_current_project()

        results = await db.search_conversations(
            query=query,
            limit=limit,
            min_score=min_score,
            project=current_proj,
        )

        if not results:
            return f"🔍 No conversations found matching '{query}' (minimum similarity: {min_score})"

        output = []
        output.append(f"🔍 Found {len(results)} conversations matching '{query}'")
        output.append(f"📊 Project: {current_proj or 'All projects'}")
        output.append(f"🎯 Similarity threshold: {min_score}")
        output.append("")

        for i, result in enumerate(results, 1):
            score = result.get("score", 0)
            timestamp = result.get("timestamp", "Unknown time")
            content_preview = (
                result.get("content", "")[:200] + "..."
                if len(result.get("content", "")) > 200
                else result.get("content", "")
            )

            output.append(f"📝 Result {i} (similarity: {score:.3f})")
            output.append(f"📅 {timestamp}")
            output.append(f"💬 {content_preview}")
            output.append("")

        return "\n".join(output)
    except Exception as retry_e:
        return f"❌ Error searching conversations (retry failed): {retry_e}"


async def reflect_on_past(
    query: str,
    limit: int = 5,
    min_score: float = 0.7,
    project: str | None = None,
    optimize_tokens: bool = True,
    max_tokens: int = 4000,
) -> str:
    """Search past conversations and store reflections with semantic similarity."""
    if not REFLECTION_TOOLS_AVAILABLE:
        return "❌ Reflection tools not available. Install dependencies: pip install duckdb transformers"

    try:
        current_proj = project or get_current_project()
        results = await _perform_main_search(query, limit, min_score, current_proj)

        if not results:
            return f"🔍 No relevant conversations found for query: '{query}'\n💡 Try adjusting the search terms or lowering min_score."

        # Apply token optimization if available
        optimization_result = await _optimize_search_results_impl(
            results,
            optimize_tokens,
            max_tokens,
            query,
        )
        results = optimization_result["results"]
        optimization_info = optimization_result.get("optimization_info", {})

        # Build and format output
        output = _build_search_header(query, len(results), optimization_info)
        output.extend(_format_search_results(results))

        return "\n".join(output)

    except Exception as e:
        if _should_retry_search(e):
            return await _retry_search_with_cleanup(query, limit, min_score, project)
        return f"❌ Error searching conversations: {e}"


def _should_retry_search(error: Exception) -> bool:
    """Determine if a search error warrants a retry with cleanup."""
    # Retry for database connection issues or temporary errors
    error_msg = str(error).lower()
    retry_conditions = [
        "database is locked",
        "connection failed",
        "temporary failure",
        "timeout",
        "index not found",
    ]
    return any(condition in error_msg for condition in retry_conditions)


# Token Optimization Tools


# Enhanced Search Tools (Phase 1)


async def get_app_monitor() -> ApplicationMonitor | None:
    """Get or initialize application monitor."""
    global _app_monitor
    if not APP_MONITOR_AVAILABLE:
        return None

    if _app_monitor is None:
        data_dir = Path.home() / ".claude" / "data" / "app_monitoring"
        working_dir = os.environ.get("PWD", str(Path.cwd()))
        project_paths = [working_dir] if Path(working_dir).exists() else []
        _app_monitor = ApplicationMonitor(str(data_dir), project_paths)

    return _app_monitor


# Global instances
_llm_manager = None
_app_monitor = None


async def get_llm_manager() -> LLMManager | None:
    """Get or initialize LLM manager."""
    global _llm_manager
    if not LLM_PROVIDERS_AVAILABLE:
        return None

    if _llm_manager is None:
        config_path = Path.home() / ".claude" / "data" / "llm_config.json"
        _llm_manager = LLMManager(str(config_path) if config_path.exists() else None)

    return _llm_manager


# Global serverless session manager
_serverless_manager = None


async def get_serverless_manager() -> ServerlessSessionManager | None:
    """Get or initialize serverless session manager."""
    global _serverless_manager
    if not SERVERLESS_MODE_AVAILABLE:
        return None

    if _serverless_manager is None:
        config_path = Path.home() / ".claude" / "data" / "serverless_config.json"
        config = ServerlessConfigManager.load_config(
            str(config_path) if config_path.exists() else None,
        )
        storage_backend = ServerlessConfigManager.create_storage_backend(config)
        _serverless_manager = ServerlessSessionManager(storage_backend)

    return _serverless_manager


# Team Knowledge Base Tools
# Natural Language Scheduling Tools
@mcp.tool()
async def create_natural_reminder(
    title: str,
    time_expression: str,
    description: str = "",
    user_id: str = "default",
    project_id: str | None = None,
    notification_method: str = "session",
) -> str:
    """Create reminder from natural language time expression."""
    try:
        from .natural_scheduler import (
            create_natural_reminder as _create_natural_reminder,
        )

        reminder_id = await _create_natural_reminder(
            title,
            time_expression,
            description,
            user_id,
            project_id,
            notification_method,
        )

        if reminder_id:
            output = []
            output.append("⏰ Natural reminder created successfully!")
            output.append(f"🆔 Reminder ID: {reminder_id}")
            output.append(f"📝 Title: {title}")
            output.append(f"📄 Description: {description}")
            output.append(f"🕐 When: {time_expression}")
            output.append(f"👤 User: {user_id}")
            if project_id:
                output.append(f"📁 Project: {project_id}")
            output.append(f"📢 Notification: {notification_method}")
            output.append(
                "🎯 Reminder will trigger automatically at the scheduled time",
            )
            return "\n".join(output)
        return f"❌ Failed to parse time expression: '{time_expression}'\n💡 Try formats like 'in 30 minutes', 'tomorrow at 9am', 'every day at 5pm'"

    except ImportError:
        return "❌ Natural scheduling tools not available. Install: pip install python-dateutil schedule python-crontab"
    except Exception as e:
        return f"❌ Error creating reminder: {e}"


def _format_no_reminders_message(user_id: str, project_id: str | None) -> list[str]:
    """Format message when no reminders are found."""
    output = []
    output.append("📋 No pending reminders found")
    output.append(f"👤 User: {user_id}")
    if project_id:
        output.append(f"📁 Project: {project_id}")
    output.append(
        "💡 Use 'create_natural_reminder' to set up time-based reminders",
    )
    return output


def _format_reminders_header(
    reminders: list[dict[str, Any]], user_id: str, project_id: str | None
) -> list[str]:
    """Format header for reminders list."""
    output = []
    output.append(f"⏰ Found {len(reminders)} pending reminders")
    output.append(f"👤 User: {user_id}")
    if project_id:
        output.append(f"📁 Project: {project_id}")
    output.append("=" * 50)
    return output


def _format_single_reminder(reminder: dict[str, Any], index: int) -> list[str]:
    """Format a single reminder for display."""
    output = []
    output.append(f"\n#{index}")
    output.append(f"🆔 ID: {reminder['id']}")
    output.append(f"📝 Title: {reminder['title']}")

    if reminder["description"]:
        output.append(f"📄 Description: {reminder['description']}")

    output.append(
        f"🔄 Type: {reminder['reminder_type'].replace('_', ' ').title()}",
    )
    output.append(f"📊 Status: {reminder['status'].replace('_', ' ').title()}")
    output.append(f"🕐 Scheduled: {reminder['scheduled_for']}")
    output.append(f"📅 Created: {reminder['created_at']}")

    if reminder.get("recurrence_rule"):
        output.append(f"🔁 Recurrence: {reminder['recurrence_rule']}")
    if reminder.get("context_triggers"):
        output.append(f"🎯 Triggers: {', '.join(reminder['context_triggers'])}")

    return output


def _format_reminders_list(
    reminders: list[dict[str, Any]], user_id: str, project_id: str | None
) -> list[str]:
    """Format the complete reminders list."""
    output = _format_reminders_header(reminders, user_id, project_id)

    for i, reminder in enumerate(reminders, 1):
        output.extend(_format_single_reminder(reminder, i))

    return output


@mcp.tool()
async def list_user_reminders(
    user_id: str = "default",
    project_id: str | None = None,
) -> str:
    """List pending reminders for user/project."""
    try:
        from .natural_scheduler import list_user_reminders as _list_user_reminders

        reminders = await _list_user_reminders(user_id, project_id)

        if not reminders:
            output = _format_no_reminders_message(user_id, project_id)
            return "\n".join(output)

        output = _format_reminders_list(reminders, user_id, project_id)
        return "\n".join(output)

    except ImportError:
        return "❌ Natural scheduling tools not available"
    except Exception as e:
        return f"❌ Error listing reminders: {e}"


@mcp.tool()
async def cancel_user_reminder(reminder_id: str) -> str:
    """Cancel a specific reminder."""
    try:
        from .natural_scheduler import cancel_user_reminder as _cancel_user_reminder

        success = await _cancel_user_reminder(reminder_id)

        if success:
            output = []
            output.append("❌ Reminder cancelled successfully!")
            output.append(f"🆔 Reminder ID: {reminder_id}")
            output.append("🚫 The reminder will no longer trigger")
            output.append("💡 You can create a new reminder if needed")
            return "\n".join(output)
        return f"❌ Failed to cancel reminder {reminder_id}. Check that the ID is correct and the reminder exists."

    except ImportError:
        return "❌ Natural scheduling tools not available"
    except Exception as e:
        return f"❌ Error cancelling reminder: {e}"


def _format_reminder_basic_info(reminder: dict[str, Any], index: int) -> list[str]:
    """Format basic reminder information."""
    lines = [
        f"\n🔥 #{index} OVERDUE",
        f"🆔 ID: {reminder['id']}",
        f"📝 Title: {reminder['title']}",
    ]

    if reminder["description"]:
        lines.append(f"📄 Description: {reminder['description']}")

    lines.extend(
        [
            f"🕐 Scheduled: {reminder['scheduled_for']}",
            f"👤 User: {reminder['user_id']}",
        ]
    )

    if reminder.get("project_id"):
        lines.append(f"📁 Project: {reminder['project_id']}")

    return lines


def _calculate_overdue_time(scheduled_for: str) -> str:
    """Calculate and format overdue time."""
    try:
        from datetime import datetime

        scheduled = datetime.fromisoformat(scheduled_for)
        now = datetime.now()
        overdue = now - scheduled

        if overdue.total_seconds() > 0:
            hours = int(overdue.total_seconds() // 3600)
            minutes = int((overdue.total_seconds() % 3600) // 60)
            if hours > 0:
                return f"⏱️ Overdue: {hours}h {minutes}m"
            return f"⏱️ Overdue: {minutes}m"
        return "⏱️ Not yet due"
    except Exception as e:
        return f"❌ Error checking due reminders: {e}"


@mcp.tool()
async def start_reminder_service() -> str:
    """Start the background reminder service."""
    try:
        from .natural_scheduler import (
            register_session_notifications,
        )
        from .natural_scheduler import (
            start_reminder_service as _start_reminder_service,
        )

        # Register default session notifications
        register_session_notifications()

        # Start the service
        _start_reminder_service()

        output = []
        output.append("🚀 Natural reminder service started!")
        output.append("⏰ Background scheduler is now active")
        output.append("🔍 Checking for due reminders every minute")
        output.append("📢 Session notifications are registered")
        output.append(
            "💡 Reminders will automatically trigger at their scheduled times",
        )
        output.append("🛑 Use 'stop_reminder_service' to stop the background service")

        return "\n".join(output)

    except ImportError:
        return "❌ Natural scheduling tools not available"
    except Exception as e:
        return f"❌ Error starting reminder service: {e}"


@mcp.tool()
async def stop_reminder_service() -> str:
    """Stop the background reminder service."""
    try:
        from .natural_scheduler import stop_reminder_service as _stop_reminder_service

        _stop_reminder_service()

        output = []
        output.append("🛑 Natural reminder service stopped")
        output.append("❌ Background scheduler is no longer active")
        output.append("⚠️ Existing reminders will not trigger automatically")
        output.append("🚀 Use 'start_reminder_service' to restart the service")
        output.append(
            "💡 You can still check due reminders manually with 'check_due_reminders'",
        )

        return "\n".join(output)

    except ImportError:
        return "❌ Natural scheduling tools not available"
    except Exception as e:
        return f"❌ Error stopping reminder service: {e}"


# Smart Interruption Management Tools
@mcp.tool()
async def get_interruption_statistics(user_id: str) -> str:
    """Get comprehensive interruption and context preservation statistics."""
    try:
        from .interruption_manager import (
            get_interruption_statistics as _get_interruption_statistics,
        )

        stats = await _get_interruption_statistics(user_id)
        output = _format_statistics_header(user_id)

        # Get statistics sections
        sessions = stats.get("sessions", {})
        interruptions = stats.get("interruptions", {})
        snapshots = stats.get("snapshots", {})
        by_type = interruptions.get("by_type", [])

        # Format all sections
        output.extend(_format_session_statistics(sessions))
        output.extend(_format_interruption_statistics(interruptions))
        output.extend(_format_snapshot_statistics(snapshots))
        output.extend(_format_efficiency_metrics(sessions, interruptions, by_type))

        # Check if we have any data
        if not _has_statistics_data(sessions, interruptions, snapshots):
            output = _format_no_data_message(user_id)

        return "\n".join(output)

    except ImportError:
        return "❌ Interruption management tools not available"
    except Exception as e:
        return f"❌ Error getting statistics: {e}"


# =====================================
# Crackerjack Integration MCP Tools
# =====================================


# Clean Command Aliases
async def _format_conversation_summary() -> list[str]:
    """Format the conversation summary section."""
    output = []
    from contextlib import suppress

    with suppress(Exception):
        conversation_summary = await summarize_current_conversation()
        if conversation_summary["key_topics"]:
            output.append("\n💬 Current Session Focus:")
            for topic in conversation_summary["key_topics"][:3]:
                output.append(f"   • {topic}")

        if conversation_summary["decisions_made"]:
            output.append("\n✅ Key Decisions:")
            for decision in conversation_summary["decisions_made"][:2]:
                output.append(f"   • {decision}")
    return output


@mcp.tool()
async def create_project_group(
    name: str,
    projects: list[str],
    description: str = "",
) -> str:
    """Create a new project group for multi-project coordination."""
    if not multi_project_coordinator:
        await initialize_new_features()
        if not multi_project_coordinator:
            return "❌ Multi-project coordination not available"

    try:
        group = await multi_project_coordinator.create_project_group(
            name=name,
            projects=projects,
            description=description,
        )

        return f"""✅ **Project Group Created**

**Group:** {group.name}
**Projects:** {", ".join(group.projects)}
**Description:** {group.description or "None"}
**ID:** {group.id}

The project group is now available for cross-project coordination and knowledge sharing."""

    except Exception as e:
        return f"❌ Failed to create project group: {e}"


@mcp.tool()
async def add_project_dependency(
    source_project: str,
    target_project: str,
    dependency_type: Literal["uses", "extends", "references", "shares_code"],
    description: str = "",
) -> str:
    """Add a dependency relationship between projects."""
    if not multi_project_coordinator:
        await initialize_new_features()
        if not multi_project_coordinator:
            return "❌ Multi-project coordination not available"

    try:
        dependency = await multi_project_coordinator.add_project_dependency(
            source_project=source_project,
            target_project=target_project,
            dependency_type=dependency_type,
            description=description,
        )

        return f"""✅ **Project Dependency Added**

**Source:** {dependency.source_project}
**Target:** {dependency.target_project}
**Type:** {dependency.dependency_type}
**Description:** {dependency.description or "None"}

This relationship will be used for cross-project search and coordination."""

    except Exception as e:
        return f"❌ Failed to add project dependency: {e}"


@mcp.tool()
async def search_across_projects(
    query: str,
    current_project: str,
    limit: int = 10,
) -> str:
    """Search conversations across related projects."""
    if not multi_project_coordinator:
        await initialize_new_features()
        if not multi_project_coordinator:
            return "❌ Multi-project coordination not available"

    try:
        results = await multi_project_coordinator.find_related_conversations(
            current_project=current_project,
            query=query,
            limit=limit,
        )

        if not results:
            return f"🔍 No results found for '{query}' across related projects"

        output = [f"🔍 **Cross-Project Search Results** ({len(results)} found)\n"]

        for i, result in enumerate(results, 1):
            project_indicator = (
                "📍 Current"
                if result["is_current_project"]
                else f"🔗 {result['source_project']}"
            )

            output.append(f"""**{i}.** {project_indicator}
**Score:** {result["score"]:.3f}
**Content:** {result["content"][:200]}{"..." if len(result["content"]) > 200 else ""}
**Timestamp:** {result.get("timestamp", "Unknown")}
---""")

        return "\n".join(output)

    except Exception as e:
        return f"❌ Search failed: {e}"


@mcp.tool()
async def get_project_insights(projects: list[str], time_range_days: int = 30) -> str:
    """Get cross-project insights and collaboration opportunities."""
    if not multi_project_coordinator:
        await initialize_new_features()
        if not multi_project_coordinator:
            return "❌ Multi-project coordination not available"

    try:
        insights = await multi_project_coordinator.get_cross_project_insights(
            projects=projects,
            time_range_days=time_range_days,
        )
        return _format_project_insights(insights, time_range_days)

    except Exception as e:
        return f"❌ Failed to get insights: {e}"


def _format_project_insights(insights: dict[str, Any], time_range_days: int) -> str:
    """Format project insights for display."""
    output = [f"📊 **Cross-Project Insights** (Last {time_range_days} days)\n"]

    # Project activity
    if insights["project_activity"]:
        output.extend(_format_project_activity_section(insights["project_activity"]))

    # Common patterns
    if insights["common_patterns"]:
        output.extend(_format_common_patterns_section(insights["common_patterns"]))

    if not insights["project_activity"] and not insights["common_patterns"]:
        output.append("No insights available for the specified time range.")

    return "\n".join(output)


def _format_project_activity_section(project_activity: dict[str, Any]) -> list[str]:
    """Format project activity section."""
    output = ["**📈 Project Activity:**"]
    for project, stats in project_activity.items():
        output.append(
            f"• **{project}:** {stats['conversation_count']} conversations, last active: {stats.get('last_activity', 'Unknown')}"
        )
    output.append("")
    return output


def _format_common_patterns_section(common_patterns: list[dict[str, Any]]) -> list[str]:
    """Format common patterns section."""
    output = ["**🔍 Common Patterns:**"]
    for pattern in common_patterns[:5]:  # Top 5
        projects_str = ", ".join(pattern["projects"])
        output.append(
            f"• **{pattern['pattern']}** across {projects_str} (frequency: {pattern['frequency']})"
        )
    output.append("")
    return output


# Advanced Search Tools


@mcp.tool()
async def advanced_search(
    query: str,
    content_type: str | None = None,
    project: str | None = None,
    timeframe: str | None = None,
    sort_by: str = "relevance",
    limit: int = 10,
) -> str:
    """Perform advanced search with faceted filtering."""
    if not advanced_search_engine:
        await initialize_new_features()
        if not advanced_search_engine:
            return "❌ Advanced search not available"

    try:
        filters = _build_advanced_search_filters(content_type, project, timeframe)
        search_results = await advanced_search_engine.search(
            query=query,
            filters=filters,
            sort_by=sort_by,
            limit=limit,
            include_highlights=True,
        )

        results = search_results["results"]
        if not results:
            return f"🔍 No results found for '{query}'"

        return _format_advanced_search_results(results)

    except Exception as e:
        return f"❌ Advanced search failed: {e}"


def _build_advanced_search_filters(
    content_type: str | None, project: str | None, timeframe: str | None
) -> list[Any]:
    """Build search filters from parameters."""
    filters = []

    if content_type:
        from session_mgmt_mcp.advanced_search import SearchFilter

        filters.append(
            SearchFilter(field="content_type", operator="eq", value=content_type)
        )

    if project:
        from session_mgmt_mcp.advanced_search import SearchFilter

        filters.append(SearchFilter(field="project", operator="eq", value=project))

    if timeframe:
        from session_mgmt_mcp.advanced_search import SearchFilter

        start_time, end_time = advanced_search_engine._parse_timeframe(timeframe)
        filters.append(
            SearchFilter(
                field="timestamp", operator="range", value=(start_time, end_time)
            )
        )

    return filters


def _format_advanced_search_results(results: list[Any]) -> str:
    """Format advanced search results for display."""
    output = [f"🔍 **Advanced Search Results** ({len(results)} found)\n"]

    for i, result in enumerate(results, 1):
        output.append(f"""**{i}.** {result.title}
**Score:** {result.score:.3f} | **Project:** {result.project or "Unknown"}
**Content:** {result.content}
**Timestamp:** {result.timestamp}""")

        if result.highlights:
            output.append(f"**Highlights:** {'; '.join(result.highlights)}")

        output.append("---")

    return "\n".join(output)


@mcp.tool()
async def search_suggestions(query: str, field: str = "content", limit: int = 5) -> str:
    """Get search completion suggestions."""
    if not advanced_search_engine:
        await initialize_new_features()
        if not advanced_search_engine:
            return "❌ Advanced search not available"

    try:
        suggestions = await advanced_search_engine.suggest_completions(
            query=query,
            field=field,
            limit=limit,
        )

        if not suggestions:
            return f"💡 No suggestions found for '{query}'"

        output = [f"💡 **Search Suggestions** for '{query}':\n"]

        for i, suggestion in enumerate(suggestions, 1):
            output.append(
                f"{i}. {suggestion['text']} (frequency: {suggestion['frequency']})",
            )

        return "\n".join(output)

    except Exception as e:
        return f"❌ Failed to get suggestions: {e}"


@mcp.tool()
async def get_search_metrics(metric_type: str, timeframe: str = "30d") -> str:
    """Get search and activity metrics."""
    if not advanced_search_engine:
        await initialize_new_features()
        if not advanced_search_engine:
            return "❌ Advanced search not available"

    try:
        metrics = await advanced_search_engine.aggregate_metrics(
            metric_type=metric_type,
            timeframe=timeframe,
        )

        if "error" in metrics:
            return f"❌ {metrics['error']}"

        output = [f"📊 **{metric_type.title()} Metrics** ({timeframe})\n"]

        for item in metrics["data"][:10]:  # Top 10
            output.append(f"• **{item['key']}:** {item['value']}")

        if not metrics["data"]:
            output.append("No data available for the specified timeframe.")

        return "\n".join(output)

    except Exception as e:
        return f"❌ Failed to get metrics: {e}"


# Git Worktree Management Tools


def _format_worktree_status(wt: dict[str, Any]) -> str:
    """Format worktree status items."""
    status_items = []
    if wt["locked"]:
        status_items.append("🔒 locked")
    if wt["prunable"]:
        status_items.append("🗑️ prunable")
    if not wt["exists"]:
        status_items.append("❌ missing")
    if wt["has_session"]:
        status_items.append("🧠 has session")

    return ", ".join(status_items)


def _format_worktree_list_header(
    total_count: int, repo_name: str, current_worktree: str
) -> list[str]:
    """Format the header for the worktree list output."""
    return [
        f"🌿 **Git Worktrees** ({total_count} total)\\n",
        f"📂 Repository: {repo_name}",
        f"🎯 Current: {current_worktree}\\n",
    ]


def _get_worktree_indicators(is_main: bool, is_detached: bool) -> tuple[str, str]:
    """Get the main and detached indicators for a worktree."""
    main_indicator = " (main)" if is_main else ""
    detached_indicator = " (detached)" if is_detached else ""
    return main_indicator, detached_indicator


def _format_single_worktree(wt: dict[str, Any]) -> list[str]:
    """Format a single worktree entry."""
    output = []

    prefix = "🔸" if wt["is_current"] else "◦"
    main_indicator, detached_indicator = _get_worktree_indicators(
        wt["is_main"], wt["is_detached"]
    )

    output.append(
        f"{prefix} **{wt['branch']}{main_indicator}{detached_indicator}**",
    )
    output.append(f"   📁 {wt['path']}")

    status_line = _format_worktree_status(wt)
    if status_line:
        output.append(f"   Status: {status_line}")
    output.append("")

    return output


async def git_worktree_list(working_directory: str | None = None) -> str:
    """List all git worktrees for the current repository."""
    from .worktree_manager import WorktreeManager

    working_dir = Path(working_directory or str(Path.cwd()))
    manager = WorktreeManager(session_logger=session_logger)

    try:
        result = await manager.list_worktrees(working_dir)

        if not result["success"]:
            return f"❌ {result['error']}"

        worktrees = result["worktrees"]
        if not worktrees:
            return (
                "📝 No worktrees found. This repository only has the main working tree."
            )

        output = _format_worktree_list_header(
            result["total_count"],
            working_dir.name,
            result.get("current_worktree", "Unknown"),
        )

        for wt in worktrees:
            output.extend(_format_single_worktree(wt))

        return "\\n".join(output)

    except Exception as e:
        session_logger.exception(f"git_worktree_list failed: {e}")
        return f"❌ Failed to list worktrees: {e}"


@mcp.tool()
async def git_worktree_add(
    branch: str,
    path: str,
    working_directory: str | None = None,
    create_branch: bool = False,
) -> str:
    """Create a new git worktree."""
    from .worktree_manager import WorktreeManager

    working_dir = Path(working_directory or str(Path.cwd()))
    new_path = Path(path)

    if not new_path.is_absolute():
        new_path = working_dir.parent / path

    manager = WorktreeManager(session_logger=session_logger)

    try:
        result = await manager.create_worktree(
            repository_path=working_dir,
            new_path=new_path,
            branch=branch,
            create_branch=create_branch,
        )

        if not result["success"]:
            return f"❌ {result['error']}"

        output = [
            "🎉 **Worktree Created Successfully!**\n",
            f"🌿 Branch: {result['branch']}",
            f"📁 Path: {result['worktree_path']}",
            f"🎯 Created new branch: {'Yes' if create_branch else 'No'}",
        ]

        if result.get("output"):
            output.append(f"\n📝 Git output: {result['output']}")

        output.append(f"\n💡 To start working: cd {result['worktree_path']}")
        output.append("💡 Use `git_worktree_list` to see all worktrees")

        return "\n".join(output)

    except Exception as e:
        session_logger.exception(f"git_worktree_add failed: {e}")
        return f"❌ Failed to create worktree: {e}"


@mcp.tool()
async def git_worktree_remove(
    path: str,
    working_directory: str | None = None,
    force: bool = False,
) -> str:
    """Remove an existing git worktree."""
    from .worktree_manager import WorktreeManager

    working_dir = Path(working_directory or str(Path.cwd()))
    remove_path = Path(path)

    if not remove_path.is_absolute():
        remove_path = working_dir.parent / path

    manager = WorktreeManager(session_logger=session_logger)

    try:
        result = await manager.remove_worktree(
            repository_path=working_dir,
            worktree_path=remove_path,
            force=force,
        )

        if not result["success"]:
            return f"❌ {result['error']}"

        output = [
            "🗑️ **Worktree Removed Successfully!**\n",
            f"📁 Removed path: {result['removed_path']}",
        ]

        if result.get("output"):
            output.append(f"📝 Git output: {result['output']}")

        output.append(f"\n💡 Used force removal: {'Yes' if force else 'No'}")
        output.append("💡 Use `git_worktree_list` to see remaining worktrees")

        return "\n".join(output)

    except Exception as e:
        session_logger.exception(f"git_worktree_remove failed: {e}")
        return f"❌ Failed to remove worktree: {e}"


def _format_session_summary(result: dict[str, Any]) -> list[str]:
    """Format session summary across all worktrees."""
    session_summary = result["session_summary"]
    return [
        "📊 **Multi-Worktree Summary:**",
        f"• Total worktrees: {result['total_worktrees']}",
        f"• Active sessions: {session_summary['active_sessions']}",
        f"• Unique branches: {session_summary['unique_branches']}",
        f"• Branches: {', '.join(session_summary['branches'])}\n",
    ]


async def git_worktree_status(working_directory: str | None = None) -> str:
    """Get comprehensive status of the current git worktree."""
    from .worktree_manager import WorktreeManager

    working_dir = Path(working_directory or str(Path.cwd()))
    manager = WorktreeManager(session_logger=session_logger)

    try:
        result = await manager.get_worktree_status(working_dir)

        if not result["success"]:
            return f"❌ {result['error']}"

        return _format_worktree_status_display(result["status"], working_dir)

    except Exception as e:
        session_logger.exception(f"git_worktree_status failed: {e}")
        return f"❌ Failed to get worktree status: {e}"


def _format_worktree_status_display(
    status_info: dict[str, Any], working_dir: Path
) -> str:
    """Format worktree status information for display."""
    header = ["🌿 **Git Worktree Status**\n"]
    basic_info = _format_basic_worktree_info(status_info, working_dir)
    session_info = _format_session_info(status_info.get("session_info"))

    return "\n".join([*header, *basic_info, *session_info])


def _format_basic_worktree_info(
    status_info: dict[str, Any], working_dir: Path
) -> list[str]:
    """Format basic worktree information."""
    return [
        f"📂 Repository: {working_dir.name}",
        f"🎯 Current worktree: {status_info['branch']}",
        f"📁 Path: {status_info['path']}",
        f"🧠 Has session: {'Yes' if status_info['has_session'] else 'No'}",
        f"🔸 Detached HEAD: {'Yes' if status_info['is_detached'] else 'No'}\n",
    ]


def _format_session_info(session_info: dict[str, Any] | None) -> list[str]:
    """Format session information if available."""
    if not session_info:
        return []

    return [
        "📊 **Session Information:**",
        f"• Session ID: {session_info.get('session_id', 'N/A')}",
        f"• Last activity: {session_info.get('last_activity', 'Unknown')}",
        f"• Session duration: {session_info.get('duration', 'Unknown')}",
    ]


@mcp.tool()
async def git_worktree_switch(from_path: str, to_path: str) -> str:
    """Switch context between git worktrees with session preservation."""
    from pathlib import Path

    from .worktree_manager import WorktreeManager

    manager = WorktreeManager(session_logger=session_logger)

    try:
        result = await manager.switch_worktree_context(Path(from_path), Path(to_path))

        if not result["success"]:
            return f" {result['error']}"

        output = [
            "**Worktree Context Switch Complete**\n",
            f" From: {result['from_worktree']['branch']} ({result['from_worktree']['path']})",
            f" To: {result['to_worktree']['branch']} ({result['to_worktree']['path']})",
        ]

        if result["context_preserved"]:
            output.append(" Session context preserved during switch")
            if result.get("session_state_saved"):
                output.append(" Current session state saved")
            if result.get("session_state_restored"):
                output.append(" Session state restored for target worktree")
        else:
            output.append(
                " Session context preservation failed (basic switch performed)"
            )
            if result.get("session_error"):
                output.append(f"   Error: {result['session_error']}")

        return "\n".join(output)

    except Exception as e:
        session_logger.exception(f"git_worktree_switch failed: {e}")
        return f"❌ Failed to switch worktree context: {e}"


@mcp.tool()
async def session_welcome() -> str:
    """Display session connection information and previous session details."""
    global _connection_info

    if not _connection_info:
        return "ℹ️ Session information not available (may not be a git repository)"

    output = []
    output.append("🚀 Session Management Connected!")
    output.append("=" * 40)

    # Current session info
    output.append(f"📁 Project: {_connection_info['project']}")
    output.append(f"📊 Current quality score: {_connection_info['quality_score']}/100")
    output.append(f"🔗 Connection status: {_connection_info['connected_at']}")

    # Previous session info
    previous = _connection_info.get("previous_session")
    if previous:
        output.append("\n📋 Previous Session Summary:")
        output.append("-" * 30)

        if "ended_at" in previous:
            output.append(f"⏰ Last session ended: {previous['ended_at']}")
        if "quality_score" in previous:
            output.append(f"📈 Final score: {previous['quality_score']}")
        if "top_recommendation" in previous:
            output.append(f"💡 Key recommendation: {previous['top_recommendation']}")

        output.append("\n✨ Session continuity restored - your progress is preserved!")
    else:
        output.append("\n🌟 This is your first session in this project!")
        output.append("💡 Session data will be preserved for future continuity")

    # Current recommendations
    recommendations = _connection_info.get("recommendations", [])
    if recommendations:
        output.append("\n🎯 Current Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            output.append(f"   {i}. {rec}")

    output.append("\n🔧 Use other session-mgmt tools for:")
    output.append("   • /session-mgmt:status - Detailed project health")
    output.append("   • /session-mgmt:checkpoint - Mid-session quality check")
    output.append("   • /session-mgmt:end - Graceful session cleanup")

    # Clear the connection info after display
    _connection_info = None

    return "\n".join(output)


def main(http_mode: bool = False, http_port: int | None = None) -> None:
    """Main entry point for the MCP server."""
    # Initialize new features on startup
    import asyncio
    from contextlib import suppress

    with suppress(Exception):
        asyncio.run(initialize_new_features())

    # Get host and port from config
    host = _mcp_config.get("http_host", "127.0.0.1")
    port = http_port or _mcp_config.get("http_port", 8678)

    # Check configuration and command line flags
    config_http_enabled = _mcp_config.get("http_enabled", False)
    use_http = http_mode or config_http_enabled

    if use_http:
        print(
            f"Starting Session Management MCP HTTP Server on http://{host}:{port}/mcp",
            file=sys.stderr,
        )
        print(
            f"WebSocket Monitor: {_mcp_config.get('websocket_monitor_port', 8677)}",
            file=sys.stderr,
        )
        mcp.run(
            transport="streamable-http",
            host=host,
            port=port,
            path="/mcp",
            stateless_http=True,
        )
    else:
        print("Starting Session Management MCP Server in STDIO mode", file=sys.stderr)
        mcp.run(stateless_http=True)


def _ensure_default_recommendations(priority_actions: list[str]) -> list[str]:
    """Ensure we always have default recommendations available."""
    if not priority_actions:
        return [
            "Run quality checks with `crackerjack lint`",
            "Check test coverage with `pytest --cov`",
            "Review recent git commits for patterns",
        ]
    return priority_actions


def _format_interruption_statistics(interruptions: list[dict[str, Any]]) -> list[str]:
    """Format interruption statistics for display."""
    if not interruptions:
        return ["📊 **Interruption Patterns**: No recent interruptions"]

    output = ["📊 **Interruption Patterns**:"]
    total = len(interruptions)
    output.append(f"   • Total interruptions: {total}")

    # Group by type if available
    types: dict[str, int] = {}
    for interruption in interruptions:
        int_type = interruption.get("type", "unknown")
        types[int_type] = types.get(int_type, 0) + 1

    for int_type, count in types.items():
        output.append(f"   • {int_type}: {count}")

    return output


def _format_snapshot_statistics(snapshots: list[dict[str, Any]]) -> list[str]:
    """Format snapshot statistics for display."""
    if not snapshots:
        return ["💾 **Context Snapshots**: No snapshots available"]

    output = ["💾 **Context Snapshots**:"]
    output.append(f"   • Total snapshots: {len(snapshots)}")

    # Show most recent snapshot info
    if snapshots:
        recent = snapshots[-1]
        if "timestamp" in recent:
            output.append(f"   • Most recent: {recent['timestamp']}")
        if "size" in recent:
            output.append(f"   • Snapshot size: {recent['size']} bytes")

    return output


def _has_statistics_data(
    sessions: list[dict[str, Any]],
    interruptions: list[dict[str, Any]],
    snapshots: list[dict[str, Any]],
) -> bool:
    """Check if we have any statistics data to display."""
    return bool(sessions or interruptions or snapshots)


if __name__ == "__main__":
    import sys

    # Check for HTTP mode flags
    http_mode = "--http" in sys.argv
    http_port = None

    if "--http-port" in sys.argv:
        port_idx = sys.argv.index("--http-port")
        if port_idx + 1 < len(sys.argv):
            http_port = int(sys.argv[port_idx + 1])

    main(http_mode, http_port)
