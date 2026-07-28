# Architecture Overview

ContextOS orchestrates six layers of SDLC intelligence. The **API contract**
defines Confirmed `POST /index` and `POST /context` shapes. Hybrid BM25 and
vector search remain the L5 retrieval path for code discovery questions.

## Key themes

- Repository packing and indexing
- Structural graph metadata
- Privacy defaults and ignore policy
