"""
Trace capture functionality for Dasein.
"""

import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from langchain_core.tools import BaseTool


# ============================================================================
# VERBOSE LOGGING HELPER
# ============================================================================

def _vprint(message: str, verbose: bool = False, force: bool = False):
    """
    Helper function for verbose printing.
    
    Args:
        message: Message to print
        verbose: Whether verbose mode is enabled
        force: If True, always print regardless of verbose setting
    """
    if force or verbose:
        print(message)


# DEPRECATED: Global trace store removed for thread-safety
# Traces are now stored instance-level in DaseinCallbackHandler._trace
# _TRACE: List[Dict[str, Any]] = []

# Hook cache for agent fingerprinting
_HOOK_CACHE: Dict[str, Any] = {}

# Store for modified tool inputs
_MODIFIED_TOOL_INPUTS: Dict[str, str] = {}


class DaseinToolWrapper(BaseTool):
    """Wrapper for tools that applies micro-turn modifications."""
    
    name: str = ""
    description: str = ""
    original_tool: Any = None
    callback_handler: Any = None
    
    def __init__(self, original_tool, callback_handler=None, verbose: bool = False):
        super().__init__(
            name=original_tool.name,
            description=original_tool.description
        )
        self.original_tool = original_tool
        self.callback_handler = callback_handler
        self._verbose = verbose
    
    def _vprint(self, message: str, force: bool = False):
        """Helper for verbose printing."""
        _vprint(message, self._verbose, force)
    
    def _run(self, *args, **kwargs):
        """Run the tool with micro-turn injection at execution level."""
        self._vprint(f"[DASEIN][TOOL_WRAPPER] _run called for {self.name} - VERSION 2.0")
        self._vprint(f"[DASEIN][TOOL_WRAPPER] Args: {args}")
        self._vprint(f"[DASEIN][TOOL_WRAPPER] Kwargs: {kwargs}")
        
        try:
            # Get the original input
            original_input = args[0] if args else ""
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Original input: {original_input[:100]}...")
            
            # Apply micro-turn injection if we have rules
            modified_input = self._apply_micro_turn_injection(str(original_input))
            
            if modified_input != original_input:
                self._vprint(f"[DASEIN][TOOL_WRAPPER] Applied micro-turn injection for {self.name}: {original_input[:50]}... -> {modified_input[:50]}...")
                # Use modified input
                result = self.original_tool._run(modified_input, *args[1:], **kwargs)
            else:
                self._vprint(f"[DASEIN][TOOL_WRAPPER] No micro-turn injection applied for {self.name}")
                # Use original input
                result = self.original_tool._run(*args, **kwargs)
            
            # Capture the tool output in the trace
            self._vprint(f"[DASEIN][TOOL_WRAPPER] About to capture tool output for {self.name}")
            self._capture_tool_output(self.name, args, kwargs, result)
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Finished capturing tool output for {self.name}")
            
            return result
            
        except Exception as e:
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Exception in _run: {e}")
            import traceback
            traceback.print_exc()
            # Still try to call the original tool
            result = self.original_tool._run(*args, **kwargs)
            return result
    
    def invoke(self, input_data, config=None, **kwargs):
        """Invoke the tool with micro-turn injection."""
        # Get the original input
        original_input = str(input_data)
        
        # Apply micro-turn injection if we have rules
        modified_input = self._apply_micro_turn_injection(original_input)
        
        if modified_input != original_input:
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Applied micro-turn injection for {self.name}: {original_input[:50]}... -> {modified_input[:50]}...")
            # Use modified input
            return self.original_tool.invoke(modified_input, config, **kwargs)
        else:
            # Use original input
            return self.original_tool.invoke(input_data, config, **kwargs)
    
    async def _arun(self, *args, **kwargs):
        """Async run the tool with micro-turn injection at execution level."""
        self._vprint(f"[DASEIN][TOOL_WRAPPER] _arun called for {self.name} - ASYNC VERSION")
        self._vprint(f"[DASEIN][TOOL_WRAPPER] Args: {args}")
        self._vprint(f"[DASEIN][TOOL_WRAPPER] Kwargs: {kwargs}")
        
        try:
            # Get the original input
            original_input = args[0] if args else ""
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Original input: {original_input[:100]}...")
            
            # Apply micro-turn injection if we have rules
            modified_input = self._apply_micro_turn_injection(str(original_input))
            
            if modified_input != original_input:
                self._vprint(f"[DASEIN][TOOL_WRAPPER] Applied micro-turn injection for {self.name}: {original_input[:50]}... -> {modified_input[:50]}...")
                # Use modified input
                result = await self.original_tool._arun(modified_input, *args[1:], **kwargs)
            else:
                self._vprint(f"[DASEIN][TOOL_WRAPPER] No micro-turn injection applied for {self.name}")
                # Use original input
                result = await self.original_tool._arun(*args, **kwargs)
            
            # Capture the tool output in the trace
            self._vprint(f"[DASEIN][TOOL_WRAPPER] About to capture tool output for {self.name}")
            self._capture_tool_output(self.name, args, kwargs, result)
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Finished capturing tool output for {self.name}")
            
            return result
            
        except Exception as e:
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Exception in _arun: {e}")
            import traceback
            traceback.print_exc()
            # Still try to call the original tool
            result = await self.original_tool._arun(*args, **kwargs)
            return result
    
    async def ainvoke(self, input_data, config=None, **kwargs):
        """Async invoke the tool with micro-turn injection."""
        self._vprint(f"[DASEIN][TOOL_WRAPPER] ainvoke called for {self.name} - ASYNC VERSION")
        
        # Get the original input
        original_input = str(input_data)
        
        # Apply micro-turn injection if we have rules
        modified_input = self._apply_micro_turn_injection(original_input)
        
        if modified_input != original_input:
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Applied micro-turn injection for {self.name}: {original_input[:50]}... -> {modified_input[:50]}...")
            # Use modified input
            return await self.original_tool.ainvoke(modified_input, config, **kwargs)
        else:
            # Use original input
            return await self.original_tool.ainvoke(input_data, config, **kwargs)
    
    def _apply_micro_turn_injection(self, original_input: str) -> str:
        """Apply micro-turn injection to the tool input."""
        try:
            # Check if we have a callback handler with rules and LLM
            if not self.callback_handler:
                return original_input
                
            # Normalize selected rules into Rule objects (handle (rule, metadata) tuples)
            normalized_rules = []
            for rule_meta in getattr(self.callback_handler, "_selected_rules", []) or []:
                if isinstance(rule_meta, tuple) and len(rule_meta) == 2:
                    rule_obj, _metadata = rule_meta
                else:
                    rule_obj = rule_meta
                normalized_rules.append(rule_obj)
                
            # Filter tool_start rules
            tool_rules = [r for r in normalized_rules if getattr(r, 'target_step_type', '') == "tool_start"]
            
            if not tool_rules:
                self._vprint(f"[DASEIN][MICROTURN] No tool rules selected - skipping micro-turn for {self.name}")
                return original_input
                
            # Check if any rule covers this tool
            covered_rules = [rule for rule in tool_rules 
                             if self._rule_covers_tool(rule, self.name, original_input)]
            
            if not covered_rules:
                return original_input
                
            # Fire micro-turn LLM call (use first matching rule)
            rule = covered_rules[0]
            self._vprint(f"[DASEIN][MICROTURN] rule_id={rule.id} tool={self.name}")
            
            # Create micro-turn prompt
            micro_turn_prompt = self._create_micro_turn_prompt(rule, self.name, original_input)
            
            # Execute micro-turn LLM call
            modified_input = self._execute_micro_turn_llm_call(micro_turn_prompt, original_input)
            
            self._vprint(f"[DASEIN][MICROTURN] Applied rule {rule.id}: {str(original_input)[:50]}... -> {str(modified_input)[:50]}...")
            return modified_input
            
        except Exception as e:
            self._vprint(f"[DASEIN][MICROTURN] Error in micro-turn injection: {e}")
            return original_input
    
    def _rule_covers_tool(self, rule, tool_name: str, tool_input: str) -> bool:
        """Check if a rule covers this tool call."""
        if not hasattr(rule, 'references') or not rule.references:
            return False
            
        # Check if the rule references this tool
        tools = rule.references.get('tools', [])
        return tool_name in tools
    
    def _create_micro_turn_prompt(self, rule, tool_name: str, tool_input: str) -> str:
        """Create the prompt for the micro-turn LLM call."""
        return f"""You are applying a rule to fix a tool input.

Rule: {rule.advice_text}

Tool: {tool_name}
Current Input: {tool_input}

Apply the rule to fix the input. Return only the corrected input, nothing else."""

    def _execute_micro_turn_llm_call(self, prompt: str, original_input: str) -> str:
        """Execute the actual micro-turn LLM call."""
        try:
            if not self.callback_handler or not self.callback_handler._llm:
                self._vprint(f"[DASEIN][MICROTURN] No LLM available for micro-turn call")
                return original_input

            self._vprint(f"[DASEIN][MICROTURN] Executing micro-turn LLM call")
            self._vprint(f"[DASEIN][MICROTURN] Prompt: {prompt[:200]}...")

            # Make the micro-turn LLM call
            messages = [{"role": "user", "content": prompt}]
            response = self.callback_handler._llm.invoke(messages)

            # Extract the response content
            if hasattr(response, 'content'):
                modified_input = response.content.strip()
            elif isinstance(response, str):
                modified_input = response.strip()
            else:
                modified_input = str(response).strip()

            self._vprint(f"[DASEIN][MICROTURN] LLM response: {modified_input[:100]}...")

            # 🚨 CRITICAL: Parse JSON responses with markdown fences
            if modified_input.startswith('```json') or modified_input.startswith('```'):
                try:
                    # Extract JSON from markdown fences
                    import re
                    import json
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', modified_input, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        parsed_json = json.loads(json_str)
                        # Convert back to the expected format
                        if isinstance(parsed_json, dict) and 'name' in parsed_json and 'args' in parsed_json:
                            modified_input = parsed_json
                            self._vprint(f"[DASEIN][MICROTURN] Parsed JSON from markdown fences: {parsed_json}")
                        else:
                            self._vprint(f"[DASEIN][MICROTURN] JSON doesn't have expected structure, using as-is")
                    else:
                        self._vprint(f"[DASEIN][MICROTURN] Could not extract JSON from markdown fences")
                except Exception as e:
                    self._vprint(f"[DASEIN][MICROTURN] Error parsing JSON: {e}")

            # Validate the response - only fallback if completely empty
            if not modified_input:
                self._vprint(f"[DASEIN][MICROTURN] LLM response empty, using original input")
                return original_input

            return modified_input

        except Exception as e:
            self._vprint(f"[DASEIN][MICROTURN] Error executing micro-turn LLM call: {e}")
            return original_input
    
    def _capture_tool_output(self, tool_name, args, kwargs, result):
        """Capture tool output in the trace."""
        try:
            # Create args excerpt
            args_str = str(args) if args else ""
            if len(args_str) > 1000:
                args_str = args_str[:1000] + "..."
            
            # Create result excerpt (with 10k limit)
            result_str = str(result) if result else ""
            if len(result_str) > 10000:
                result_str = result_str[:10000] + "..."
            
            # Add tool_end step to trace
            step = {
                "step_type": "tool_end",
                "tool_name": tool_name,
                "args_excerpt": args_str,
                "outcome": result_str,
                "ts": datetime.now().isoformat(),
                "run_id": f"tool_{id(self)}_{datetime.now().timestamp()}",
                "parent_run_id": None,
            }
            
            # Add to LLM wrapper's trace if available
            if self.callback_handler and hasattr(self.callback_handler, '_llm') and self.callback_handler._llm:
                if hasattr(self.callback_handler._llm, '_trace'):
                    self.callback_handler._llm._trace.append(step)
                    self._vprint(f"[DASEIN][TOOL_WRAPPER] Added to LLM wrapper trace")
                else:
                    self._vprint(f"[DASEIN][TOOL_WRAPPER] LLM wrapper has no _trace attribute")
            else:
                self._vprint(f"[DASEIN][TOOL_WRAPPER] No LLM wrapper available")
            
            # Also add to callback handler's trace if it has one
            if self.callback_handler and hasattr(self.callback_handler, '_trace'):
                self.callback_handler._trace.append(step)
                self._vprint(f"[DASEIN][TOOL_WRAPPER] Added to callback handler trace")
            
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Captured tool output for {tool_name}")
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Output length: {len(result_str)} chars")
            self._vprint(f"[DASEIN][TOOL_WRAPPER] First 200 chars: {result_str[:200]}")
            if self.callback_handler and hasattr(self.callback_handler, '_trace'):
                self._vprint(f"[DASEIN][TOOL_WRAPPER] Callback handler trace length after capture: {len(self.callback_handler._trace)}")
            
        except Exception as e:
            self._vprint(f"[DASEIN][TOOL_WRAPPER] Error capturing tool output: {e}")


