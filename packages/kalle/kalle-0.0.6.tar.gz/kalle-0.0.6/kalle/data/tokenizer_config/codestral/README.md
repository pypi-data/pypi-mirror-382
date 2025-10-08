---
inference: false
license: other
license_name: mnpl
license_link: https://mistral.ai/licences/MNPL-0.1.md
tags:
- code
language:
- code
---

# Model Card for Codestral-22B-v0.1

Codestrall-22B-v0.1 is trained on a diverse dataset of 80+ programming languages, including the most popular ones, such as Python, Java, C, C++, JavaScript, and Bash (more details in the [Blogpost](https://mistral.ai/news/codestral/)). The model can be queried:
- As instruct, for instance to answer any questions about a code snippet (write documentation, explain, factorize) or to generate code following specific indications
- As Fill in the Middle (FIM), to predict the middle tokens between a prefix and a suffix (very useful for software development add-ons like in VS Code)


## Inference

It's the same as Mistral 7B.

## Limitations

The Codestral-22B-v0.1 does not have any moderation mechanisms. We're looking forward to engaging with the community on ways to
make the model finely respect guardrails, allowing for deployment in environments requiring moderated outputs.

## License

Codestral-22B-v0.1 is released under the `MNLP-0.1` license.

## The Mistral AI Team

Albert Jiang, Alexandre Sablayrolles, Alexis Tacnet, Antoine Roux, Arthur Mensch, Audrey Herblin-Stoop, Baptiste Bout, Baudouin de Monicault, Blanche Savary, Bam4d, Caroline Feldman, Devendra Singh Chaplot, Diego de las Casas, Eleonore Arcelin, Emma Bou Hanna, Etienne Metzger, Gianna Lengyel, Guillaume Bour, Guillaume Lample, Harizo Rajaona, Henri Roussez, Jean-Malo Delignon, Jia Li, Justus Murke, Kartik Khandelwal, Lawrence Stewart, Louis Martin, Louis Ternon, Lucile Saulnier, Lélio Renard Lavaud, Margaret Jennings, Marie Pellat, Marie Torelli, Marie-Anne Lachaux, Marjorie Janiewicz, Mickael Seznec, Nicolas Schuhl, Patrick von Platen, Romain Sauvestre, Pierre Stock, Sandeep Subramanian, Saurabh Garg, Sophia Yang, Szymon Antoniak, Teven Le Scao, Thibaut Lavril, Thibault Schueller, Timothée Lacroix, Théophile Gervet, Thomas Wang, Valera Nemychnikova, Wendy Shang, William El Sayed, William Marshall