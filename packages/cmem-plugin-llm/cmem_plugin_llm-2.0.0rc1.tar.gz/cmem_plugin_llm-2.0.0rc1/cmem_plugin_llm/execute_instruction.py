"""Execute Instructions Plugin"""

import asyncio
import json
from collections.abc import AsyncGenerator, Generator, Sequence
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from cmem_plugin_base.dataintegration.context import (
    ExecutionContext,
    ExecutionReport,
)
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntityPath,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.parameter.code import JinjaCode, JsonCode, PythonCode
from cmem_plugin_base.dataintegration.parameter.password import Password
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import (
    FixedNumberOfInputs,
    FixedSchemaPort,
    FlexibleSchemaPort,
)
from cmem_plugin_base.dataintegration.types import EnumParameterType
from jinja2 import Template, UndefinedError
from openai import APIError, AsyncAzureOpenAI, AsyncOpenAI, NotGiven
from pydantic import BaseModel

from cmem_plugin_llm.commons import (
    APIType,
    OpenAPIModel,
    SamePathError,
    SharedParams,
    extract_variables_from_template,
)

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam

MESSAGES_TEMPLATE_EXAMPLE = JsonCode("""[
    {
        "role": "developer",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "{{ instruction_prompt }}"
    }
]""")


PYDANTIC_SCHEMA_EXAMPLE = PythonCode("""from pydantic import BaseModel

class StructuredOutput(BaseModel):
    title: str
    abstract: str
    keywords: list[str]
""")


class OutputFormat(Enum):
    """The output format"""

    TEXT = 1
    STRUCTURED_OUTPUT = 2
    JSON_MODE = 3


class Params:
    """Plugin parameters"""

    model = PluginParameter(
        name="model",
        label="Instruct Model",
        description="""The identifier of the instruct model to use.

Note that some provider do not support a model list endpoint.
Just create a custom entry then.

Available model IDs for some public providers can be found here:
[Claude](https://docs.claude.com/en/docs/about-claude/models/overview),
[OpenRouter](https://openrouter.ai/models),
[Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure).
""",
        default_value="gpt-4o-mini",
        param_type=OpenAPIModel(),
    )
    instruct_prompt_template = PluginParameter(
        name="instruct_prompt_template",
        label="Instruction Prompt Template",
        description="""The instruction prompt template.
Please have a look at the task documentation for detailed instructions.""",
        default_value=JinjaCode("""Write a paragraph about this entity: {{ entity }}"""),
    )
    temperature = PluginParameter(
        name="temperature",
        label="Temperature (between 0 and 2)",
        description="""A parameter that controls the randomness and creativity of the model.

A high temperature value (`0.8` - `1.0`) increases randomness and creativity.
This is useful for open-ended tasks like storytelling or brainstorming.
A low temperature value (`0.0` - `0.4`) produces more deterministic and focused outputs.
This is suitable for factual or technical tasks.""",
        default_value=1.0,
        advanced=True,
    )
    timeout = PluginParameter(
        name="timeout",
        label="Timeout (seconds)",
        description="The timeout for a single API request in seconds.",
        advanced=True,
        default_value=300,
    )
    instruction_output_path = PluginParameter(
        name="instruction_output_path",
        label="Instruction Output Path",
        description="The entity path where the instruction result will be provided.",
        advanced=True,
        default_value="_instruction_output",
    )
    messages_template = PluginParameter(
        name="messages_template",
        label="Messages Template",
        description="""A list of messages comprising the conversation compatible with OpenAI
        chat completion API message object.

        Have look at [Message roles and instruction following](https://platform.openai.com/docs/guides/text#message-roles-and-instruction-following)
        to learn about different levels of priority to messages with different roles.
        """,
        advanced=True,
        default_value=MESSAGES_TEMPLATE_EXAMPLE,
    )
    output_format = PluginParameter(
        name="output_format",
        label="Output Format",
        description="""Specifying the format that the model must output.

Possible values are `TEXT` - Standard text output, `STRUCTURED_OUTPUT` - output follows a given
schema. Add your schema as Pydantic model in the parameter below, `JSON_MODE` - a more basic
version of the structured outputs feature where you have to add your structure to the prompt
template.
""",
        param_type=EnumParameterType(enum_type=OutputFormat),
        default_value=OutputFormat.TEXT,
        advanced=True,
    )
    pydantic_schema = PluginParameter(
        name="pydantic_schema",
        label="Pydantic Schema",
        description="""The Pydantic schema definition with a mandatory class named
`StructuredOutput(BaseModel)`. This is only used in combination with the Structured Output format.

A schema may have up to 100 object properties total, with up to 5 levels of nesting.
The total string length of all property names, definition names, enum values,
and const values cannot exceed 15,000 characters.""",
        default_value=PYDANTIC_SCHEMA_EXAMPLE,
        advanced=True,
    )
    raise_on_error = PluginParameter(
        name="raise_on_error",
        label="Raise on API errors",
        description="""How to react on API errors.

When enable, any API errors will cause the workflow to stop with an exception.
When disabled, API errors are logged and the error message is written to the entity output,
allowing the workflow to continue processing other entities.
        """,
        default_value=True,
        advanced=True,
    )
    max_concurrent_requests = PluginParameter(
        name="max_concurrent_requests",
        label="Maximum Concurrent Requests",
        description="Maximum number of concurrent API requests to prevent rate limiting "
        "and resource exhaustion.",
        default_value=10,
        advanced=True,
    )
    batch_size = PluginParameter(
        name="batch_size",
        label="Batch Size",
        description="Number of entities to process in each batch for memory optimization.",
        default_value=100,
        advanced=True,
    )
    request_delay = PluginParameter(
        name="request_delay",
        label="Request Delay (seconds)",
        description="Delay between API requests in seconds to respect rate limits.",
        default_value=0.0,
        advanced=True,
    )

    def as_list(self) -> list[PluginParameter]:
        """Provide all parameters as list"""
        return [
            getattr(self, attr)
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        ]