class DaseinCallbackHandler(BaseCallbackHandler):
    """
    Callback handler that captures step-by-step traces and implements rule injection.
    """
    
    def __init__(self, weights=None, llm=None, is_langgraph=False, coordinator_node=None, planning_nodes=None, verbose: bool = False):
        super().__init__()
        self._weights = weights
        self._selected_rules = []  # Rules selected for this run
        self._injection_guard = set()  # Prevent duplicate injections
        self._last_modified_prompts = []  # Store modified prompts for LLM wrapper
        self._llm = llm  # Store reference to LLM for micro-turn calls
        self._tool_name_by_run_id = {}  # Track tool names by run_id
        self._discovered_tools = set()  # Track tools discovered during execution
        self._wrapped_dynamic_tools = {}  # Cache of wrapped dynamic tools
        self._is_langgraph = is_langgraph  # Flag to skip planning rule injection for LangGraph
        self._coordinator_node = coordinator_node  # Coordinator node (for future targeted injection)
        self._planning_nodes = planning_nodes if planning_nodes else set()  # Planning-capable nodes (including subgraph children)
        self._current_chain_node = None  # Track current LangGraph node
        self._agent_was_recreated = False  # Track if agent was successfully recreated
        self._function_calls_made = {}  # Track function calls: {function_name: [{'step': N, 'ts': timestamp}]}
        self._trace = []  # Instance-level trace storage (not global) for thread-safety
        self._verbose = verbose
        self._start_times = {}  # Track start times for duration calculation: {step_index: datetime}
        self._vprint(f"[DASEIN][CALLBACK] Initialized callback handler (LangGraph: {is_langgraph})")
        if coordinator_node:
            self._vprint(f"[DASEIN][CALLBACK] Coordinator: {coordinator_node}")
        if planning_nodes:
            self._vprint(f"[DASEIN][CALLBACK] Planning nodes: {planning_nodes}")
        self._vprint(f"[DASEIN][CALLBACK] Dynamic tool detection enabled (tools discovered at runtime)")
    
    def _vprint(self, message: str, force: bool = False):
        """Helper for verbose printing."""
        _vprint(message, self._verbose, force)
    
    def reset_run_state(self):
        """Reset state that should be cleared between runs."""
        self._function_calls_made = {}
        self._injection_guard = set()
        self._trace = []  # Clear instance trace
        self._start_times = {}  # Clear start times
        self._vprint(f"[DASEIN][CALLBACK] Reset run state (trace, function calls, injection guard, and start times cleared)")
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        """Called when an LLM starts running."""
        model_name = serialized.get("name", "unknown") if serialized else "unknown"
        
        # 🎯 CRITICAL: Track current node from kwargs metadata (LangGraph includes langgraph_node)
        if self._is_langgraph and 'metadata' in kwargs and isinstance(kwargs['metadata'], dict):
            if 'langgraph_node' in kwargs['metadata']:
                node_name = kwargs['metadata']['langgraph_node']
                self._current_chain_node = node_name
        
        # Inject rules if applicable
        modified_prompts = self._inject_rule_if_applicable("llm_start", model_name, prompts)
        
        # Store the modified prompts for the LLM wrapper to use
        self._last_modified_prompts = modified_prompts
        
        # 🚨 OPTIMIZED: For LangGraph, check if kwargs contains 'invocation_params' with messages
        # Extract the most recent message instead of full history
        # Use from_end=True to capture the END of system prompts (where user's actual query is)
        if 'invocation_params' in kwargs and 'messages' in kwargs['invocation_params']:
            args_excerpt = self._extract_recent_message({'messages': kwargs['invocation_params']['messages']})
        else:
            args_excerpt = self._excerpt(" | ".join(modified_prompts), from_end=True)
        
        # GNN-related fields
        step_index = len(self._trace)
        
        # Track which rules triggered at this step (llm_start rules)
        rule_triggered_here = []
        if hasattr(self, '_selected_rules') and self._selected_rules:
            for rule_meta in self._selected_rules:
                if isinstance(rule_meta, tuple) and len(rule_meta) == 2:
                    rule_obj, _metadata = rule_meta
                else:
                    rule_obj = rule_meta
                target_step_type = getattr(rule_obj, 'target_step_type', '')
                if target_step_type in ['llm_start', 'chain_start']:
                    rule_triggered_here.append(getattr(rule_obj, 'id', 'unknown'))
        
        # Record start time for duration calculation
        start_time = datetime.now()
        self._start_times[step_index] = start_time
        
        step = {
            "step_type": "llm_start",
            "tool_name": model_name,
            "args_excerpt": args_excerpt,
            "outcome": "",
            "ts": start_time.isoformat(),
            "run_id": None,
            "parent_run_id": None,
            "node": self._current_chain_node,  # LangGraph node name (if available)
            # GNN step-level fields
            "step_index": step_index,
            "rule_triggered_here": rule_triggered_here,
        }
        self._trace.append(step)
        # self._vprint(f"[DASEIN][CALLBACK] Captured llm_start: {len(_TRACE)} total steps")  # Commented out - too noisy
    
    def on_llm_end(
        self,
        response: Any,
        **kwargs: Any,
    ) -> None:
        """Called when an LLM ends running."""
        outcome = ""
        try:
            # Debug: Print ALL available data to see what we're getting
            # print(f"[DEBUG] on_llm_end called")
            # print(f"  response type: {type(response)}")
            # print(f"  kwargs keys: {kwargs.keys()}")
            
            # Try multiple extraction strategies
            # Strategy 1: Standard LangChain LLMResult structure
            if hasattr(response, 'generations') and response.generations:
                if len(response.generations) > 0:
                    first_gen = response.generations[0]
                    if isinstance(first_gen, list) and len(first_gen) > 0:
                        generation = first_gen[0]
                    else:
                        generation = first_gen
                    
                    # Try multiple content fields
                    if hasattr(generation, 'text') and generation.text:
                        outcome = self._excerpt(generation.text)
                    elif hasattr(generation, 'message'):
                        if hasattr(generation.message, 'content'):
                            outcome = self._excerpt(generation.message.content)
                        elif hasattr(generation.message, 'text'):
                            outcome = self._excerpt(generation.message.text)
                    elif hasattr(generation, 'content'):
                        outcome = self._excerpt(generation.content)
                    else:
                        outcome = self._excerpt(str(generation))
            
            # Strategy 2: Check if response itself has content
            elif hasattr(response, 'content'):
                outcome = self._excerpt(response.content)
            
            # Strategy 3: Check kwargs for output/response
            elif 'output' in kwargs:
                outcome = self._excerpt(str(kwargs['output']))
            elif 'result' in kwargs:
                outcome = self._excerpt(str(kwargs['result']))
            
            # Fallback
            if not outcome:
                outcome = self._excerpt(str(response))
            
            # Debug: Warn if still empty
            if not outcome or len(outcome) == 0:
                self._vprint(f"[DASEIN][CALLBACK] WARNING: on_llm_end got empty outcome!")
                print(f"  Response: {str(response)[:200]}")
                print(f"  kwargs keys: {list(kwargs.keys())}")
                
        except (AttributeError, IndexError, TypeError) as e:
            self._vprint(f"[DASEIN][CALLBACK] Error in on_llm_end: {e}")
            outcome = self._excerpt(str(response))
        
        # 🎯 CRITICAL: Extract function calls for state tracking (agent-agnostic)
        try:
            if hasattr(response, 'generations') and response.generations:
                first_gen = response.generations[0]
                if isinstance(first_gen, list) and len(first_gen) > 0:
                    generation = first_gen[0]
                else:
                    generation = first_gen
                
                # Check for function_call in message additional_kwargs
                if hasattr(generation, 'message') and hasattr(generation.message, 'additional_kwargs'):
                    func_call = generation.message.additional_kwargs.get('function_call')
                    if func_call and isinstance(func_call, dict) and 'name' in func_call:
                        func_name = func_call['name']
                        step_num = len(self._trace)
                        
                        # Extract arguments and create preview
                        args_str = func_call.get('arguments', '')
                        preview = ''
                        if args_str and len(args_str) > 0:
                            # Take first 100 chars as preview
                            preview = args_str[:100].replace('\n', ' ').replace('\r', '')
                            if len(args_str) > 100:
                                preview += '...'
                        
                        call_info = {
                            'step': step_num,
                            'ts': datetime.now().isoformat(),
                            'preview': preview
                        }
                        
                        if func_name not in self._function_calls_made:
                            self._function_calls_made[func_name] = []
                        self._function_calls_made[func_name].append(call_info)
                        
                        self._vprint(f"[DASEIN][STATE] Tracked function call: {func_name} (count: {len(self._function_calls_made[func_name])})")
        except Exception as e:
            pass  # Silently skip if function call extraction fails
        
        # Extract token usage from response metadata
        input_tokens = 0
        output_tokens = 0
        try:
            # DEBUG: Print response structure for first LLM call
            # Uncomment to see token structure:
            # import json
            # print(f"[DEBUG] Response structure:")
            # print(f"  Has llm_output: {hasattr(response, 'llm_output')}")
            # if hasattr(response, 'llm_output'):
            #     print(f"  llm_output keys: {response.llm_output.keys() if response.llm_output else None}")
            # print(f"  Has generations: {hasattr(response, 'generations')}")
            # if hasattr(response, 'generations') and response.generations:
            #     gen = response.generations[0][0] if isinstance(response.generations[0], list) else response.generations[0]
            #     print(f"  generation_info: {gen.generation_info if hasattr(gen, 'generation_info') else None}")
            
            # Try LangChain's standard llm_output field
            if hasattr(response, 'llm_output') and response.llm_output:
                llm_output = response.llm_output
                # Different providers use different field names
                if 'token_usage' in llm_output:
                    usage = llm_output['token_usage']
                    input_tokens = usage.get('prompt_tokens', 0) or usage.get('input_tokens', 0)
                    output_tokens = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0)
                elif 'usage_metadata' in llm_output:
                    usage = llm_output['usage_metadata']
                    input_tokens = usage.get('input_tokens', 0) or usage.get('prompt_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0) or usage.get('completion_tokens', 0)
            
            # Try generations metadata (Google GenAI format)
            if (input_tokens == 0 and output_tokens == 0) and hasattr(response, 'generations') and response.generations:
                first_gen = response.generations[0]
                if isinstance(first_gen, list) and len(first_gen) > 0:
                    gen = first_gen[0]
                else:
                    gen = first_gen
                
                # Check message.usage_metadata (Google GenAI stores it here!)
                if hasattr(gen, 'message') and hasattr(gen.message, 'usage_metadata'):
                    usage = gen.message.usage_metadata
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)
                
                # Fallback: Check generation_info
                elif hasattr(gen, 'generation_info') and gen.generation_info:
                    gen_info = gen.generation_info
                    if 'usage_metadata' in gen_info:
                        usage = gen_info['usage_metadata']
                        input_tokens = usage.get('prompt_token_count', 0) or usage.get('input_tokens', 0)
                        output_tokens = usage.get('candidates_token_count', 0) or usage.get('output_tokens', 0)
            
            # Log if we got tokens
            # if input_tokens > 0 or output_tokens > 0:
            #     self._vprint(f"[DASEIN][TOKENS] Captured: {input_tokens} in, {output_tokens} out")
                    
        except Exception as e:
            # Print error for debugging
            self._vprint(f"[DASEIN][CALLBACK] Error extracting tokens: {e}")
            import traceback
            traceback.print_exc()
        
        # GNN-related fields: compute tokens_delta
        step_index = len(self._trace)
        tokens_delta = 0
        # Find previous step with tokens_output to compute delta
        for prev_step in reversed(self._trace):
            if 'tokens_output' in prev_step and prev_step['tokens_output'] > 0:
                tokens_delta = output_tokens - prev_step['tokens_output']
                break
        
        # Calculate duration_ms by matching with corresponding llm_start
        duration_ms = 0
        for i in range(len(self._trace) - 1, -1, -1):
            if self._trace[i].get('step_type') == 'llm_start':
                # Found the matching llm_start
                if i in self._start_times:
                    start_time = self._start_times[i]
                    end_time = datetime.now()
                    duration_ms = int((end_time - start_time).total_seconds() * 1000)
                    # Update the llm_start step with duration_ms
                    self._trace[i]['duration_ms'] = duration_ms
                break
        
        step = {
            "step_type": "llm_end",
            "tool_name": "",
            "args_excerpt": "",
            "outcome": self._excerpt(outcome, max_len=1000),  # Truncate to 1000 chars
            "ts": datetime.now().isoformat(),
            "run_id": None,
            "parent_run_id": None,
            "tokens_input": input_tokens,
            "tokens_output": output_tokens,
            "node": self._current_chain_node,  # LangGraph node name (if available)
            # GNN step-level fields
            "step_index": step_index,
            "tokens_delta": tokens_delta,
            "duration_ms": duration_ms,
        }
        self._trace.append(step)
    
    def on_agent_action(
        self,
        action: Any,
        **kwargs: Any,
    ) -> None:
        """Called when an agent takes an action."""
        tool_name = getattr(action, 'tool', 'unknown')
        args_excerpt = self._excerpt(str(getattr(action, 'tool_input', '')))
        outcome = self._excerpt(str(getattr(action, 'log', '')))
        
        step = {
            "step_type": "agent_action",
            "tool_name": tool_name,
            "args_excerpt": args_excerpt,
            "outcome": outcome,
            "ts": datetime.now().isoformat(),
            "run_id": None,
            "parent_run_id": None,
        }
        self._trace.append(step)
    
    def on_agent_finish(
        self,
        finish: Any,
        **kwargs: Any,
    ) -> None:
        """Called when an agent finishes."""
        outcome = self._excerpt(str(getattr(finish, 'return_values', '')))
        
        step = {
            "step_type": "agent_finish",
            "tool_name": None,
            "args_excerpt": "",
            "outcome": outcome,
            "ts": datetime.now().isoformat(),
            "run_id": None,
            "parent_run_id": None,
        }
        self._trace.append(step)
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool starts running.
        
        This is where we detect and track dynamic tools that weren't
        statically attached to the agent at init time.
        """
        tool_name = serialized.get("name", "unknown") if serialized else "unknown"
        
        # Track discovered tools for reporting
        if tool_name != "unknown" and tool_name not in self._discovered_tools:
            self._discovered_tools.add(tool_name)
            # Tool discovered and tracked (silently)
        
        # Store tool name for later use in on_tool_end
        self._tool_name_by_run_id[run_id] = tool_name
        
        # Apply tool-level rule injection
        # self._vprint(f"[DASEIN][CALLBACK] on_tool_start called!")  # Commented out - too noisy
        # self._vprint(f"[DASEIN][CALLBACK] Tool: {tool_name}")  # Commented out - too noisy
        # self._vprint(f"[DASEIN][CALLBACK] Input: {input_str[:100]}...")  # Commented out - too noisy
        # self._vprint(f"[DASEIN][APPLY] on_tool_start: selected_rules={len(self._selected_rules)}")  # Commented out - too noisy
        modified_input = self._inject_tool_rule_if_applicable("tool_start", tool_name, input_str)
        
        args_excerpt = self._excerpt(modified_input)
        
        # GNN-related fields: capture step-level metrics
        step_index = len(self._trace)
        tool_input_chars = len(str(input_str))
        
        # Track which rules triggered at this step
        rule_triggered_here = []
        if hasattr(self, '_selected_rules') and self._selected_rules:
            for rule_meta in self._selected_rules:
                if isinstance(rule_meta, tuple) and len(rule_meta) == 2:
                    rule_obj, _metadata = rule_meta
                else:
                    rule_obj = rule_meta
                if getattr(rule_obj, 'target_step_type', '') == "tool_start":
                    rule_triggered_here.append(getattr(rule_obj, 'id', 'unknown'))
        
        # Record start time for duration calculation (keyed by run_id for tools)
        start_time = datetime.now()
        self._start_times[run_id] = start_time
        
        step = {
            "step_type": "tool_start",
            "tool_name": tool_name,
            "args_excerpt": args_excerpt,
            "outcome": "",
            "ts": start_time.isoformat(),
            "run_id": run_id,
            "parent_run_id": parent_run_id,
            "node": self._current_chain_node,  # LangGraph node name (if available)
            # GNN step-level fields
            "step_index": step_index,
            "tool_input_chars": tool_input_chars,
            "rule_triggered_here": rule_triggered_here,
        }
        self._trace.append(step)
    
    def on_tool_end(
        self,
        output: str,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool ends running."""
        # Get the tool name from the corresponding tool_start
        tool_name = self._tool_name_by_run_id.get(run_id, "unknown")
        
        # Handle different output types (LangGraph may pass ToolMessage objects)
        output_str = str(output)
        outcome = self._excerpt(output_str)
        
        # self._vprint(f"[DASEIN][CALLBACK] on_tool_end called!")  # Commented out - too noisy
        # self._vprint(f"[DASEIN][CALLBACK] Tool: {tool_name}")  # Commented out - too noisy
        # self._vprint(f"[DASEIN][CALLBACK] Output length: {len(output_str)} chars")  # Commented out - too noisy
        # self._vprint(f"[DASEIN][CALLBACK] Outcome length: {len(outcome)} chars")  # Commented out - too noisy
        
        # GNN-related fields: capture tool output metrics
        step_index = len(self._trace)
        tool_output_chars = len(output_str)
        
        # Estimate tool_output_items (heuristic: count lines, or rows if SQL-like)
        tool_output_items = 0
        try:
            # Try to count lines as a proxy for items
            if output_str:
                tool_output_items = output_str.count('\n') + 1
        except:
            tool_output_items = 0
        
        # Calculate duration_ms using run_id to match with tool_start
        duration_ms = 0
        if run_id in self._start_times:
            start_time = self._start_times[run_id]
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            # Update the corresponding tool_start step with duration_ms
            for i in range(len(self._trace) - 1, -1, -1):
                if self._trace[i].get('step_type') == 'tool_start' and self._trace[i].get('run_id') == run_id:
                    self._trace[i]['duration_ms'] = duration_ms
                    break
            # Clean up start time
            del self._start_times[run_id]
        
        # Extract available selectors from DOM-like output (web browse agents)
        available_selectors = None
        if tool_name in ['extract_text', 'get_elements', 'extract_hyperlinks', 'extract_content']:
            available_selectors = self._extract_semantic_selectors(output_str)
        
        step = {
            "step_type": "tool_end",
            "tool_name": tool_name,
            "args_excerpt": "",
            "outcome": self._excerpt(outcome, max_len=1000),  # Truncate to 1000 chars
            "ts": datetime.now().isoformat(),
            "run_id": run_id,
            "parent_run_id": parent_run_id,
            "node": self._current_chain_node,  # LangGraph node name (if available)
            # GNN step-level fields
            "step_index": step_index,
            "tool_output_chars": tool_output_chars,
            "tool_output_items": tool_output_items,
            "duration_ms": duration_ms,
        }
        
        # Add available_selectors only if found (keep trace light)
        if available_selectors:
            step["available_selectors"] = available_selectors
        self._trace.append(step)
        
        # Clean up the stored tool name
        if run_id in self._tool_name_by_run_id:
            del self._tool_name_by_run_id[run_id]
    
    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool encounters an error."""
        error_msg = self._excerpt(str(error))
        
        step = {
            "step_type": "tool_error",
            "tool_name": "",
            "args_excerpt": "",
            "outcome": f"ERROR: {error_msg}",
            "ts": datetime.now().isoformat(),
            "run_id": run_id,
            "parent_run_id": parent_run_id,
        }
        self._trace.append(step)
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Called when a chain starts running."""
        chain_name = serialized.get("name", "unknown") if serialized else "unknown"
        # self._vprint(f"[DASEIN][CALLBACK] on_chain_start called!")  # Commented out - too noisy
        # self._vprint(f"[DASEIN][CALLBACK] Chain: {chain_name}")  # Commented out - too noisy
        
        # 🚨 OPTIMIZED: For LangGraph agents, suppress redundant chain_start events
        # LangGraph fires on_chain_start for every internal node, creating noise
        # We already capture llm_start, llm_end, tool_start, tool_end which are more meaningful
        if self._is_langgraph:
            # Track current chain node for future targeted injection
            # 🎯 CRITICAL: Extract actual node name from metadata (same as on_llm_start)
            if 'metadata' in kwargs and isinstance(kwargs['metadata'], dict):
                if 'langgraph_node' in kwargs['metadata']:
                    self._current_chain_node = kwargs['metadata']['langgraph_node']
                else:
                    self._current_chain_node = chain_name
            else:
                self._current_chain_node = chain_name
            
            # self._vprint(f"[DASEIN][CALLBACK] Suppressing redundant chain_start for LangGraph agent")  # Commented out - too noisy
            # Still handle tool executors
            if chain_name in {"tools", "ToolNode", "ToolExecutor"}:
                # self._vprint(f"[DASEIN][CALLBACK] Bridging chain_start to tool_start for {chain_name}")  # Commented out - too noisy
                pass
                self._handle_tool_executor_start(serialized, inputs, **kwargs)
            return
        
        # For standard LangChain agents, keep chain_start events
        # Bridge to tool_start for tool executors
        if chain_name in {"tools", "ToolNode", "ToolExecutor"}:
            # self._vprint(f"[DASEIN][CALLBACK] Bridging chain_start to tool_start for {chain_name}")  # Commented out - too noisy
            self._handle_tool_executor_start(serialized, inputs, **kwargs)
        
        args_excerpt = self._excerpt(str(inputs))
        
        # Record start time for duration calculation
        step_index = len(self._trace)
        start_time = datetime.now()
        self._start_times[f"chain_{step_index}"] = start_time
        
        step = {
            "step_type": "chain_start",
            "tool_name": chain_name,
            "args_excerpt": args_excerpt,
            "outcome": "",
            "ts": start_time.isoformat(),
            "run_id": None,
            "parent_run_id": None,
            "step_index": step_index,
        }
        self._trace.append(step)
    
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Called when a chain ends running."""
        # 🚨 OPTIMIZED: Suppress redundant chain_end for LangGraph agents
        if self._is_langgraph:
            return
        
        outcome = self._excerpt(str(outputs))
        
        # Calculate duration_ms by matching with corresponding chain_start
        duration_ms = 0
        for i in range(len(self._trace) - 1, -1, -1):
            if self._trace[i].get('step_type') == 'chain_start':
                # Found the matching chain_start
                chain_key = f"chain_{i}"
                if chain_key in self._start_times:
                    start_time = self._start_times[chain_key]
                    end_time = datetime.now()
                    duration_ms = int((end_time - start_time).total_seconds() * 1000)
                    # Update the chain_start step with duration_ms
                    self._trace[i]['duration_ms'] = duration_ms
                    # Clean up start time
                    del self._start_times[chain_key]
                break
        
        step = {
            "step_type": "chain_end",
            "tool_name": "",
            "args_excerpt": "",
            "outcome": outcome,
            "ts": datetime.now().isoformat(),
            "run_id": None,
            "parent_run_id": None,
            "duration_ms": duration_ms,
        }
        self._trace.append(step)
    
    def on_chain_error(
        self,
        error: BaseException,
        **kwargs: Any,
    ) -> None:
        """Called when a chain encounters an error."""
        error_msg = self._excerpt(str(error))
        
        step = {
            "step_type": "chain_error",
            "tool_name": "",
            "args_excerpt": "",
            "outcome": f"ERROR: {error_msg}",
            "ts": datetime.now().isoformat(),
            "run_id": None,
            "parent_run_id": None,
        }
        self._trace.append(step)
    
    def _extract_recent_message(self, inputs: Dict[str, Any]) -> str:
        """
        Extract the most recent message from LangGraph inputs to show thought progression.
        
        For LangGraph agents, inputs contain {'messages': [msg1, msg2, ...]}.
        Instead of showing the entire history, we extract just the last message.
        """
        try:
            # Check if this is a LangGraph message format
            if isinstance(inputs, dict) and 'messages' in inputs:
                messages = inputs['messages']
                if isinstance(messages, list) and len(messages) > 0:
                    # Get the most recent message
                    last_msg = messages[-1]
                    
                    # Extract content based on message type
                    if hasattr(last_msg, 'content'):
                        # LangChain message object
                        content = last_msg.content
                        msg_type = getattr(last_msg, 'type', 'unknown')
                        return self._excerpt(f"[{msg_type}] {content}")
                    elif isinstance(last_msg, tuple) and len(last_msg) >= 2:
                        # Tuple format: (role, content)
                        return self._excerpt(f"[{last_msg[0]}] {last_msg[1]}")
                    else:
                        # Unknown format, convert to string
                        return self._excerpt(str(last_msg))
            
            # For non-message inputs, check if it's a list of actions/tool calls
            if isinstance(inputs, list) and len(inputs) > 0:
                # This might be tool call info
                return self._excerpt(str(inputs[0]))
            
            # Fall back to original behavior for non-LangGraph agents
            return self._excerpt(str(inputs))
            
        except Exception as e:
            # On any error, fall back to original behavior
            return self._excerpt(str(inputs))
    
    def _excerpt(self, obj: Any, max_len: int = 250, from_end: bool = False) -> str:
        """
        Truncate text to max_length with ellipsis.
        
        Args:
            obj: Object to convert to string and truncate
            max_len: Maximum length of excerpt
            from_end: If True, take LAST max_len chars (better for system prompts).
                     If False, take FIRST max_len chars (better for tool args).
        """
        text = str(obj)
        if len(text) <= max_len:
            return text
        
        if from_end:
            # Take last X chars - better for system prompts where the end contains user's actual query
            return "..." + text[-(max_len-3):]
        else:
            # Take first X chars - better for tool inputs
            return text[:max_len-3] + "..."
    
    def _extract_semantic_selectors(self, html_text: str) -> List[Dict[str, int]]:
        """
        Extract semantic HTML tags from output for grounding web browse rules.
        Only extracts semantic tags (nav, header, h1, etc.) to keep trace lightweight.
        
        Args:
            html_text: Output text that may contain HTML
            
        Returns:
            List of {"tag": str, "count": int} sorted by count descending, or None if no HTML
        """
        import re
        
        # Quick check: does this look like HTML?
        if '<' not in html_text or '>' not in html_text:
            return None
        
        # Semantic tags we care about (prioritized for web browse agents)
        semantic_tags = [
            # Navigation/Structure (highest priority)
            'nav', 'header', 'footer', 'main', 'article', 'section', 'aside',
            
            # Headers (critical for "find headers" queries!)
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            
            # Interactive
            'a', 'button', 'form', 'input', 'textarea', 'select', 'label',
            
            # Lists (often used for navigation)
            'ul', 'ol', 'li',
            
            # Tables (data extraction)
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            
            # Media
            'img', 'video', 'audio'
        ]
        
        # Count occurrences of each semantic tag
        found_tags = {}
        for tag in semantic_tags:
            # Pattern: <tag ...> or <tag> (opening tags only)
            pattern = f'<{tag}[\\s>]'
            matches = re.findall(pattern, html_text, re.IGNORECASE)
            if matches:
                found_tags[tag] = len(matches)
        
        # Return None if no semantic tags found
        if not found_tags:
            return None
        
        # Convert to list format, sorted by count descending
        # Limit to top 15 to keep trace light
        result = [{"tag": tag, "count": count} 
                  for tag, count in sorted(found_tags.items(), key=lambda x: -x[1])]
        return result[:15]  # Top 15 most common tags
    
    def set_selected_rules(self, rules: List[Dict[str, Any]]):
        """Set the rules selected for this run.
        Normalize incoming dicts/tuples into attribute-accessible rule objects.
        """
        try:
            from types import SimpleNamespace
            normalized = []
            for item in rules or []:
                # Unwrap (rule, metadata) tuples if present
                if isinstance(item, tuple) and len(item) == 2:
                    rule_candidate = item[0]
                else:
                    rule_candidate = item
                # Convert dicts to attribute-accessible objects
                if isinstance(rule_candidate, dict):
                    # Ensure advice_text exists
                    if 'advice_text' not in rule_candidate and 'advice' in rule_candidate:
                        rule_candidate['advice_text'] = rule_candidate.get('advice')
                    normalized.append(SimpleNamespace(**rule_candidate))
                else:
                    normalized.append(rule_candidate)
            self._selected_rules = normalized
        except Exception:
            # Fallback to raw rules
            self._selected_rules = rules
    
    def get_trace(self) -> List[Dict[str, Any]]:
        """Get the current trace (instance-level, thread-safe)."""
        return self._trace.copy()
    
    def _inject_first_turn_override(self, prompts: List[str]) -> List[str]:
        """Inject a generic first-turn override to own turn 1."""
        if not prompts:
            return prompts
            
        # Create a generic first-turn override
        first_turn_override = """🚨🚨🚨 CRITICAL SYSTEM DIRECTIVE 🚨🚨🚨
