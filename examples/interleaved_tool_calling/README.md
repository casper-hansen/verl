# Interleaved Tool Calling

This example showcases tool calling during generation of a token sequence with vLLM. Specifically, we showcase (1) in this example but note that this is extensible to other use-cases.

1. A simple and common use-case is search/retrieval. Given a search tool, the model can learn to query and retrieve additional information into the context. Advanced use-cases includes a DeepResearch model.
2. Code execution and feedback. You can implement an environment with execution and feedback. This extends to the possibility of generating multiple parallel solutions with a rollout.
3. Evaluate mathematical expressions and return feedback. Advanced use-cases could be calling Wolframalpha API or using Lean 4 for theorem proving.

## Example behavior

In this example, the goal is to teach the model to query a search engine. We use DuckDuckGo as it requires no API keys and zero setup. Below, you can find an example of the desired behavior we want to elicit in the model.

```
<|im_start|>system
You are a helpful assistant that is capable of tool calling.
You always seek additional information by creating search queries between <search>[INSERT QUERY]</search> tags.<|im_end|>
<|im_start|>user
Explain what veRL is<|im_end|>
<|im_start|>assistant
To answer this question, I should seek more information. <search>veRL</search><info>verl is a flexible, efficient and production-ready RL training library for large language models (LLMs). verl is the open-source version of HybridFlow: A Flexible and Efficient RLHF Framework paper. verl is flexible and easy to use with: Easy extension of diverse RL algorithms: The hybrid-controller ...</info>
Based on the search results, veRL seems to be a post-training library for large language models (LLMs).
<|im_end|>
```

## Getting started

First, you need to `pip install duckduckgo_search` for this example to work.