@Plugin(
    label="Execute Instructions",
    plugin_id="cmem_plugin_llm-ExecuteInstructions",
    icon=Icon(package=__package__, file_name="execute_instruction.svg"),
    parameters=[
        SharedParams.base_url,
        SharedParams.api_type,
        SharedParams.api_key,
        SharedParams.api_version,
        *Params().as_list(),
    ],
    description="Send instructions (prompt) to an LLM and process the result.",
    documentation="""
## Overview

This plugin executes Large Language Model (LLM) instructions over entity collections, enabling
AI-powered text generation, analysis, and transformation tasks within Corporate Memory workflows.

## Core Functionality

- **LLM Integration**: Supports OpenAI API, Azure OpenAI, and OpenAI-compatible endpoints
  (Anthropic Claude, OpenRouter, etc.)
- **Entity Processing**: Processes entities individually or in batches with configurable
  concurrency
- **Template System**: Uses Jinja2 templates for dynamic prompt generation from entity data
- **Output Formats**: Supports text, JSON mode, and structured outputs with Pydantic schemas
- **Performance Optimization**: Includes batching, rate limiting, and async processing for
  high-throughput scenarios

## Input/Output Behavior

After processing, each entity receives an additional path (default: `_instruction_output`)
containing the LLM response. Input/output ports are automatically configured based on
template variables:

- **No placeholders**: No input ports required
- **With placeholders**: Single input port created for entity data
- **Schema handling**: Fixed schemas when using specific entity paths, flexible schemas otherwise

## Template System

Uses Jinja2 templating for dynamic prompts:

```jinja2
{{ entity }}           # Entire entity as JSON
{{ entity.name }}      # Specific entity property
```

The following template processing rules are implemented:

1. **Variable Extraction**: Automatically detects template variables to configure input ports
2. **Entity Iteration**: Processes entities from the single input port individually
3. **Single Entity Context**: Each entity is processed independently with its own template context

## Output Formats

1. **Text Output (Default)** - Standard LLM text responses for general-purpose tasks.
2. **JSON Mode** - Ensures valid JSON output format. Add JSON structure requirements
   to your prompt template.
3. **Structured Output** - Uses Pydantic schemas for type-safe, validated responses:

```python
from pydantic import BaseModel

class StructuredOutput(BaseModel):
    title: str
    summary: str
    keywords: list[str]
    confidence_score: float
```

## Performance Features

Parallel Processing:
- **Concurrent Requests**: Configurable semaphore-controlled API calls
- **Batch Processing**: Entities processed in configurable batch sizes
- **Rate Limiting**: Optional delays between requests
- **Memory Optimization**: Streaming processing with generator patterns

Error Handling:
- **Graceful Degradation**: Continue processing on API errors (configurable)
- **Detailed Logging**: Comprehensive error reporting and debugging information
- **Workflow Integration**: Proper cancellation support and progress reporting

## API Compatibility

Supported Providers:
- **OpenAI**: Direct API access with full feature support
- **Azure OpenAI**: Enterprise Azure-hosted services with API versioning
- **OpenAI-Compatible**: Anthropic Claude, OpenRouter, local models, and other compatible endpoints

Authentication:
- **API Keys**: Secure password-type parameters for API authentication
- **Azure Integration**: Supports Azure OpenAI API versioning and endpoint configuration
- **Flexible Endpoints**: Custom base URLs for various providers

## Advanced Configuration

### Message Templates
Customize the conversation structure beyond simple prompts:

```json
[
    {"role": "system", "content": "You are a data analyst."},
    {"role": "user", "content": "{{ instruction_prompt }}"}
]
```

### Performance Tuning
- **Temperature Control**: Adjust creativity vs. determinism (0.0-2.0)
- **Timeout Management**: Request-level timeout configuration
- **Concurrency Limits**: Prevent rate limiting with request throttling
- **Batch Optimization**: Balance memory usage vs. throughput

## Best Practices

1. **Schema Design**: Use specific entity paths in templates for fixed schemas
2. **Error Strategy**: Enable error continuation for large datasets
3. **Performance**: Adjust concurrency and batch size based on API limits
4. **Templates**: Design prompts with clear instructions and expected outputs
5. **Testing**: Start with small entity sets to validate templates and outputs

For detailed prompting guidance, see [OpenAI's Text Generation Guide](https://platform.openai.com/docs/guides/text?api-mode=chat).
""",
)
class ExecuteInstruction(WorkflowPlugin):
    """Execute Instructions from OpenAI completion API endpoint over entities"""

    execution_context: ExecutionContext
    instruction_output_path: str
    execution_report: ExecutionReport
    messages_template: str
    instruct_prompt_template: str
    client: AsyncOpenAI | AsyncAzureOpenAI
    model: str
    output_format: OutputFormat
    pydantic_schema: str
    raise_on_error: bool
    max_concurrent_requests: int
    batch_size: int
    request_delay: float

    def __init__(  # noqa: PLR0913
        self,
        base_url: str,
        api_type: APIType,
        api_key: Password | str = "",
        api_version: str = "",
        model: str = Params.model.default_value,
        temperature: float = Params.temperature.default_value,
        timeout: float = Params.timeout.default_value,
        instruction_output_path: str = Params.instruction_output_path.default_value,
        messages_template: JsonCode = MESSAGES_TEMPLATE_EXAMPLE,
        instruct_prompt_template: JinjaCode = Params.instruct_prompt_template.default_value,
        output_format: OutputFormat = Params.output_format.default_value,
        pydantic_schema: PythonCode = Params.pydantic_schema.default_value,
        raise_on_error: bool = Params.raise_on_error.default_value,
        max_concurrent_requests: int = Params.max_concurrent_requests.default_value,
        batch_size: int = Params.batch_size.default_value,
        request_delay: float = Params.request_delay.default_value,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key if isinstance(api_key, str) else api_key.decrypt()
        if self.api_key == "":
            self.api_key = "dummy-key"
        self.temperature = temperature
        self.timeout = timeout

        # Initialize the appropriate client based on API type
        if api_type.value == APIType.AZURE_OPENAI.value:
            self.client = AsyncAzureOpenAI(
                api_key=self.api_key,
                api_version=api_version,
                azure_endpoint=self.base_url,
                timeout=self.timeout,
            )
        else:
            self.client = AsyncOpenAI(
                base_url=self.base_url, api_key=self.api_key, timeout=self.timeout
            )
        self.instruction_output_path = instruction_output_path
        self.messages_template = str(messages_template)
        self.instruct_prompt_template = str(instruct_prompt_template)
        self.model = model
        self.output_format = output_format
        self.pydantic_schema = str(pydantic_schema)
        self.raise_on_error = raise_on_error
        self.max_concurrent_requests = max_concurrent_requests
        self.batch_size = batch_size
        self.request_delay = request_delay
        self.execution_report = ExecutionReport()
        self.execution_report.operation = "executing"
        self.execution_report.operation_desc = "instructions executed"
        self.base_template_variables, self.explicit_template_variables = (
            extract_variables_from_template(self.instruct_prompt_template)
        )
        self.sorted_template_variables = self._get_sorted_template_variables()
        self._setup_ports()

    def _get_sorted_template_variables(self) -> list[str]:
        """Get entity template variables as sorted list"""
        entity_variables = [
            explicit_var[explicit_var.find(".") + 1 :]
            for explicit_var in self.explicit_template_variables
            if explicit_var.startswith("entity.")
        ]
        return sorted(entity_variables)

    def _setup_ports(self) -> None:
        """Configure input and output ports depending on the configuration"""
        instruct_output_path = EntityPath(path=self.instruction_output_path)
        if not self.base_template_variables:
            # no input data used, so input port closed and output port minimal schema
            self.input_ports = FixedNumberOfInputs([])
            output_schema = EntitySchema(type_uri="entity", paths=[instruct_output_path])
            self.output_port = FixedSchemaPort(schema=output_schema)
        else:
            # since we only allow 'entity' as undeclared variable, create single input port
            entity_paths = self.sorted_template_variables

            if entity_paths and "entity" not in self.explicit_template_variables:
                # if entity has specific paths, use fixed schema port
                _paths = [EntityPath(path=path) for path in entity_paths]
                input_schema = EntitySchema(type_uri="entity", paths=_paths)
                input_port = FixedSchemaPort(schema=input_schema)

                # output schema includes input paths plus instruction output
                output_paths = [*_paths, instruct_output_path]
                output_schema = EntitySchema(type_uri="entity", paths=output_paths)
                self.output_port = FixedSchemaPort(schema=output_schema)
            else:
                # if entity has no specific paths, use flexible schema port
                input_port = FlexibleSchemaPort()
                self.output_port = FlexibleSchemaPort()

            # always create exactly one input port
            self.input_ports = FixedNumberOfInputs([input_port])

    def _cancel_workflow(self) -> bool:
        """Cancel workflow"""
        try:
            if self.execution_context.workflow.status() == "Canceling":
                self.log.info("End task (Cancelled Workflow).")
                return True
        except AttributeError:
            pass
        return False

    def _instruct_report_update(self, n: int) -> None:
        """Update report"""
        if hasattr(self.execution_context, "report"):
            self.execution_report.entity_count += n
            self.execution_context.report.update(self.execution_report)

    @staticmethod
    def _entity_to_dict(paths: Sequence[EntityPath], entity: Entity) -> dict[str, list[str]]:
        """Create a dict representation of an entity"""
        entity_dic: dict[str, list[str]] = {}
        for key, value in zip(paths, entity.values, strict=False):
            entity_dic[key.path] = list(value)
        return entity_dic

    @staticmethod
    def _render_messages_template(template: str, instruction_prompt: str) -> str:
        """Fill jinja template with string"""
        if "instruction_prompt" not in template:
            raise KeyError("instruction_prompt key not found in template")
        try:
            return Template(template).render(instruction_prompt=instruction_prompt)
        except UndefinedError as error:
            raise KeyError("Could not render jinja template") from error

    @staticmethod
    def _fill_jinja_template(template: str, mapping: dict[str, dict[str, list[str]]]) -> str:
        """Fill jinja template"""
        try:
            return Template(template).render(mapping)
        except UndefinedError as error:
            raise KeyError("Could not render jinja template") from error

    def validate_template_mapping(self, mapping: dict[str, dict[str, list[str]]]) -> None:
        """Validate template mapping"""
        for base_var in self.base_template_variables:
            if base_var not in mapping:
                raise KeyError(f"Variable {base_var} has no mapping")
            for sub_var in self.explicit_template_variables:
                if (
                    sub_var.startswith(f"{base_var}.")
                    and sub_var.split(".")[1] not in mapping[base_var]
                ):
                    raise KeyError(f"Variable {sub_var} has no mapping")

    def _handle_api_error(self, api_error: APIError, entity: Entity) -> str:
        """Handle API errors with configurable raise behavior"""
        self.log.error(f"OpenAI API error for entity {entity.uri}: {api_error}")
        if self.raise_on_error:
            raise api_error
        return f"API Error: {api_error}"

    def _handle_unexpected_error(self, error: Exception, entity: Entity) -> str:
        """Handle unexpected errors with configurable raise behavior"""
        self.log.error(f"Unexpected error for entity {entity.uri}: {error}")
        if self.raise_on_error:
            raise error
        return f"Error: {error}"

    async def _execute_llm_request_with_controls(
        self, semaphore: asyncio.Semaphore, messages: list[dict], entity: Entity
    ) -> tuple[str, Entity]:
        """Execute LLM request with semaphore control and rate limiting"""
        async with semaphore:
            if self.request_delay > 0:
                await asyncio.sleep(self.request_delay)
            return await self._execute_llm_request(messages, entity)

    async def _execute_llm_request(
        self, messages: list[dict], entity: Entity
    ) -> tuple[str, Entity]:
        """Execute LLM request based on output format and return result"""
        try:
            result = ""
            typed_messages = cast("list[ChatCompletionMessageParam]", messages)
            match self.output_format.name:
                case OutputFormat.TEXT.name:
                    completion = await self.client.chat.completions.create(
                        model=self.model, messages=typed_messages, temperature=self.temperature
                    )
                    result = completion.choices[0].message.content or ""
                case OutputFormat.JSON_MODE.name:
                    completion = await self.client.chat.completions.create(
                        model=self.model,
                        messages=typed_messages,
                        temperature=self.temperature,
                        response_format={"type": "json_object"},  # type: ignore[call-overload]
                    )
                    result = completion.choices[0].message.content or ""
                case OutputFormat.STRUCTURED_OUTPUT.name:
                    namespace: dict[str, Any] = {}
                    exec(self.pydantic_schema, namespace)  # noqa: S102
                    pydantic_classes = {
                        name: cls
                        for name, cls in namespace.items()
                        if isinstance(cls, type)
                        and issubclass(cls, namespace.get("BaseModel", BaseModel))
                        and cls is not namespace["BaseModel"]
                    }
                    structured_output_cls = pydantic_classes.get("StructuredOutput")
                    response_format = (
                        structured_output_cls if structured_output_cls is not None else NotGiven
                    )
                    completion = await self.client.beta.chat.completions.parse(
                        model=self.model,
                        messages=typed_messages,
                        temperature=self.temperature,
                        response_format=response_format,
                    )
                    parsed_output = completion.choices[0].message.parsed
                    result = (
                        parsed_output.model_dump_json()  # type: ignore[attr-defined]
                        if parsed_output and hasattr(parsed_output, "model_dump_json")
                        else ""
                    )
        except APIError as api_error:
            return self._handle_api_error(api_error, entity), entity
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            return self._handle_unexpected_error(error, entity), entity
        else:
            return result, entity

    async def _process_entities_async(self, entities: Entities) -> list[Entity]:
        return [result async for result in self._process_entities_generator(entities)]

    def _create_entity_batches(self, entities: Entities) -> Generator[list[Entity], None, None]:
        """Create batches of entities for processing"""
        entity_list = []
        for entity in entities.entities:
            entity_list.append(entity)
            if len(entity_list) >= self.batch_size:
                yield entity_list
                entity_list = []
        if entity_list:
            yield entity_list

    async def _process_batch(
        self,
        semaphore: asyncio.Semaphore,
        batch: list[Entity],
        entities_schema: Sequence[EntityPath],
    ) -> list[Entity]:
        """Process a batch of entities with concurrency control"""
        tasks = []

        for entity in batch:
            instruct: str = self.instruct_prompt_template
            if self.base_template_variables:
                # Create mapping for this entity
                mapping = self._create_entity_mapping(entity, entities_schema)
                self.validate_template_mapping(mapping)
                instruct = self._fill_jinja_template(self.instruct_prompt_template, mapping)

            try:
                messages = json.loads(self.messages_template)
            except json.decoder.JSONDecodeError as error:
                raise ValueError("Could not decode messages object") from error

            user_message = messages[1]["content"]
            user_message_rendered: str = self._render_messages_template(user_message, instruct)
            messages[1]["content"] = user_message_rendered

            # Create task with semaphore and rate limiting controls
            task = asyncio.create_task(
                self._execute_llm_request_with_controls(semaphore, messages, entity)
            )
            tasks.append(task)

        # Wait for all tasks in this batch to complete
        results = await asyncio.gather(*tasks)

        # Convert results to output entities
        output_entities = []
        for result, entity in results:
            entity_dict = self._entity_to_dict(entities_schema, entity)
            entity_dict[self.instruction_output_path] = [result]
            values = list(entity_dict.values())
            output_entities.append(Entity(uri=entity.uri, values=values))

        return output_entities

    async def _process_entities_generator(self, entities: Entities) -> AsyncGenerator[Entity, None]:
        """Process entities through LLM with optimized batching and concurrency control"""
        self._instruct_report_update(0)

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        # Process batches sequentially to maintain streaming and memory efficiency
        for batch_idx, batch in enumerate(self._create_entity_batches(entities)):
            if self._cancel_workflow():
                break

            self.log.debug(f"Processing batch {batch_idx + 1} entities")

            # Process the batch with concurrency control
            processed_entities = await self._process_batch(semaphore, batch, entities.schema.paths)

            # Yield entities as they become available
            for entity in processed_entities:
                self._instruct_report_update(1)
                yield entity

    def _create_entity_mapping(
        self, entity: Entity, schema_paths: Sequence[EntityPath]
    ) -> dict[str, dict[str, list[str]]]:
        """Create mapping for template rendering from a single entity."""
        if self.base_template_variables:
            # Create mapping with 'entity' key
            entity_dict = self._entity_to_dict(schema_paths, entity)
            return {"entity": entity_dict}
        return {}

    def _generate_output_schema(self, input_schema: EntitySchema) -> EntitySchema:
        """Get output schema"""
        paths = list(input_schema.paths).copy()
        paths.append(EntityPath(self.instruction_output_path))
        return EntitySchema(type_uri=input_schema.type_uri, paths=paths)

    def execute(
        self,
        inputs: Sequence[Entities],
        context: ExecutionContext,
    ) -> Entities:
        """Run the workflow operator."""
        self.log.info("Start")
        self.execution_context = context
        try:
            first_input: Entities = inputs[0]
        except IndexError:
            # if we have no input, we create a single input with a Null entity
            first_input = Entities(
                entities=iter([Entity(uri="urn:x-ecc:null", values=[])]),
                schema=EntitySchema(type_uri="urn:x-ecc:null-type", paths=[]),
            )
        if self.instruction_output_path in [_.path for _ in first_input.schema.paths]:
            raise SamePathError(self.instruction_output_path)

        # Use streaming generator that yields entities as each batch completes
        def streaming_entity_generator() -> Generator[Entity, None, None]:
            """Yield entities immediately as batches are processed"""

            async def async_processor() -> AsyncGenerator[Entity, None]:
                async for entity in self._process_entities_generator(first_input):
                    yield entity

            # Run async generator in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                generator = async_processor()
                while True:
                    try:
                        yield loop.run_until_complete(generator.__anext__())
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()

        schema = self._generate_output_schema(first_input.schema)
        self.log.info("End")
        return Entities(entities=streaming_entity_generator(), schema=schema)
