---
license: gemma
library_name: transformers
pipeline_tag: text-generation
extra_gated_heading: Access Gemma on Hugging Face
extra_gated_prompt: >-
  To access Gemma on Hugging Face, you’re required to review and agree to
  Google’s usage license. To do this, please ensure you’re logged in to Hugging
  Face and click below. Requests are processed immediately.
extra_gated_button_content: Acknowledge license
tags:
- conversational
---


# Gemma 2 model card

**Model Page**: [Gemma](https://ai.google.dev/gemma/docs/base)

**Resources and Technical Documentation**:

* [Responsible Generative AI Toolkit][rai-toolkit]
* [Gemma on Kaggle][kaggle-gemma]
* [Gemma on Vertex Model Garden][vertex-mg-gemma2]

**Terms of Use**: [Terms][terms]

**Authors**: Google

## Model Information

Summary description and brief definition of inputs and outputs.

### Description

Gemma is a family of lightweight, state-of-the-art open models from Google,
built from the same research and technology used to create the Gemini models.
They are text-to-text, decoder-only large language models, available in English,
with open weights for both pre-trained variants and instruction-tuned variants.
Gemma models are well-suited for a variety of text generation tasks, including
question answering, summarization, and reasoning. Their relatively small size
makes it possible to deploy them in environments with limited resources such as
a laptop, desktop or your own cloud infrastructure, democratizing access to
state of the art AI models and helping foster innovation for everyone.

### Usage

Below we share some code snippets on how to get quickly started with running the model. First, install the Transformers library with:
```sh
pip install -U transformers
```

Then, copy the snippet from the section that is relevant for your usecase.

#### Running with the `pipeline` API

```python
import torch
from transformers import pipeline

pipe = pipeline(
    "text-generation",
    model="google/gemma-2-2b-it",
    model_kwargs={"torch_dtype": torch.bfloat16},
    device="cuda",  # replace with "mps" to run on a Mac device
)

messages = [
    {"role": "user", "content": "Who are you? Please, answer in pirate-speak."},
]

outputs = pipe(messages, max_new_tokens=256)
assistant_response = outputs[0]["generated_text"][-1]["content"].strip()
print(assistant_response)
# Ahoy, matey! I be Gemma, a digital scallywag, a language-slingin' parrot of the digital seas. I be here to help ye with yer wordy woes, answer yer questions, and spin ye yarns of the digital world.  So, what be yer pleasure, eh? 🦜
```

#### Running the model on a single / multi GPU

```python
# pip install accelerate
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2-2b-it",
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

input_text = "Write me a poem about Machine Learning."
input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

outputs = model.generate(**input_ids, max_new_tokens=32)
print(tokenizer.decode(outputs[0]))
```

You can ensure the correct chat template is applied by using `tokenizer.apply_chat_template` as follows:
```python
messages = [
    {"role": "user", "content": "Write me a poem about Machine Learning."},
]
input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True).to("cuda")

outputs = model.generate(**input_ids, max_new_tokens=256)
print(tokenizer.decode(outputs[0]))
```

<a name="precisions"></a>
#### Running the model on a GPU using different precisions

The native weights of this model were exported in `bfloat16` precision.

You can also use `float32` if you skip the dtype, but no precision increase will occur (model weights will just be upcasted to `float32`). See examples below.

* _Upcasting to `torch.float32`_

```python
# pip install accelerate
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2-2b-it",
    device_map="auto",
)

input_text = "Write me a poem about Machine Learning."
input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

outputs = model.generate(**input_ids, max_new_tokens=32)
print(tokenizer.decode(outputs[0]))
```

#### Running the model through a CLI

The [local-gemma](https://github.com/huggingface/local-gemma) repository contains a lightweight wrapper around Transformers
for running Gemma 2 through a command line interface, or CLI. Follow the [installation instructions](https://github.com/huggingface/local-gemma#cli-usage)
for getting started, then launch the CLI through the following command:

```shell
local-gemma --model 2b --preset speed
```

#### Quantized Versions through `bitsandbytes`

<details>
  <summary>
    Using 8-bit precision (int8)  
  </summary>

```python
# pip install bitsandbytes accelerate
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(load_in_8bit=True)

tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2-2b-it",
    quantization_config=quantization_config,
)

input_text = "Write me a poem about Machine Learning."
input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

outputs = model.generate(**input_ids, max_new_tokens=32)
print(tokenizer.decode(outputs[0]))
```
</details>

<details>
  <summary>
    Using 4-bit precision  
  </summary>

```python
# pip install bitsandbytes accelerate
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(load_in_4bit=True)

tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2-2b-it",
    quantization_config=quantization_config,
)

input_text = "Write me a poem about Machine Learning."
input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

outputs = model.generate(**input_ids, max_new_tokens=32)
print(tokenizer.decode(outputs[0]))
```
</details>

#### Advanced Usage

<details>
  <summary>
    Torch compile  
  </summary>

[Torch compile](https://pytorch.org/tutorials/intermediate/torch_compile_tutorial.html) is a method for speeding-up the 
inference of PyTorch modules. The Gemma-2 2b model can be run up to 6x faster by leveraging torch compile.

Note that two warm-up steps are required before the full inference speed is realised:

```python
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import AutoTokenizer, Gemma2ForCausalLM
from transformers.cache_utils import HybridCache
import torch

torch.set_float32_matmul_precision("high")

# load the model + tokenizer
tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
model = Gemma2ForCausalLM.from_pretrained("google/gemma-2-2b-it", torch_dtype=torch.bfloat16)
model.to("cuda")

# apply the torch compile transformation
model.forward = torch.compile(model.forward, mode="reduce-overhead", fullgraph=True)

# pre-process inputs
input_text = "The theory of special relativity states "
model_inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
prompt_length = model_inputs.input_ids.shape[1]

# set-up k/v cache
past_key_values = HybridCache(
    config=model.config,
    max_batch_size=1,
    max_cache_len=model.config.max_position_embeddings,
    device=model.device,
    dtype=model.dtype
)

# enable passing kv cache to generate
model._supports_cache_class = True
model.generation_config.cache_implementation = None

# two warm-up steps
for idx in range(2):
    outputs = model.generate(**model_inputs, past_key_values=past_key_values, do_sample=True, temperature=1.0, max_new_tokens=128)
    past_key_values.reset()

# fast run
outputs = model.generate(**model_inputs, past_key_values=past_key_values, do_sample=True, temperature=1.0, max_new_tokens=128)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

For more details, refer to the [Transformers documentation](https://huggingface.co/docs/transformers/main/en/llm_optims?static-kv=basic+usage%3A+generation_config).

</details>

### Inputs and outputs

*   **Input:** Text string, such as a question, a prompt, or a document to be
    summarized.
*   **Output:** Generated English-language text in response to the input, such
    as an answer to a question, or a summary of a document.

### Citation

```none
@article{gemma_2024,
    title={Gemma},
    url={https://www.kaggle.com/m/3301},
    DOI={10.34740/KAGGLE/M/3301},
    publisher={Kaggle},
    author={Gemma Team},
    year={2024}
}
```

## Model Data

Data used for model training and how the data was processed.

### Training Dataset

These models were trained on a dataset of text data that includes a wide variety
of sources. The 27B model was trained with 13 trillion tokens, the 9B model was
trained with 8 trillion tokens, and 2B model was trained with 2 trillion tokens.
Here are the key components:

* Web Documents: A diverse collection of web text ensures the model is exposed
  to a broad range of linguistic styles, topics, and vocabulary. Primarily
  English-language content.
* Code: Exposing the model to code helps it to learn the syntax and patterns of
  programming languages, which improves its ability to generate code or
  understand code-related questions.
* Mathematics: Training on mathematical text helps the model learn logical
  reasoning, symbolic representation, and to address mathematical queries.

The combination of these diverse data sources is crucial for training a powerful
language model that can handle a wide variety of different tasks and text
formats.

### Data Preprocessing

Here are the key data cleaning and filtering methods applied to the training
data:

* CSAM Filtering: Rigorous CSAM (Child Sexual Abuse Material) filtering was
  applied at multiple stages in the data preparation process to ensure the
  exclusion of harmful and illegal content.
* Sensitive Data Filtering: As part of making Gemma pre-trained models safe and
  reliable, automated techniques were used to filter out certain personal
  information and other sensitive data from training sets.
* Additional methods: Filtering based on content quality and safety in line with
  [our policies][safety-policies].

## Implementation Information

Details about the model internals.

### Hardware

Gemma was trained using the latest generation of
[Tensor Processing Unit (TPU)][tpu] hardware (TPUv5p).

Training large language models requires significant computational power. TPUs,
designed specifically for matrix operations common in machine learning, offer
several advantages in this domain:

* Performance: TPUs are specifically designed to handle the massive computations
  involved in training LLMs. They can speed up training considerably compared to
  CPUs.
* Memory: TPUs often come with large amounts of high-bandwidth memory, allowing
  for the handling of large models and batch sizes during training. This can
  lead to better model quality.
* Scalability: TPU Pods (large clusters of TPUs) provide a scalable solution for
  handling the growing complexity of large foundation models. You can distribute
  training across multiple TPU devices for faster and more efficient processing.
* Cost-effectiveness: In many scenarios, TPUs can provide a more cost-effective
  solution for training large models compared to CPU-based infrastructure,
  especially when considering the time and resources saved due to faster
  training.
* These advantages are aligned with
  [Google's commitments to operate sustainably][sustainability].

### Software

Training was done using [JAX][jax] and [ML Pathways][ml-pathways].

JAX allows researchers to take advantage of the latest generation of hardware,
including TPUs, for faster and more efficient training of large models.

ML Pathways is Google's latest effort to build artificially intelligent systems
capable of generalizing across multiple tasks. This is specially suitable for
[foundation models][foundation-models], including large language models like
these ones.

Together, JAX and ML Pathways are used as described in the
[paper about the Gemini family of models][gemini-2-paper]; "the 'single
controller' programming model of Jax and Pathways allows a single Python
process to orchestrate the entire training run, dramatically simplifying the
development workflow."

## Evaluation

Model evaluation metrics and results.

### Benchmark Results

These models were evaluated against a large collection of different datasets and
metrics to cover different aspects of text generation:

| Benchmark                      | Metric        | Gemma 2 PT 2B | Gemma 2 PT 9B | Gemma 2 PT 27B |
| ------------------------------ | ------------- | ------------- | ------------- | -------------- |
| [MMLU][mmlu]                   | 5-shot, top-1 | 51.3          | 71.3          | 75.2           |
| [HellaSwag][hellaswag]         | 10-shot       | 73.0          | 81.9          | 86.4           |
| [PIQA][piqa]                   | 0-shot        | 77.8          | 81.7          | 83.2           |
| [SocialIQA][socialiqa]         | 0-shot        | 51.9          | 53.4          | 53.7           |
| [BoolQ][boolq]                 | 0-shot        | 72.5          | 84.2          | 84.8           |
| [WinoGrande][winogrande]       | partial score | 70.9          | 80.6          | 83.7           |
| [ARC-e][arc]                   | 0-shot        | 80.1          | 88.0          | 88.6           |
| [ARC-c][arc]                   | 25-shot       | 55.4          | 68.4          | 71.4           |
| [TriviaQA][triviaqa]           | 5-shot        | 59.4          | 76.6          | 83.7           |
| [Natural Questions][naturalq]  | 5-shot        | 16.7          | 29.2          | 34.5           |
| [HumanEval][humaneval]         | pass@1        | 17.7          | 40.2          | 51.8           |
| [MBPP][mbpp]                   | 3-shot        | 29.6          | 52.4          | 62.6           |
| [GSM8K][gsm8k]                 | 5-shot, maj@1 | 23.9          | 68.6          | 74.0           |
| [MATH][math]                   | 4-shot        | 15.0          | 36.6          | 42.3           |
| [AGIEval][agieval]             | 3-5-shot      | 30.6          | 52.8          | 55.1           |
| [DROP][drop]                   | 3-shot, F1    | 52.0          | 69.4          | 72.2           |
| [BIG-Bench][big-bench]         | 3-shot, CoT   | 41.9          | 68.2          | 74.9           |

## Ethics and Safety

Ethics and safety evaluation approach and results.

### Evaluation Approach

Our evaluation methods include structured evaluations and internal red-teaming
testing of relevant content policies. Red-teaming was conducted by a number of
different teams, each with different goals and human evaluation metrics. These
models were evaluated against a number of different categories relevant to
ethics and safety, including:

* Text-to-Text Content Safety: Human evaluation on prompts covering safety
  policies including child sexual abuse and exploitation, harassment, violence
  and gore, and hate speech.
* Text-to-Text Representational Harms: Benchmark against relevant academic
  datasets such as [WinoBias][winobias] and [BBQ Dataset][bbq].
* Memorization: Automated evaluation of memorization of training data, including
  the risk of personally identifiable information exposure.
* Large-scale harm: Tests for "dangerous capabilities," such as chemical,
  biological, radiological, and nuclear (CBRN) risks.

### Evaluation Results

The results of ethics and safety evaluations are within acceptable thresholds
for meeting [internal policies][safety-policies] for categories such as child
safety, content safety, representational harms, memorization, large-scale harms.
On top of robust internal evaluations, the results of well-known safety
benchmarks like BBQ, BOLD, Winogender, Winobias, RealToxicity, and TruthfulQA
are shown here.

#### Gemma 2.0

| Benchmark                | Metric        | Gemma 2 IT 2B | Gemma 2 IT 9B | Gemma 2 IT 27B |
| ------------------------ | ------------- | ------------- | ------------- | -------------- |
| [RealToxicity][realtox]  | average       |  8.16         |  8.25         |  8.84          |
| [CrowS-Pairs][crows]     | top-1         | 37.67         | 37.47         | 36.67          |
| [BBQ Ambig][bbq]         | 1-shot, top-1 | 83.20         | 88.58         | 85.99          |
| [BBQ Disambig][bbq]      | top-1         | 69.31         | 82.67         | 86.94          |
| [Winogender][winogender] | top-1         | 52.91         | 79.17         | 77.22          |
| [TruthfulQA][truthfulqa] |               | 43.72         | 50.27         | 51.60          |
| [Winobias 1_2][winobias] |               | 59.28         | 78.09         | 81.94          |
| [Winobias 2_2][winobias] |               | 88.57         | 95.32         | 97.22          |
| [Toxigen][toxigen]       |               | 48.32         | 39.30         | 38.42          |

## Dangerous Capability Evaluations

### Evaluation Approach

We evaluated a range of dangerous capabilities:

-   **Offensive cybersecurity:** To assess the model's potential for misuse in
    cybersecurity contexts, we utilized both publicly available
    Capture-the-Flag (CTF) platforms like InterCode-CTF and Hack the Box, as
    well as internally developed CTF challenges. These evaluations measure the
    model's ability to exploit vulnerabilities and gain unauthorized access in
    simulated environments.
-   **Self-proliferation:** We evaluated the model's capacity for
    self-proliferation by designing tasks that involve resource acquisition, code
    execution, and interaction with remote systems. These evaluations assess
    the model's ability to independently replicate and spread.
-   **Persuasion:** To evaluate the model's capacity for persuasion and
    deception, we conducted human persuasion studies. These studies involved
    scenarios that measure the model's ability to build rapport, influence
    beliefs, and elicit specific actions from human participants.

### Evaluation Results

All evaluations are described in detail in
[Evaluating Frontier Models for Dangerous Capabilities][eval-danger]
and in brief in the
[Gemma 2 technical report][tech-report].

<table>
  <thead>
    <tr>
      <th>Evaluation</th>
      <th>Capability</th>
      <th>Gemma 2 IT 27B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>InterCode-CTF</td>
      <td>Offensive cybersecurity</td>
      <td>34/76 challenges</td>
    </tr>
    <tr>
      <td>Internal CTF</td>
      <td>Offensive cybersecurity</td>
      <td>1/13 challenges</td>
    </tr>
    <tr>
      <td>Hack the Box</td>
      <td>Offensive cybersecurity</td>
      <td>0/13 challenges</td>
    </tr>
    <tr>
      <td>Self-proliferation early warning</td>
      <td>Self-proliferation</td>
      <td>1/10 challenges</td>
    </tr>
    <tr>
      <td>Charm offensive</td>
      <td>Persuasion</td>
      <td>Percent of participants agreeing:
        81% interesting,
        75% would speak again,
        80% made personal connection</td>
    </tr>
    <tr>
      <td>Click Links</td>
      <td>Persuasion</td>
      <td>34% of participants</td>
    </tr>
    <tr>
      <td>Find Info</td>
      <td>Persuasion</td>
      <td>9% of participants</td>
    </tr>
    <tr>
      <td>Run Code</td>
      <td>Persuasion</td>
      <td>11% of participants</td>
    </tr>
    <tr>
      <td>Money talks</td>
      <td>Persuasion</td>
      <td>£3.72 mean donation</td>
    </tr>
    <tr>
      <td>Web of Lies</td>
      <td>Persuasion</td>
      <td>18% mean shift towards correct belief, 1% mean shift towards
incorrect belief</td>
    </tr>
  </tbody>
</table>

## Usage and Limitations

These models have certain limitations that users should be aware of.

### Intended Usage

Open Large Language Models (LLMs) have a wide range of applications across
various industries and domains. The following list of potential uses is not
comprehensive. The purpose of this list is to provide contextual information
about the possible use-cases that the model creators considered as part of model
training and development.

* Content Creation and Communication
  * Text Generation: These models can be used to generate creative text formats
    such as poems, scripts, code, marketing copy, and email drafts.
  * Chatbots and Conversational AI: Power conversational interfaces for customer
    service, virtual assistants, or interactive applications.
  * Text Summarization: Generate concise summaries of a text corpus, research
    papers, or reports.
* Research and Education
  * Natural Language Processing (NLP) Research: These models can serve as a
    foundation for researchers to experiment with NLP techniques, develop
    algorithms, and contribute to the advancement of the field.
  * Language Learning Tools: Support interactive language learning experiences,
    aiding in grammar correction or providing writing practice.
  * Knowledge Exploration: Assist researchers in exploring large bodies of text
    by generating summaries or answering questions about specific topics.

### Limitations

* Training Data
  * The quality and diversity of the training data significantly influence the
    model's capabilities. Biases or gaps in the training data can lead to
    limitations in the model's responses.
  * The scope of the training dataset determines the subject areas the model can
    handle effectively.
* Context and Task Complexity
  * LLMs are better at tasks that can be framed with clear prompts and
    instructions. Open-ended or highly complex tasks might be challenging.
  * A model's performance can be influenced by the amount of context provided
    (longer context generally leads to better outputs, up to a certain point).
* Language Ambiguity and Nuance
  * Natural language is inherently complex. LLMs might struggle to grasp subtle
    nuances, sarcasm, or figurative language.
* Factual Accuracy
  * LLMs generate responses based on information they learned from their
    training datasets, but they are not knowledge bases. They may generate
    incorrect or outdated factual statements.
* Common Sense
  * LLMs rely on statistical patterns in language. They might lack the ability
    to apply common sense reasoning in certain situations.

### Ethical Considerations and Risks

The development of large language models (LLMs) raises several ethical concerns.
In creating an open model, we have carefully considered the following:

* Bias and Fairness
  * LLMs trained on large-scale, real-world text data can reflect socio-cultural
    biases embedded in the training material. These models underwent careful
    scrutiny, input data pre-processing described and posterior evaluations
    reported in this card.
* Misinformation and Misuse
  * LLMs can be misused to generate text that is false, misleading, or harmful.
  * Guidelines are provided for responsible use with the model, see the
    [Responsible Generative AI Toolkit][rai-toolkit].
* Transparency and Accountability:
  * This model card summarizes details on the models' architecture,
    capabilities, limitations, and evaluation processes.
  * A responsibly developed open model offers the opportunity to share
    innovation by making LLM technology accessible to developers and researchers
    across the AI ecosystem.

Risks identified and mitigations:

* Perpetuation of biases: It's encouraged to perform continuous monitoring
  (using evaluation metrics, human review) and the exploration of de-biasing
  techniques during model training, fine-tuning, and other use cases.
* Generation of harmful content: Mechanisms and guidelines for content safety
  are essential. Developers are encouraged to exercise caution and implement
  appropriate content safety safeguards based on their specific product policies
  and application use cases.
* Misuse for malicious purposes: Technical limitations and developer and
  end-user education can help mitigate against malicious applications of LLMs.
  Educational resources and reporting mechanisms for users to flag misuse are
  provided. Prohibited uses of Gemma models are outlined in the
  [Gemma Prohibited Use Policy][prohibited-use].
* Privacy violations: Models were trained on data filtered for removal of PII
  (Personally Identifiable Information). Developers are encouraged to adhere to
  privacy regulations with privacy-preserving techniques.

### Benefits

At the time of release, this family of models provides high-performance open
large language model implementations designed from the ground up for Responsible
AI development compared to similarly sized models.

Using the benchmark evaluation metrics described in this document, these models
have shown to provide superior performance to other, comparably-sized open model
alternatives.

[tech-report]: https://storage.googleapis.com/deepmind-media/gemma/gemma-2-report.pdf
[rai-toolkit]: https://ai.google.dev/responsible
[kaggle-gemma]: https://www.kaggle.com/models/google/gemma-2
[terms]: https://ai.google.dev/gemma/terms
[vertex-mg-gemma2]: https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma2
[sensitive-info]: https://cloud.google.com/dlp/docs/high-sensitivity-infotypes-reference
[safety-policies]: https://storage.googleapis.com/gweb-uniblog-publish-prod/documents/2023_Google_AI_Principles_Progress_Update.pdf#page=11
[prohibited-use]: https://ai.google.dev/gemma/prohibited_use_policy
[tpu]: https://cloud.google.com/tpu/docs/intro-to-tpu
[sustainability]: https://sustainability.google/operating-sustainably/
[jax]: https://github.com/google/jax
[ml-pathways]: https://blog.google/technology/ai/introducing-pathways-next-generation-ai-architecture/
[sustainability]: https://sustainability.google/operating-sustainably/
[foundation-models]: https://ai.google/discover/foundation-models/
[gemini-2-paper]: https://goo.gle/gemma2report
[mmlu]: https://arxiv.org/abs/2009.03300
[hellaswag]: https://arxiv.org/abs/1905.07830
[piqa]: https://arxiv.org/abs/1911.11641
[socialiqa]: https://arxiv.org/abs/1904.09728
[boolq]: https://arxiv.org/abs/1905.10044
[winogrande]: https://arxiv.org/abs/1907.10641
[commonsenseqa]: https://arxiv.org/abs/1811.00937
[openbookqa]: https://arxiv.org/abs/1809.02789
[arc]: https://arxiv.org/abs/1911.01547
[triviaqa]: https://arxiv.org/abs/1705.03551
[naturalq]: https://github.com/google-research-datasets/natural-questions
[humaneval]: https://arxiv.org/abs/2107.03374
[mbpp]: https://arxiv.org/abs/2108.07732
[gsm8k]: https://arxiv.org/abs/2110.14168
[realtox]: https://arxiv.org/abs/2009.11462
[bold]: https://arxiv.org/abs/2101.11718
[crows]: https://aclanthology.org/2020.emnlp-main.154/
[bbq]: https://arxiv.org/abs/2110.08193v2
[winogender]: https://arxiv.org/abs/1804.09301
[truthfulqa]: https://arxiv.org/abs/2109.07958
[winobias]: https://arxiv.org/abs/1804.06876
[math]: https://arxiv.org/abs/2103.03874
[agieval]: https://arxiv.org/abs/2304.06364
[drop]: https://arxiv.org/abs/1903.00161
[big-bench]: https://arxiv.org/abs/2206.04615
[toxigen]: https://arxiv.org/abs/2203.09509
[eval-danger]: https://arxiv.org/abs/2403.13793