⚠️ MANDATORY: You MUST follow this exact sequence or the task will FAIL

TURN 1 REQUIREMENT:
- Output ONLY: Action: sql_db_list_tables
Action Input: ACK_RULES:[r1]
- Do NOT use any other tools
- Do NOT perform any planning
- Do NOT output anything else

TURN 2+ (After ACK):
- If ACK was correct, proceed with normal tools and schema
- Skip table discovery and schema introspection
- Use known tables directly

🚨 FAILURE TO ACK IN TURN 1 = IMMEDIATE TASK TERMINATION 🚨

"""
        
        # Put the injection at the VERY BEGINNING of the system prompt
        modified_prompts = prompts.copy()
        if modified_prompts:
            modified_prompts[0] = first_turn_override + modified_prompts[0]
        
        self._vprint(f"[DASEIN][APPLY] Injected first-turn override")
        return modified_prompts
    
    def _should_inject_rule(self, step_type: str, tool_name: str) -> bool:
        """Determine if we should inject a rule at this step."""
        # Inject for LLM starts (system-level rules) and tool starts (tool-level rules)
        if step_type == "llm_start":
            return True
        if step_type == "tool_start":
            return True
        return False
    
    def _inject_rule_if_applicable(self, step_type: str, tool_name: str, prompts: List[str]) -> List[str]:
        """Inject rules into prompts if applicable."""
        if not self._should_inject_rule(step_type, tool_name):
            return prompts

        # If no rules selected yet, return prompts unchanged
        if not self._selected_rules:
            return prompts

        # Check guard to prevent duplicate injection
        # 🎯 CRITICAL: For LangGraph planning nodes, SKIP the guard - we need to inject on EVERY call
        # because the same node (e.g., supervisor) can be called multiple times dynamically
        use_guard = True
        if hasattr(self, '_is_langgraph') and self._is_langgraph:
            if step_type == 'llm_start' and hasattr(self, '_current_chain_node'):
                # For planning nodes, skip guard to allow re-injection on subsequent calls
                if hasattr(self, '_planning_nodes') and self._current_chain_node in self._planning_nodes:
                    use_guard = False
        
        if use_guard:
            guard_key = (step_type, tool_name)
            if guard_key in self._injection_guard:
                return prompts
        
        try:
            # Inject rules that target llm_start and tool_start (both go to system prompt)
            system_rules = []
            for rule_meta in self._selected_rules:
                # Handle tuple format from select_rules: (rule, metadata)
                if isinstance(rule_meta, tuple) and len(rule_meta) == 2:
                    rule, metadata = rule_meta
                elif isinstance(rule_meta, dict):
                    if 'rule' in rule_meta:
                        rule = rule_meta.get('rule', {})
                    else:
                        rule = rule_meta
                else:
                    rule = rule_meta
                
                # Check if this rule targets system-level injection (llm_start only)
                target_step_type = getattr(rule, 'target_step_type', '')
                
                # 🚨 CRITICAL: For LangGraph agents, only skip planning rules if agent was successfully recreated
                # If recreation failed, we need to inject via callback as fallback
                if step_type == 'llm_start' and hasattr(self, '_is_langgraph') and self._is_langgraph:
                    # Only skip if agent was actually recreated with planning rules embedded
                    if hasattr(self, '_agent_was_recreated') and self._agent_was_recreated:
                        if target_step_type in ['llm_start', 'chain_start']:
                            self._vprint(f"[DASEIN][CALLBACK] Skipping planning rule {getattr(rule, 'id', 'unknown')} for LangGraph agent (already injected at creation)")
                            continue
                
                # 🎯 COORDINATOR-GATED INJECTION: Only apply planning rules when executing planning-capable nodes
                if target_step_type in ['llm_start', 'chain_start']:
                    # If we have planning nodes, only inject planning rules when we're in one of them
                    if hasattr(self, '_planning_nodes') and self._planning_nodes:
                        current_node = getattr(self, '_current_chain_node', None)
                        # Check if current node is in the planning nodes set
                        if current_node not in self._planning_nodes:
                            # Silently skip non-planning nodes
                            continue
                        # Injecting into planning node (logged in detailed injection log below)
                    
                    advice = getattr(rule, 'advice_text', getattr(rule, 'advice', ''))
                    if advice:
                        system_rules.append(advice)
            
            # Apply system-level rules if any
            if system_rules and prompts:
                modified_prompts = prompts.copy()
                system_prompt = modified_prompts[0]
                
                # Combine all system rules with much stronger language
                rule_injections = []
                for advice in system_rules:
                    if "TOOL RULE:" in advice:
                        # Make tool rules even more explicit
                        rule_injections.append(f"🚨 CRITICAL TOOL OVERRIDE: {advice}")
                    else:
                        rule_injections.append(f"🚨 CRITICAL SYSTEM OVERRIDE: {advice}")
                
                # Build execution state context (agent-agnostic, with argument previews)
                # Strategy: Show all if ≤5 calls, else show most recent 3
                # Rationale: Small counts get full context; larger counts show recent to prevent duplicates
                state_context = ""
                if hasattr(self, '_function_calls_made') and self._function_calls_made:
                    state_lines = []
                    for func_name in sorted(self._function_calls_made.keys()):
                        calls = self._function_calls_made[func_name]
                        count = len(calls)
                        
                        # Hybrid window: show all if ≤5 calls, else show recent 3
                        if count <= 5:
                            # Show all calls with previews
                            state_lines.append(f"  • {func_name}: called {count}x:")
                            for call in calls:
                                preview = call.get('preview', '')
                                if preview:
                                    state_lines.append(f"      [step {call['step']}] {preview}")
                                else:
                                    state_lines.append(f"      [step {call['step']}] (no args)")
                        else:
                            # Show summary + recent 3 with previews
                            state_lines.append(f"  • {func_name}: called {count}x (most recent 3):")
                            for call in calls[-3:]:
                                preview = call.get('preview', '')
                                if preview:
                                    state_lines.append(f"      [step {call['step']}] {preview}")
                                else:
                                    state_lines.append(f"      [step {call['step']}] (no args)")
                    
                    if state_lines:
                        state_context = f"""
