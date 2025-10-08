---
license: other
license_name: mrl
license_link: https://mistral.ai/licenses/MRL-0.1.md
language:
  - en
  - fr
  - de
  - es
  - it
  - pt
  - zh
  - ja
  - ru 
  - ko

extra_gated_description: If you want to learn more about how we process your personal data, please read our <a href="https://mistral.ai/terms/">Privacy Policy</a>.
---

# Model Card for Mistral-Large-Instruct-2407

Mistral-Large-Instruct-2407 is an advanced dense Large Language Model (LLM) of 123B parameters with state-of-the-art reasoning, knowledge and coding capabilities.

For more details about this model please refer to our release [blog post](https://mistral.ai/news/mistral-large-2407/).

## Key features
- **Multi-lingual by design:** Dozens of languages supported, including English, French, German, Spanish, Italian, Chinese, Japanese, Korean, Portuguese, Dutch and Polish.
- **Proficient in coding:** Trained on 80+ coding languages such as Python, Java, C, C++, Javacsript, and Bash. Also trained on more specific languages such as Swift and Fortran.
- **Agentic-centric:** Best-in-class agentic capabilities with native function calling and JSON outputting.
- **Advanced Reasoning:** State-of-the-art mathematical and reasoning capabilities.
- **Mistral Research License:** Allows usage and modification for research and non-commercial usages.
- **Large Context:** A large 128k context window.

## Metrics

### Base Pretrained Benchmarks

| Benchmark | Score |
| --- | --- |
| MMLU | 84.0% |


### Base Pretrained Multilingual Benchmarks (MMLU)
| Benchmark | Score |
| --- | --- |
| French | 82.8% |
| German | 81.6% |
| Spanish | 82.7% |
| Italian | 82.7% |
| Dutch | 80.7% |
| Portuguese | 81.6% |
| Russian | 79.0% |
| Korean | 60.1% |
| Japanese | 78.8% |
| Chinese | 74.8% |


### Instruction Benchmarks

| Benchmark | Score |
| --- | --- |
| MT Bench | 8.63 |
| Wild Bench | 56.3 |
| Arena Hard| 73.2 |

### Code & Reasoning Benchmarks
| Benchmark | Score |
| --- | --- |
| Human Eval | 92% |
| Human Eval Plus| 87% |
| MBPP Base| 80% |
| MBPP Plus| 69% |

### Math Benchmarks

| Benchmark | Score |
| --- | --- |
| GSM8K | 93% |
| Math Instruct (0-shot, no CoT) | 70% |
| Math Instruct (0-shot, CoT)| 71.5% |

## Usage

The model can be used with two different frameworks

- [`mistral_inference`](https://github.com/mistralai/mistral-inference): See [here](https://huggingface.co/mistralai/Mistral-Large-2407#mistral-inference)
- [`transformers`](https://github.com/huggingface/transformers): See [here](#transformers)

### Mistral Inference

#### Install

It is recommended to use `mistralai/Mistral-Large-2407` with [mistral-inference](https://github.com/mistralai/mistral-inference). For HF transformers code snippets, please keep scrolling.

```
pip install mistral_inference
```

#### Download

```py
from huggingface_hub import snapshot_download
from pathlib import Path

mistral_models_path = Path.home().joinpath('mistral_models', 'Large')
mistral_models_path.mkdir(parents=True, exist_ok=True)

snapshot_download(repo_id="mistralai/Mistral-Large-2407", allow_patterns=["params.json", "consolidated-*.safetensors", "tokenizer.model.v3"], local_dir=mistral_models_path)
```

#### Chat

After installing `mistral_inference`, a `mistral-chat` CLI command should be available in your environment.
Given the size of this model, you will need a node with several GPUs (more than 300GB cumulated vRAM).
If you have 8 GPUs on your machine, you can chat with the model using

```
torchrun --nproc-per-node 8 --no-python mistral-chat $HOME/mistral_models/Large --instruct --max_tokens 256 --temperature 0.7
```

*E.g.* Try out something like:
```
How expensive would it be to ask a window cleaner to clean all windows in Paris. Make a reasonable guess in US Dollar.
```

#### Instruct following

```py
from mistral_inference.transformer import Transformer
from mistral_inference.generate import generate

from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest

tokenizer = MistralTokenizer.from_file(f"{mistral_models_path}/tokenizer.model.v3")
model = Transformer.from_folder(mistral_models_path)

prompt = "How expensive would it be to ask a window cleaner to clean all windows in Paris. Make a reasonable guess in US Dollar."

completion_request = ChatCompletionRequest(messages=[UserMessage(content=prompt)])

tokens = tokenizer.encode_chat_completion(completion_request).tokens

out_tokens, _ = generate([tokens], model, max_tokens=64, temperature=0.7, eos_id=tokenizer.instruct_tokenizer.tokenizer.eos_id)
result = tokenizer.decode(out_tokens[0])

print(result)
```

#### Function calling

```py
from mistral_common.protocol.instruct.tool_calls import Function, Tool
from mistral_inference.transformer import Transformer
from mistral_inference.generate import generate

from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest


tokenizer = MistralTokenizer.from_file(f"{mistral_models_path}/tokenizer.model.v3")
model = Transformer.from_folder(mistral_models_path)

completion_request = ChatCompletionRequest(
    tools=[
        Tool(
            function=Function(
                name="get_current_weather",
                description="Get the current weather",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location.",
                        },
                    },
                    "required": ["location", "format"],
                },
            )
        )
    ],
    messages=[
        UserMessage(content="What's the weather like today in Paris?"),
        ],
)

tokens = tokenizer.encode_chat_completion(completion_request).tokens

out_tokens, _ = generate([tokens], model, max_tokens=256, temperature=0.7, eos_id=tokenizer.instruct_tokenizer.tokenizer.eos_id)
result = tokenizer.decode(out_tokens[0])

print(result)
```

### Transformers

> [!IMPORTANT]
> NOTE: Until a new release has been made, you need to install transformers from source:
> ```sh
> pip install git+https://github.com/huggingface/transformers.git
> ```

If you want to use Hugging Face `transformers` to generate text, you can do something like this.

```py
from transformers import pipeline

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]
chatbot = pipeline("text-generation", model="mistralai/Mistral-Large-2407")
chatbot(messages)
```

## Limitations

The Mistral Large model is a quick demonstration that the base model can be easily fine-tuned to achieve compelling performance. 
It does not have any moderation mechanisms. We're looking forward to engaging with the community on ways to
make the model finely respect guardrails, allowing for deployment in environments requiring moderated outputs.

## The Mistral AI Team

Albert Jiang, Alexandre Sablayrolles, Alexis Tacnet, Alok Kothari, Antoine Roux, Arthur Mensch, Audrey Herblin-Stoop, Augustin Garreau, Austin Birky, Bam4d, Baptiste Bout, Baudouin de Monicault, Blanche Savary, Carole Rambaud, Caroline Feldman, Devendra Singh Chaplot, Diego de las Casas, Diogo Costa, Eleonore Arcelin, Emma Bou Hanna, Etienne Metzger, Gaspard Blanchet, Gianna Lengyel, Guillaume Bour, Guillaume Lample, Harizo Rajaona, Henri Roussez, Hichem Sattouf, Ian Mack, Jean-Malo Delignon, Jessica Chudnovsky, Justus Murke, Kartik Khandelwal, Lawrence Stewart, Louis Martin, Louis Ternon, Lucile Saulnier, Lélio Renard Lavaud, Margaret Jennings, Marie Pellat, Marie Torelli, Marie-Anne Lachaux, Marjorie Janiewicz, Mickaël Seznec, Nicolas Schuhl, Niklas Muhs, Olivier de Garrigues, Patrick von Platen, Paul Jacob, Pauline Buche, Pavan Kumar Reddy, Perry Savas, Pierre Stock, Romain Sauvestre, Sagar Vaze, Sandeep Subramanian, Saurabh Garg, Sophia Yang, Szymon Antoniak, Teven Le Scao, Thibault Schueller, Thibaut Lavril, Thomas Wang, Théophile Gervet, Timothée Lacroix, Valera Nemychnikova, Wendy Shang, William El Sayed, William Marshall