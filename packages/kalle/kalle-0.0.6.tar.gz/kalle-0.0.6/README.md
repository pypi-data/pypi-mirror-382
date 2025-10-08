# kalle

![kalle](media/kalle_multi.jpg "kalle")

```bash
kalle -x "Briefly describe yourself for the README.md for your project. $(kalle -h)"
```

```bash
Hey there! I'm Kalle, your friendly personal assistant. I'm here to help you
with any questions or tasks you might have. I'm a smart CLI friend, which means
I can understand and respond to your messages in a conversational way. Think of
me as your go-to buddy for getting things done!
```

---
## Hello!

kalle is useful for anyone who wants a quick and easy way to get answers or complete
tasks without having to leave the command line. It's perfect for developers,
researchers, and anyone who wants to automate their workflow.

With kalle, you can:

- Get answers to common questions
- Have focused discussions on specific topics
- Incorporate documents from your local filesystem or web pages into your conversations
- Recall previous conversations
- Summarize content, create and edit files and more to get things done

![kalle_intro](media/kalle_intro.gif "kalle intro")

---
## Getting Started

To get started with kalle, simply install it with `pipx`:

```bash
pipx install kalle
kalle -h
```

Run for the first time!

```bash
kalle hi
```

*NOTE: When running for the first time, the a default model will be downloaded
(SmolLM-1.7b) for use with the llamacpp connector. This may take a few minutes.*

More information can be found in [the installation instructions](installation.md).

Detailed information on how to work with kalle be found in the [documentation](docs/README.md).

---
## Usage

Here are some simple examples of how to use kalle:

- **Simple example**: `kalle "hi"`
- **No conversation history**: `kalle -x "What's the capital of California?"`
- **Custom conversation**: `kalle -c partyplanning "Lets plan a party."`
- **Using a different profile**: `kalle -P ollama "Hello, world!"`

***For more examples, check out the [usage guide](docs/usage.md).***

---
## Features

**Profiles**: connect to any number of different endppints and language models

- Local and self hosted models are supported via llama.cpp and Ollama and TabbyAPI
- Vendor managed models can be accessed via Anthropic, OpenAI, Grok and Google VertexAI APIs

**Conversations**: kalle supports multiple conversations, so you can have focused discussions on specific topics.

- Create a new conversation: `kalle -c my_conversation "Hello, world!"`
- List all conversations: `kalle -l`
- Have a different conversation: `kalle -c my_other_conversation "Hello, other conversation!"`

**Piped input**: information can be piped into kalle on the command line.

- Reference command output: `git diff | kalle -x "Review this git diff, determine why the changes were made and generated a well formed git commit comment." `

**Document references**: kalle can incorporate documents from your local filesystem or web pages into your conversations.

- Reference a local file: `kalle -f "Tell me about this document: file://test.pdf"`
- Reference a web page: `kalle -f "What is this webpage about: https://www.fsf.org"`

**Tools**: tools can be invoked to accomplish various tasks

- Create a file: `kalle -t "Create a file containing the text 'Hello World'."`
- Send a desktop notification: `kalle -t "Send a desktop notification with a haiku about turtles."`

**Constrained generation**: (limited connector support) constrain generation with regex and json-schema

- Constrain with regex: `kalle -S $(date "+%s") -x --regex "HEADS|TAILS" "Flip a coin and tell me if its heads or tails."`
- Constrain with json-schema: `kalle -x -J schema.json -f "Reformat this content into json: file://data.md"`

**Patterns**: create building blocks of agentic functionality

- Combine a set of system prompt template, prompt template, constrainer and profile
- Pipe output from one pattern to the input of another
- Create streamlined workflows

**Memory:** You can add content to kalle's memory and use it during conversations!

- Add content and documents to memory (sqlite-vec): `kalle -S -R README.md < README.md`
- Directly query the memory: `kalle -Q Give me a good smashburger recipe`
- Automatically use memories relevant to your prompt: `kalle -M Give me a good smashburger recipe`
- Use separate and distinct memory-stores: `kalle -K notes What have I written about agentic architecture\?`

***For more examples, check out the [usage guide](docs/usage.md).***

---
## Resources

Similar projects or alternatives include:

- [AIChat](https://github.com/sigoden/aichat)
- [Elia](https://github.com/darrenburns/elia)
- [Fabric](https://github.com/danielmiessler/fabric)
- [Mods](https://github.com/charmbracelet/mods)
- [oterm](https://github.com/ggozad/oterm)
- [Terminal GPT](https://github.com/aandrew-me/tgpt)

---
## Copyright & License

**Copyright (C) 2024-2025 Wayland Holdings, LLC**

This software is licensed under the GNU Affero GPL
(see [LICENSE.md](LICENSE.md))

This software uses a number of third party libraries. See
[3RDPARTY.licenses](3RDPARTY.licenses) for details. NOTE: This may be out of
date. See the script `./bin/update_license_data.sh` to get the latest.

---
*Copyright (C) 2024-2025 Wayland Holdings, LLC*

<img src="https://fe2.net/static/fe2_logo_kc.png" width="24" alt="fe2">

<img src="https://gc.fe2.net/count?p=/c/kalle/README.md" width="1" alt="fe2">