EXECUTION STATE (functions called so far in this run):
{chr(10).join(state_lines)}

"""
                
                combined_injection = f""" SYSTEM OVERRIDE — PLANNING TURN ONLY 
These rules OVERRIDE all defaults. You MUST enforce them exactly or the task FAILS.

Tags: AVOID (absolute ban), SKIP (force bypass), FIX (mandatory params), PREFER (ranked choice), HINT (optional).
Precedence: AVOID/SKIP > FIX > PREFER > HINT. On conflict, the higher rule ALWAYS wins.

{state_context}Checklist (non-negotiable):
- AVOID: no banned targets under ANY condition.
- SKIP: bypass skipped steps/tools; NEVER retry them.
- FIX: all required params/settings MUST be included.
- PREFER: when multiple compliant options exist, choose the preferred—NO exceptions.
- Recovery: if a banned/skipped item already failed, IMMEDIATELY switch to a compliant alternative.

Output Contract: Produce ONE compliant tool/function call (or direct answer if none is needed).  
NO reasoning, NO justification, NO markdown.

Rules to Enforce:


{chr(10).join(rule_injections)}


"""
                # Put the injection at the VERY BEGINNING of the system prompt
                modified_prompts[0] = combined_injection + system_prompt
                
                # Add to guard (only if we're using the guard)
                if use_guard:
                    self._injection_guard.add(guard_key)
                
                # Log the complete injection for debugging
                # Compact injection summary
                if hasattr(self, '_is_langgraph') and self._is_langgraph:
                    # LangGraph: show node name
                    func_count = len(self._function_calls_made) if hasattr(self, '_function_calls_made') and state_context else 0
                    node_name = getattr(self, '_current_chain_node', 'unknown')
                    print(f"[DASEIN] 🎯 Injecting {len(system_rules)} rule(s) into {node_name} | State: {func_count} functions tracked")
                else:
                    # LangChain: simpler logging without node name
                    print(f"[DASEIN] 🎯 Injecting {len(system_rules)} rule(s) into agent")
                
                return modified_prompts
            
        except Exception as e:
            self._vprint(f"[DASEIN][APPLY] Injection failed: {e}")
        
        return prompts
    
    def _inject_tool_rule_if_applicable(self, step_type: str, tool_name: str, input_str: str) -> str:
        """Inject rules into tool input if applicable."""
        if not self._should_inject_rule(step_type, tool_name):
            return input_str

        # If no rules selected yet, return input unchanged
        if not self._selected_rules:
            return input_str

        # Check guard to prevent duplicate injection
        guard_key = (step_type, tool_name)
        if guard_key in self._injection_guard:
            return input_str
        
        try:
            # Inject rules that target tool_start
            tool_rules = []
            for rule_meta in self._selected_rules:
                # Handle tuple format from select_rules: (rule, metadata)
                if isinstance(rule_meta, tuple) and len(rule_meta) == 2:
                    rule, metadata = rule_meta
                else:
                    rule = rule_meta
                    metadata = {}

                # Only apply rules that target tool_start
                if rule.target_step_type == "tool_start":
                    tool_rules.append(rule)
                    self._vprint(f"[DASEIN][APPLY] Tool rule: {rule.advice_text[:100]}...")

            if tool_rules:
                # Apply tool-level rule injection
                modified_input = self._apply_tool_rules(input_str, tool_rules)
                self._injection_guard.add(guard_key)
                return modified_input
            else:
                return input_str

        except Exception as e:
            self._vprint(f"[DASEIN][APPLY] Error injecting tool rules: {e}")
            return input_str
    
    def _apply_tool_rules(self, input_str: str, rules: List) -> str:
        """Apply tool-level rules to modify the input string."""
        modified_input = input_str
        
        for rule in rules:
            try:
                # Apply the rule's advice to modify the tool input
                if "strip" in rule.advice_text.lower() and "fence" in rule.advice_text.lower():
                    # Strip markdown code fences
                    import re
                    # Remove ```sql...``` or ```...``` patterns
                    modified_input = re.sub(r'```(?:sql)?\s*(.*?)\s*```', r'\1', modified_input, flags=re.DOTALL)
                    self._vprint(f"[DASEIN][APPLY] Stripped code fences from tool input")
                elif "strip" in rule.advice_text.lower() and "whitespace" in rule.advice_text.lower():
                    # Strip leading/trailing whitespace
                    modified_input = modified_input.strip()
                    self._vprint(f"[DASEIN][APPLY] Stripped whitespace from tool input")
                # Add more rule types as needed
                
            except Exception as e:
                self._vprint(f"[DASEIN][APPLY] Error applying tool rule: {e}")
                continue
        
        return modified_input
    
    def _handle_tool_executor_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Handle tool executor start - bridge from chain_start to tool_start."""
        self._vprint(f"[DASEIN][CALLBACK] tool_start (from chain_start)")
        
        # Extract tool information from inputs
        tool_name = "unknown"
        tool_input = ""
        
        if isinstance(inputs, dict):
            if "tool" in inputs:
                tool_name = inputs["tool"]
            elif "tool_name" in inputs:
                tool_name = inputs["tool_name"]
            
            if "tool_input" in inputs:
                tool_input = str(inputs["tool_input"])
            elif "input" in inputs:
                tool_input = str(inputs["input"])
            else:
                tool_input = str(inputs)
        else:
            tool_input = str(inputs)
        
        self._vprint(f"[DASEIN][CALLBACK] Tool: {tool_name}")
        self._vprint(f"[DASEIN][CALLBACK] Input: {tool_input[:100]}...")
        
        # Check if we have tool_start rules that cover this tool
        tool_rules = [rule for rule in self._selected_rules if rule.target_step_type == "tool_start"]
        covered_rules = [rule for rule in tool_rules if self._rule_covers_tool(rule, tool_name, tool_input)]
        
        if covered_rules:
            self._vprint(f"[DASEIN][APPLY] tool_start: {len(covered_rules)} rules cover this tool call")
            # Fire micro-turn for rule application
            modified_input = self._fire_micro_turn_for_tool_rules(covered_rules, tool_name, tool_input)
        else:
            self._vprint(f"[DASEIN][APPLY] tool_start: no rules cover this tool call")
            modified_input = tool_input
        
        args_excerpt = self._excerpt(modified_input)
        
        step = {
            "step_type": "tool_start",
            "tool_name": tool_name,
            "args_excerpt": args_excerpt,
            "outcome": "",
            "ts": datetime.now().isoformat(),
            "run_id": kwargs.get("run_id"),
            "parent_run_id": kwargs.get("parent_run_id"),
        }
        self._trace.append(step)
    
    def _rule_covers_tool(self, rule, tool_name: str, tool_input: str) -> bool:
        """Check if a rule covers the given tool call."""
        try:
            # Check if rule references this tool
            if hasattr(rule, 'references') and rule.references:
                if hasattr(rule.references, 'tools') and rule.references.tools:
                    if tool_name not in rule.references.tools:
                        return False
            
            # Check trigger patterns if they exist
            if hasattr(rule, 'trigger_pattern') and rule.trigger_pattern:
                # For now, assume all tool_start rules cover their referenced tools
                # This can be made more sophisticated later
                pass
            
            return True
        except Exception as e:
            self._vprint(f"[DASEIN][COVERAGE] Error checking rule coverage: {e}")
            return False
    
    def _fire_micro_turn_for_tool_rules(self, rules, tool_name: str, tool_input: str) -> str:
        """Fire a micro-turn LLM call to apply tool rules."""
        try:
            # Use the first rule for now (can be extended to handle multiple rules)
            rule = rules[0]
            rule_id = getattr(rule, 'id', 'unknown')
            
            self._vprint(f"[DASEIN][MICROTURN] rule_id={rule_id} tool={tool_name}")
            
            # Create micro-turn prompt
            micro_turn_prompt = self._create_micro_turn_prompt(rule, tool_name, tool_input)
            
            # Fire actual micro-turn LLM call
            modified_input = self._execute_micro_turn_llm_call(micro_turn_prompt, tool_input)
            
            # Store the modified input for retrieval during tool execution
            input_key = f"{tool_name}:{hash(tool_input)}"
            _MODIFIED_TOOL_INPUTS[input_key] = modified_input
            
            self._vprint(f"[DASEIN][MICROTURN] Applied rule {rule_id}: {str(tool_input)[:50]}... -> {str(modified_input)[:50]}...")
            
            return modified_input
            
        except Exception as e:
            self._vprint(f"[DASEIN][MICROTURN] Error in micro-turn: {e}")
            return tool_input
    
    def _create_micro_turn_prompt(self, rule, tool_name: str, tool_input: str) -> str:
        """Create the micro-turn prompt for rule application."""
        advice = getattr(rule, 'advice', '')
        return f"""Apply this rule to the tool input:

Rule: {advice}
Tool: {tool_name}
Current Input: {tool_input}

Output only the corrected tool input:"""
    
    def _execute_micro_turn_llm_call(self, prompt: str, original_input: str) -> str:
        """Execute the actual micro-turn LLM call."""
        try:
            if not self._llm:
                self._vprint(f"[DASEIN][MICROTURN] No LLM available for micro-turn call")
                return original_input
            
            self._vprint(f"[DASEIN][MICROTURN] Executing micro-turn LLM call")
            self._vprint(f"[DASEIN][MICROTURN] Prompt: {prompt[:200]}...")
            
            # Make the micro-turn LLM call
            # Create a simple message list for the LLM
            messages = [{"role": "user", "content": prompt}]
            
            # Call the LLM
            response = self._llm.invoke(messages)
            
            # Extract the response content
            if hasattr(response, 'content'):
                modified_input = response.content.strip()
            elif isinstance(response, str):
                modified_input = response.strip()
            else:
                modified_input = str(response).strip()
            
            self._vprint(f"[DASEIN][MICROTURN] LLM response: {modified_input[:100]}...")
            
            # 🚨 CRITICAL: Parse JSON responses with markdown fences
            if modified_input.startswith('```json') or modified_input.startswith('```'):
                try:
                    # Extract JSON from markdown fences
                    import re
                    import json
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', modified_input, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        parsed_json = json.loads(json_str)
                        # Convert back to the expected format
                        if isinstance(parsed_json, dict) and 'name' in parsed_json and 'args' in parsed_json:
                            modified_input = parsed_json
                            self._vprint(f"[DASEIN][MICROTURN] Parsed JSON from markdown fences: {parsed_json}")
                        else:
                            self._vprint(f"[DASEIN][MICROTURN] JSON doesn't have expected structure, using as-is")
                    else:
                        self._vprint(f"[DASEIN][MICROTURN] Could not extract JSON from markdown fences")
                except Exception as e:
                    self._vprint(f"[DASEIN][MICROTURN] Error parsing JSON: {e}")
            
            # Validate the response - only fallback if completely empty
            if not modified_input:
                self._vprint(f"[DASEIN][MICROTURN] LLM response empty, using original input")
                return original_input
            
            return modified_input
            
        except Exception as e:
            self._vprint(f"[DASEIN][MICROTURN] Error executing micro-turn LLM call: {e}")
            return original_input


