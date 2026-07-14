---
id: SRC-XXX
kind: source
created_at: <ISO 8601>
hash: sha256:<filled-by-harness>
title: "<one line: source title or filename>"
file_path: "inputs/<filename>.md"
source_type: <audit | research | notes | draft | analysis | recommendation | calendar | blueprint | roadmap | interview | competitive-brief | other>
round: <initial | notes | draft | correction | final | single>
supersedes: null               # or "[SRC-NNN#hash]" of an earlier round this corrects
superseded_by: null            # filled by harness when a later round registers
author: null                   # or "<name>" of who/what produced the source
date: null                     # or YYYY-MM-DD source date
weight: secondary              # primary | secondary | contextual
tags: []
---

# Source SRC-XXX — <Title>

## Summary

<2-3 sentences: what this source covers, in the agent's words. Not a content extraction (T-002 handles that); just enough for a reader of the inventory to know what the source is for.>

## Why this source is in scope

<One sentence linking the source to OR-001.synthesis_purpose. If the source is contextual (background only), say so.>

## Round-relationship notes (optional)

<If this source is part of a round chain, note which round and what it corrects from the prior round. Cite the prior source by [SRC-NNN#hash]. Filled when relevant; omit if round=single.>
