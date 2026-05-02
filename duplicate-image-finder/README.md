# Duplicate Image Finder

Duplicate Image Finder is a small experimental project I built to group visually similar images together and make photo sorting easier. I built it because I had a drive filled with a huge number of duplicates and needed a better way to sort them.

The idea is simple: when a folder contains many near-duplicates, it becomes hard to quickly find the best shot. This tool helps by comparing images through vector embeddings and clustering the ones that look the same or very close to each other.

I used SigLIP2 to extract image vectors and compare them in a semantic way, instead of relying only on file hashes or exact duplicates. This makes it possible to detect similar photos, not just identical ones.

The project is designed to run locally, with open-source models, so the whole workflow can stay private.

I also added an Agno-based agent to make it easier to manage groups and ungrouped images through a more natural conversational interface. That part is still experimental, but it was a good fit for quickly prototyping this kind of experience.