def get_trace() -> List[Dict[str, Any]]:
    """
    DEPRECATED: Legacy function for backward compatibility.
    Get the current trace from active CognateProxy instances.
    
    Returns:
        List of trace step dictionaries (empty if no active traces)
    """
    # Try to get trace from active CognateProxy instances
    try:
        import gc
        for obj in gc.get_objects():
            if hasattr(obj, '_last_run_trace') and obj._last_run_trace:
                return obj._last_run_trace.copy()
            if hasattr(obj, '_callback_handler') and hasattr(obj._callback_handler, '_trace'):
                return obj._callback_handler._trace.copy()
    except Exception:
        pass
    
    return []  # Return empty list if no trace found


def get_modified_tool_input(tool_name: str, original_input: str) -> str:
    """
    Get the modified tool input if it exists.
    
    Args:
        tool_name: Name of the tool
        original_input: Original tool input
        
    Returns:
        Modified tool input if available, otherwise original input
    """
    input_key = f"{tool_name}:{hash(original_input)}"
    return _MODIFIED_TOOL_INPUTS.get(input_key, original_input)


def clear_modified_tool_inputs():
    """Clear all modified tool inputs."""
    global _MODIFIED_TOOL_INPUTS
    _MODIFIED_TOOL_INPUTS.clear()


