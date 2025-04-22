# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import aiohttp
from collections import deque
import importlib.util
import time
from typing import Any, List, Dict

def import_function(spec: str) -> callable:
    """
    Dynamically import a function from a file, given a single string with the pattern:
    path/to/file[:function_name].
    """
    if ":" not in spec:
        raise ImportError("A path like examples/interleaved_tool_calling/functions.py:search_ddg must be specified.")
    
    module_path, function_name = spec.rsplit(":", 1)

    spec_obj = importlib.util.spec_from_file_location("tool_function", module_path)
    if not spec_obj:
        raise ImportError(f"Could not create a spec for {module_path}")

    mod = importlib.util.module_from_spec(spec_obj)

    loader = spec_obj.loader
    if not loader:
        raise ImportError(f"No loader found for {module_path}")
    loader.exec_module(mod)

    if not hasattr(mod, function_name):
        raise AttributeError(f"The module '{module_path}' has no attribute '{function_name}'")

    return getattr(mod, function_name)

class RateLimiter:
    """A simple rolling-window rate limiter for async calls."""
    def __init__(self, calls_per_second: int):
        self.calls_per_second = calls_per_second
        self.call_timestamps = deque()
        self.lock = asyncio.Lock()

    async def wait(self):
        """
        Ensure we do not exceed 'calls_per_second' in a trailing 1-second window.
        If at capacity, wait until there's room.
        """
        async with self.lock:
            now = time.monotonic()
            
            # Remove old calls that are more than 1 second old
            while self.call_timestamps and self.call_timestamps[0] <= now - 1:
                self.call_timestamps.popleft()

            # If at the limit, wait
            if len(self.call_timestamps) >= self.calls_per_second:
                sleep_time = 1 - (now - self.call_timestamps[0])
                await asyncio.sleep(sleep_time)

                # Remove old timestamps again after waiting
                now = time.monotonic()
                while self.call_timestamps and self.call_timestamps[0] <= now - 1:
                    self.call_timestamps.popleft()

            # Add new call timestamp
            self.call_timestamps.append(now)

def batch_process_queries(
    tool_function_path: str,
    search_queries: List[Dict[str, Any]],
    tool_kwargs: Dict[str, Any],
    max_calls_per_second: int = 10
) -> List[Any]:
    """
    Process queries concurrently with a rolling-window rate limit,
    using aiohttp for real async I/O to reduce overhead.
    
    Args:
        tool_function_path: The path to an async function to call for each query
        search_queries: List of query dictionaries
        tool_kwargs: Additional keyword arguments for the tool function
        max_calls_per_second: Maximum number of tool function calls per second
        
    Returns:
        List of results in the same order as the input queries
    """

    tool_function = import_function(tool_function_path)
    
    async def execute_query(rate_limiter, session, query):
        # Request permission from rate limiter
        await rate_limiter.wait()
        return await tool_function(query["query"], session, **tool_kwargs)
    
    async def process_all_queries():
        rate_limiter = RateLimiter(max_calls_per_second)
        
        # Reuse a single aiohttp session for all requests
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(execute_query(rate_limiter, session, q))
                for q in search_queries
            ]
            return await asyncio.gather(*tasks)

    return asyncio.run(process_all_queries())
