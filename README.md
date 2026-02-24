# Honeypot MCP Server

Four AI-powered tools for Claude Code and other MCP clients, backed by Google Gemini Flash.

## Tools

### `red_team_attack`
Run adversarial analysis on any document using 3 expert personas (VC Partner, Technical Architect, Regulatory Attorney). Returns synthesized scores, kill shots, and actionable fixes.

- **full** — All 3 personas in parallel
- **quick** — Single VC/Devil's Advocate pass
- **brainstorm** — Creative exploration of alternatives

### `score_content`
Score written content on 6 dimensions (clarity, readability, SEO, persuasiveness, structure, originality) with specific improvement recommendations.

### `deep_research`
Research any topic using Gemini with real-time web search grounding. Returns key findings, source summaries, conflicting information, and knowledge gaps.

### `verse_assist`
Generate, fix, or explain Verse code for Unreal Editor for Fortnite (UEFN). Understands Verse syntax, device APIs, event patterns, concurrency, and failable expressions. The only AI tool on Smithery purpose-built for Verse.

- **generate** — Create complete Verse scripts from English descriptions
- **fix** — Debug existing Verse code with specific error explanations
- **explain** — Break down what Verse code does in plain English

## Setup

1. Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Install via Smithery or add to your MCP config:

```json
{
  "mcpServers": {
    "honeypot": {
      "command": "python",
      "args": ["/path/to/honeypot-mcp/server.py"],
      "env": {
        "GEMINI_API_KEY": "your-key-here"
      }
    }
  }
}
```

## Limits

- Max input: 10,000 characters per call
- Rate limit: 3 calls/minute per caller
- Daily cap: 500 calls globally

## Built by [Chinchilla AI](https://chinchilla-ai.com)
