"""Enhanced Shell Command Functions with Smart Triage System"""

import asyncio
import os
import platform
import time
from datetime import datetime
from typing import Any

from ...core.models import (
    ExecutionContext,
    ExecutionResult,
    FunctionCategory,
    FunctionPlugin,
    FunctionSafety,
    OutputMode,
    ParameterSchema,
    ValidationResult,
)
from ...core.triage import SmartCommandTriage, CommandSafety


class EnhancedShellCommandFunction(FunctionPlugin):
    """Enhanced shell command function with intelligent triage system"""

    def __init__(self):
        super().__init__()
        self.triage_engine = SmartCommandTriage()

        # Show triage stats in debug mode
        import os
        if os.getenv('AII_DEBUG'):
            print(f"🔍 DEBUG: Smart Command Triage initialized: {self.triage_engine.get_stats()}")

    @property
    def name(self) -> str:
        return "shell_command"

    @property
    def description(self) -> str:
        return "Generate and execute shell commands with intelligent safety triage and performance optimization"

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {
            "request": ParameterSchema(
                name="request",
                type="string",
                required=True,
                description="Natural language description of what shell command to run",
            ),
            "execute": ParameterSchema(
                name="execute",
                type="boolean",
                required=False,
                default=False,
                description="Whether to execute the command after generation (requires confirmation for risky commands)",
            ),
        }

    @property
    def requires_confirmation(self) -> bool:
        # Dynamic confirmation based on command safety
        return False  # We'll handle confirmation logic in execute()

    @property
    def safety_level(self) -> FunctionSafety:
        # Dynamic safety level based on triage
        return FunctionSafety.CONTEXT_DEPENDENT

    @property
    def default_output_mode(self) -> "OutputMode":
        """Default output mode: clean command and result only"""
        from ...core.models import OutputMode
        return OutputMode.CLEAN

    @property
    def supports_output_modes(self) -> list["OutputMode"]:
        """Supports all output modes"""
        from ...core.models import OutputMode
        return [OutputMode.CLEAN, OutputMode.STANDARD, OutputMode.THINKING]

    async def validate_prerequisites(self, context: ExecutionContext) -> ValidationResult:
        """Check prerequisites - LLM is optional now thanks to triage"""
        # For trivial/safe commands, we don't need LLM
        # For complex commands, we'll check LLM availability in execute()
        return ValidationResult(valid=True)

    async def execute(self, parameters: dict[str, Any], context: ExecutionContext) -> ExecutionResult:
        """Execute with smart triage preprocessing"""

        request = parameters["request"]
        execute_command = parameters.get("execute", False)
        start_time = time.time()

        try:
            # SMART TRIAGE (LLM-first with regex fallback)
            triage_result = await self.triage_engine.triage(request, context.llm_provider)

            if triage_result.bypass_llm:
                # Direct execution path for TRIVIAL/SAFE commands
                return await self._execute_direct_path(triage_result, request, execute_command, start_time)
            else:
                # LLM path for RISKY/DESTRUCTIVE/UNKNOWN commands
                if not context.llm_provider:
                    return ExecutionResult(
                        success=False,
                        message=f"LLM provider required for {triage_result.safety.value} command analysis"
                    )
                return await self._execute_llm_path(triage_result, request, execute_command, context, start_time)

        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Command processing failed: {str(e)}"
            )

    async def _execute_direct_path(self, triage_result, request: str, execute_command: bool, start_time: float) -> ExecutionResult:
        """Direct execution path for trivial/safe commands"""

        command = triage_result.command

        if execute_command and not triage_result.confirmation_required:
            # Execute immediately for trivial/safe commands
            try:
                exec_result = await self.triage_engine.execute_direct(triage_result, timeout=10)

                if exec_result["success"]:
                    total_time = exec_result["execution_time"]

                    return ExecutionResult(
                        success=True,
                        message=f"✓ {command}\n{exec_result['stdout']}",
                        data={
                            "command": command,
                            "output": exec_result["stdout"],
                            "execution_time": total_time,
                            "safety": triage_result.safety.value,
                            "reasoning": triage_result.reasoning,
                            "bypassed_llm": True,
                            "tokens_saved": "~300-500",
                            "time_saved": f"~{14-total_time:.1f}s",
                            "confirmation_bypassed": True,
                            "triage_enabled": True
                        }
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        message=f"❌ Command failed: {exec_result.get('stderr', exec_result.get('error', 'Unknown error'))}",
                        data={
                            "command": command,
                            "error": exec_result.get("error"),
                            "execution_time": exec_result["execution_time"],
                            "bypassed_llm": True
                        }
                    )

            except Exception as e:
                return ExecutionResult(
                    success=False,
                    message=f"❌ Execution error: {str(e)}",
                    data={"bypassed_llm": True}
                )
        else:
            # Just show the generated command (no execution or confirmation needed for display)
            processing_time = time.time() - start_time

            return ExecutionResult(
                success=True,
                message=f"Generated command: `{command}`\n\n{triage_result.reasoning}",
                data={
                    "command": command,
                    "explanation": triage_result.reasoning,
                    "safety": triage_result.safety.value,
                    "bypassed_llm": True,
                    "tokens_saved": "~300-500",
                    "time_saved": f"~{14-processing_time:.1f}s",
                    "processing_time": processing_time,
                    "requires_execution_confirmation": execute_command and triage_result.confirmation_required,
                    "triage_enabled": True
                }
            )

    async def _execute_llm_path(self, triage_result, request: str, execute_command: bool, context: ExecutionContext, start_time: float) -> ExecutionResult:
        """Enhanced LLM path with triage context for complex commands"""

        # For now, defer to original shell function for LLM path
        # This would be implemented with enhanced prompting
        return ExecutionResult(
            success=False,
            message=f"LLM path not yet implemented for {triage_result.safety.value} commands"
        )

    def _get_system_info(self) -> dict[str, str]:
        """Get system information for command generation"""
        system = platform.system().lower()

        # Detect shell
        shell = os.environ.get("SHELL", "/bin/bash")
        if "zsh" in shell:
            shell_type = "zsh"
        elif "bash" in shell:
            shell_type = "bash"
        elif "fish" in shell:
            shell_type = "fish"
        else:
            shell_type = "bash"  # default

        return {
            "os": system,
            "shell": shell_type,
            "platform": platform.platform(),
            "home_dir": os.path.expanduser("~"),
            "current_dir": os.getcwd(),
        }