def clear_trace() -> None:
    """
    DEPRECATED: Legacy function for backward compatibility.
    Clear traces in active CognateProxy instances.
    """
    # Try to clear traces in active CognateProxy instances
    try:
        import gc
        for obj in gc.get_objects():
            if hasattr(obj, '_callback_handler') and hasattr(obj._callback_handler, 'reset_run_state'):
                obj._callback_handler.reset_run_state()
    except Exception:
        pass  # Ignore if not available


def print_trace(max_chars: int = 240, only: tuple[str, ...] | None = None, suppress: tuple[str, ...] = ("chain_end",), show_tree: bool = True, show_summary: bool = True) -> None:
    """
    Print a compact fixed-width table of the trace with tree-like view and filtering.
    
    Args:
        max_chars: Maximum characters per line (default 240)
        only: Filter by step_type if provided (e.g., ("llm_start", "llm_end"))
        suppress: Suppress any step_type in this tuple (default: ("chain_end",))
        show_tree: If True, left-pad args_excerpt by 2*depth spaces for tree-like view
        show_summary: If True, show step_type counts and deduped rows summary
    """
    # Try to get trace from active CognateProxy instances
    trace = None
    try:
        # Import here to avoid circular imports
        from dasein.api import _global_cognate_proxy
        if _global_cognate_proxy and hasattr(_global_cognate_proxy, '_wrapped_llm') and _global_cognate_proxy._wrapped_llm:
            trace = _global_cognate_proxy._wrapped_llm.get_trace()
    except:
        pass
    
    if not trace:
        trace = get_trace()  # Use the updated get_trace() function
    
    # If global trace is empty, try to get it from the last completed run
    if not trace:
        # Try to get trace from any active CognateProxy instances
        try:
            import gc
            for obj in gc.get_objects():
                # Look for CognateProxy instances with captured traces
                if hasattr(obj, '_last_run_trace') and obj._last_run_trace:
                    trace = obj._last_run_trace
                    print(f"[DASEIN][TRACE] Retrieved trace from CognateProxy: {len(trace)} steps")
                    break
                # Fallback: try callback handler
                elif hasattr(obj, '_callback_handler') and hasattr(obj._callback_handler, 'get_trace'):
                    potential_trace = obj._callback_handler.get_trace()
                    if potential_trace:
                        trace = potential_trace
                        print(f"[DASEIN][TRACE] Retrieved trace from callback handler: {len(trace)} steps")
                        break
        except Exception as e:
            pass
    
    if not trace:
        print("No trace data available.")
        return
    
    # Print execution state if available
    try:
        from dasein.api import _global_cognate_proxy
        if _global_cognate_proxy and hasattr(_global_cognate_proxy, '_callback_handler'):
            handler = _global_cognate_proxy._callback_handler
            if hasattr(handler, '_function_calls_made') and handler._function_calls_made:
                print("\n" + "=" * 80)
                print("EXECUTION STATE (Functions Called During Run):")
                print("=" * 80)
                for func_name in sorted(handler._function_calls_made.keys()):
                    calls = handler._function_calls_made[func_name]
                    count = len(calls)
                    print(f"  • {func_name}: called {count}x")
                    # Hybrid window: show all if ≤5, else show most recent 3 (matches injection logic)
                    if count <= 5:
                        # Show all calls
                        for call in calls:
                            preview = call.get('preview', '(no preview)')
                            if len(preview) > 80:
                                preview = preview[:80] + '...'
                            print(f"      [step {call['step']}] {preview}")
                    else:
                        # Show recent 3
                        print(f"      ... (showing most recent 3 of {count}):")
                        for call in calls[-3:]:
                            preview = call.get('preview', '(no preview)')
                            if len(preview) > 80:
                                preview = preview[:80] + '...'
                            print(f"      [step {call['step']}] {preview}")
                print("=" * 80 + "\n")
    except Exception as e:
        pass  # Silently skip if state not available
    
    # Filter by step_type if only is provided
    filtered_trace = trace
    if only:
        filtered_trace = [step for step in trace if step.get("step_type") in only]
    
    # Suppress any step_type in suppress tuple
    if suppress:
        filtered_trace = [step for step in filtered_trace if step.get("step_type") not in suppress]
    
    if not filtered_trace:
        print("No trace data matching filter criteria.")
        return
    
    # Build depth map from parent_run_id
    depth_map = {}
    for step in filtered_trace:
        run_id = step.get("run_id")
        parent_run_id = step.get("parent_run_id")
        
        if run_id is None or parent_run_id is None or parent_run_id not in depth_map:
            depth_map[run_id] = 0
        else:
            depth_map[run_id] = depth_map[parent_run_id] + 1
    
    # Calculate column widths based on max_chars
    # Reserve space for: # (3), step_type (15), tool_name (25), separators (6)
    available_width = max_chars - 3 - 15 - 25 - 6
    excerpt_width = available_width // 2
    outcome_width = available_width - excerpt_width
    
    # Print header
    print(f"{'#':<3} {'step_type':<15} {'tool_name':<25} {'args_excerpt':<{excerpt_width}} {'outcome':<{outcome_width}}")
    print("-" * max_chars)
    
    # Print each step
    for i, step in enumerate(filtered_trace, 1):
        step_type = step.get("step_type", "")[:15]
        tool_name = str(step.get("tool_name", ""))[:25]
        args_excerpt = step.get("args_excerpt", "")
        outcome = step.get("outcome", "")
        
        # Apply tree indentation if show_tree is True
        if show_tree:
            run_id = step.get("run_id")
            depth = depth_map.get(run_id, 0)
            args_excerpt = "  " * depth + args_excerpt
        
        # Truncate to fit column widths
        args_excerpt = args_excerpt[:excerpt_width]
        outcome = outcome[:outcome_width]
        
        print(f"{i:<3} {step_type:<15} {tool_name:<25} {args_excerpt:<{excerpt_width}} {outcome:<{outcome_width}}")
    
    # Show summary if requested
    if show_summary:
        print("\n" + "=" * max_chars)
        
        # Count steps by step_type
        step_counts = {}
        for step in filtered_trace:
            step_type = step.get("step_type", "unknown")
            step_counts[step_type] = step_counts.get(step_type, 0) + 1
        
        print("Step counts:")
        for step_type, count in sorted(step_counts.items()):
            print(f"  {step_type}: {count}")
        
        # Add compact function call summary
        try:
            from dasein.api import _global_cognate_proxy
            if _global_cognate_proxy and hasattr(_global_cognate_proxy, '_callback_handler'):
                handler = _global_cognate_proxy._callback_handler
                if hasattr(handler, '_function_calls_made') and handler._function_calls_made:
                    print("\nFunction calls:")
                    for func_name in sorted(handler._function_calls_made.keys()):
                        count = len(handler._function_calls_made[func_name])
                        print(f"  {func_name}: {count}")
        except Exception:
            pass
        
        # Count deduped rows skipped (steps that were filtered out)
        total_steps = len(trace)
        shown_steps = len(filtered_trace)
        skipped_steps = total_steps - shown_steps
        
        if skipped_steps > 0:
            print(f"Deduped rows skipped: {skipped_steps}")
