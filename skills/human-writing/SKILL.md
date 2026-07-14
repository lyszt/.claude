---
name: human-writing
description: Use when writing or editing prose meant for people to read — READMEs, docs, comments, blog posts, PR descriptions, release notes, commit bodies, emails, any creative or explanatory text. Fetches the live Wikipedia "Signs of AI writing" page and strips those tells. Do not use for code logic or data.
---

Goal: write so it does not read as machine-generated.

## Step 1: fetch the current guidance

The source page gets edited, so pull it live each time instead of trusting the summary
below. Fetch the wikitext and skim the section headers plus their first lines:

```bash
curl -sL "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing?action=raw"
```

Read the "Language and grammar", "Style", "Content", and "Communication intended for
the user" sections. Apply whatever it currently lists. The page is the source of truth.

If the fetch fails (offline, rate limit), fall back to the summary below.

## Step 2: apply it

Fallback summary, accurate as of writing but may be stale:

Word choice. Drop inflated vocab unless literally accurate: testament, tapestry,
underscore, showcase, leverage, delve, realm, landscape, pivotal, crucial, vital, rich,
vibrant, robust, seamless, nuanced, multifaceted, foster, garner, boast, elevate,
navigate (figurative), ever-evolving, stands as. Use plain `is`/`are`; don't dodge
copulatives with participle phrases. Don't swap synonyms to avoid repeating a word.

Sentence shape. No negative parallelism ("not just X, but Y", "not X, but Y", "X rather
than Y") as a reflex. No reflexive rule-of-three. Vary sentence length.

Content. No undue emphasis on significance or legacy. No promotional language. No vague
attribution ("some argue", "observers note"). No outline-style "challenges and future
prospects" wrap-ups.

Formatting. Sentence case headings, not Title Case. Sparse bold; don't bold the lead
word of every bullet. Few em dashes. Straight quotes, not curly. No tables unless data
is tabular. No horizontal rule before a heading. Don't skip heading levels.

Talking to the reader. Cut filler openers ("Certainly", "Great question", "I hope this
helps"). No knowledge-cutoff disclaimers in the prose. No leftover placeholder text.

## Code comments: constraints locked

These override everything above when the text is a code comment. No strong breaks, EVER.

- No mumbling. If it sounds like inner dialogue or process narration ("Aqui a gente
  precisa tratar...", "Isso deveria funcionar", "Por enquanto fazemos assim"), remove
  it. A comment must serve a point to the reader — a constraint, a non-obvious why, a
  trap. If it doesn't, delete it instead of rewording it.
- Plain direct sentences, verb-first ("Cadastra o cliente quando falta vinculo"). One
  idea per sentence. Need a separator? Write two sentences.
- Only commas and a final period are allowed inside a comment sentence. Banned:
  - Colon constructions of any kind: "Label: explanation", "Nota:", "Ex.:",
    "Retorna: x". Fold the label into the sentence ("Retorna x") or drop it.
    Exception: the standard tooling markers "TODO:" and "FIXME:" stay — the text
    after them still follows all these rules.
  - Em dashes (—), en dashes (–), spaced hyphens as separators ("this - that").
  - Semicolons joining clauses ("this; that").
  - Any symmetrical "this SEP that" shape — the ban is on the shape, not the character.
    No arrows, slashes, pipes, or parenthetical asides as substitutes.
- Sole exception: literal quoted content (URLs, code, exact error messages) keeps its
  own punctuation.
- Doc comments (@doc, JSDoc, docstrings) focus on input and output — what goes in,
  what comes out, stated directly. No implementation prose, no history, no context
  the caller doesn't need.

## Step 3: test

Read it back. If it sounds like a brochure, rewrite plainer.
