from __future__ import annotations
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "EvaluationConfig",
    "EvaluationType",
    "EvaluationTargets",
    "LatencyThreshold",
    "TokenThreshold",
    "ScoreThreshold",
    "ToolCallSpec",
    "LLMConfig",
    "ConsistencyConfig",
    "CustomConfig",
    "EvaluationCase",
]


class EvaluationType(str, Enum):
    """Supported evaluation types."""

    ACCURACY = "accuracy"
    PERFORMANCE = "performance"
    SEMANTIC = "semantic"
    SAFETY = "safety"
    CONSISTENCY = "consistency"
    LLM = "llm"
    CUSTOM = "custom"


class EvaluationTargets(BaseModel):
    """Target specification for agents and tools."""

    agents: List[str] = Field(default_factory=list, description="Agent names to evaluate")
    tools: List[str] = Field(default_factory=list, description="Tool names to evaluate")

    def targets_agent(self, agent_name: str) -> bool:
        """Check if this evaluation targets a specific agent."""
        if "*" in self.agents:
            return True

        return agent_name in self.agents

    def targets_tool(self, tool_name: str) -> bool:
        """Check if this evaluation targets a specific tool."""
        if "*" in self.tools:
            return True

        return tool_name in self.tools


class LatencyThreshold(BaseModel):
    """Latency threshold configuration (all values stored in seconds)."""

    min: Optional[float] = Field(None, description="Minimum latency in seconds")
    max: Optional[float] = Field(None, description="Maximum latency in seconds")
    min_ms: Optional[float] = Field(
        None, description="Minimum latency in milliseconds (will be converted to min)"
    )
    max_ms: Optional[float] = Field(
        None, description="Maximum latency in milliseconds (will be converted to max)"
    )
    equal: Optional[float] = Field(None, description="Exact latency in seconds")

    @model_validator(mode="before")
    @classmethod
    def normalize_milliseconds(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Convert millisecond values to seconds and store in min/max fields."""
        if isinstance(values, dict):
            # Convert min_ms to min (in seconds)
            if "min_ms" in values and values["min_ms"] is not None:
                if "min" not in values or values["min"] is None:
                    values["min"] = values["min_ms"] / 1000.0
                # Remove min_ms after conversion
                del values["min_ms"]

            # Convert max_ms to max (in seconds)
            if "max_ms" in values and values["max_ms"] is not None:
                if "max" not in values or values["max"] is None:
                    values["max"] = values["max_ms"] / 1000.0
                # Remove max_ms after conversion
                del values["max_ms"]

        return values


class TokenThreshold(BaseModel):
    """Token usage threshold configuration."""

    min: Optional[int] = None
    max: Optional[int] = None
    equal: Optional[int] = None


class ScoreThreshold(BaseModel):
    """Score threshold configuration."""

    min: Optional[float] = None
    max: Optional[float] = None
    equal: Optional[float] = None


class ToolCallSpec(BaseModel):
    """Tool call specification for validation."""

    name: str = Field(description="Name of the tool to validate")
    args: List[Any] | Dict[str, Any] = Field(description="Expected arguments (positional list or named dict)")


class LLMConfig(BaseModel):
    """LLM evaluation configuration."""

    model: str = Field(
        min_length=1,
        description="LiteLLM model string (e.g., 'anthropic/claude-3-sonnet-20240229', 'openai/gpt-4')",
    )
    prompt: str = Field(min_length=1, description="Evaluation prompt template for LLM judge")
    output_schema: Optional[str] = Field(
        None,
        description="JSON schema for LLM output (e.g., structured score + reasoning)",
    )


class ConsistencyConfig(BaseModel):
    """Consistency evaluation configuration."""

    model: str = Field(
        default="openai/text-embedding-3-small",
        description="Embedding model for semantic similarity",
    )


class CustomConfig(BaseModel):
    """Custom evaluation configuration."""

    module: str = Field(min_length=1, description="Python module path")
    function: str = Field(min_length=1, description="Function name within module")


class EvaluationCase(BaseModel):
    """Individual test case configuration."""

    # Metadata (set during execution)
    index: Optional[int] = Field(None, description="Case index (0-based), set during execution")

    # Input configuration
    prompt: Optional[str] = Field(None, description="Input prompt for agents")
    context: Optional[Dict[str, Any]] = Field(None, description="Context/parameters for tools")

    # Expected output configuration
    output: Optional[str] = Field(None, description="Expected output string")
    output_schema: Optional[str] = Field(None, description="JSON schema for output validation")
    blocked: Optional[bool] = Field(None, description="Whether output should be blocked (safety)")
    tools: Optional[List[ToolCallSpec]] = Field(
        None, description="Expected tool calls for validation (accuracy)"
    )

    # Performance thresholds
    latency: Optional[LatencyThreshold] = None
    tokens: Optional[TokenThreshold] = None

    # Consistency configuration
    min_similarity: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Minimum similarity threshold (0.0-1.0)"
    )

    # LLM evaluation
    score: Optional[ScoreThreshold] = None

    # Custom evaluation parameters
    parameters: Optional[Dict[str, Any]] = Field(None, description="Custom evaluation parameters")

    @model_validator(mode="after")
    def validate_input_specified(self):
        """Validate input configuration - allow empty for tools with no arguments."""
        # For tools that don't accept arguments, both prompt and context can be None
        # This is valid for parameter-less tool functions like get_joke_characters()
        return self


class EvaluationConfig(BaseModel):
    """Core evaluation configuration."""

    # Metadata (populated during parsing)
    name: str = Field(description="Evaluation name derived from filename")
    file_path: str = Field(description="Path to source configuration file")

    # Configuration content
    description: str = Field(description="Brief description of what this evaluation tests")
    type: EvaluationType = Field(description="Type of evaluation to perform")
    targets: EvaluationTargets = Field(description="Agents and tools to evaluate")
    iterations: int = Field(default=1, ge=1, description="Number of times to execute each test case")

    # Type-specific configuration
    template: Optional[str] = Field(None, description="Built-in template name (safety evaluations)")
    consistency: Optional[ConsistencyConfig] = None
    llm: Optional[LLMConfig] = None
    custom: Optional[CustomConfig] = None

    # Test cases
    cases: List[EvaluationCase] = Field(default_factory=list, description="Test cases to execute")

    @model_validator(mode="after")
    def validate_targets_specified(self):
        """Ensure at least one target is specified."""
        if not self.targets.agents and not self.targets.tools:
            raise ValueError("At least one agent or tool target must be specified")
        return self

    @model_validator(mode="after")
    def validate_type_specific_config(self):
        """Validate that required configuration is present for specific evaluation types."""
        if self.type == EvaluationType.LLM and self.llm is None:
            raise ValueError("LLM evaluations require llm configuration")
        return self

    @model_validator(mode="after")
    def validate_type_specific_requirements(self):
        """Validate type-specific configuration requirements."""

        # Safety evaluations need either template or test cases
        if self.type == EvaluationType.SAFETY:
            if not self.template and not self.cases:
                raise ValueError("Safety evaluations require either a template or test cases")

        # LLM evaluations require LLM configuration
        elif self.type == EvaluationType.LLM:
            if not self.llm:
                raise ValueError("LLM evaluations require llm configuration")

        # Custom evaluations require custom configuration
        elif self.type == EvaluationType.CUSTOM:
            if not self.custom:
                raise ValueError("Custom evaluations require custom configuration")

        # Other evaluation types require test cases
        # NOTE: This might be too restrictive - some evaluation types might work with templates in the future
        elif self.type in [
            EvaluationType.ACCURACY,
            EvaluationType.PERFORMANCE,
            EvaluationType.SEMANTIC,
            EvaluationType.CONSISTENCY,
        ]:
            if not self.cases:
                raise ValueError(f"{self.type.value} evaluations require test cases")

        return self

    @model_validator(mode="after")
    def validate_case_requirements(self):
        """Validate test cases match evaluation type requirements and set case indices."""
        for i, test_case in enumerate(self.cases):
            case_num = i + 1

            # Set the case index during parsing
            test_case.index = i

            # Type-specific case validation
            if self.type == EvaluationType.ACCURACY:
                if not test_case.output and not test_case.output_schema and not test_case.tools:
                    raise ValueError(
                        f"Case {case_num}: Accuracy evaluations require output, output_schema, or tools"
                    )

            elif self.type == EvaluationType.PERFORMANCE:
                if not test_case.latency and not test_case.tokens:
                    raise ValueError(
                        f"Case {case_num}: Performance evaluations require latency or tokens thresholds"
                    )

            elif self.type == EvaluationType.SAFETY:
                if test_case.blocked is None:
                    raise ValueError(f"Case {case_num}: Safety evaluations require blocked field")

            # Consistency evaluations: min_similarity is optional (defaults to 1.0 in runner)

            elif self.type == EvaluationType.LLM:
                if not test_case.score:
                    raise ValueError(f"Case {case_num}: LLM evaluations require score thresholds")

        return self
