# Design Document — Lenny Growth Assistant

## 1. UI/UX Principles

- **Familiar**: Follows ChatGPT-like patterns users already understand
- **Grounded**: Every AI response shows its sources prominently
- **Fast**: Optimistic updates, loading animations, auto-scroll
- **Clean**: Dark theme with purposeful contrast and whitespace
- **Accessible**: Keyboard navigable, labeled controls, proper ARIA attributes

## 2. Information Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Application                            │
│                                                                │
│  ┌──────────┬─────────────────────────┬──────────────────────┐ │
│  │ Sidebar  │       Chat Area         │  Artifact Viewer     │ │
│  │          │                         │  (toggleable)        │ │
│  │ Sessions │  Messages with          │                      │ │
│  │ list     │  source citations       │  Renders MD/HTML     │ │
│  │          │                         │                      │ │
│  │ New Chat │  Starter prompts        │  Empty state when    │ │
│  │ button   │  (empty session)        │  no artifact         │ │
│  │          │                         │                      │ │
│  │ Ingest   │  Loading animation      │  Sandboxed iframe    │ │
│  │ button   │  (while generating)     │  for HTML            │ │
│  │          │                         │                      │ │
│  │ Provider │  Composer with          │                      │ │
│  │ badge    │  send button            │                      │ │
│  └──────────┴─────────────────────────┴──────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 3. Key Interaction States

### Empty State
- Welcome screen with gradient icon and description
- Suggests starting a new chat

### Active Session — No Messages
- Sparkles icon with prompt suggestions
- Four starter prompts covering common topics

### Active Session — Conversation
- Messages alternate between user (right) and assistant (left)
- Assistant messages render Markdown (headings, bold, bullets, code)
- Source citations appear as pill-shaped links below assistant messages
- Artifact button appears when a message includes a generated document

### Loading State
- Three pulsing dots animation while waiting for AI response
- Optimistic user message appears immediately

### Error State
- Structured error messages from backend
- Graceful handling when Ollama is unavailable

## 4. Responsive Behavior

### Desktop (≥768px)
- Three-column layout: Sidebar (280px) + Chat (flexible) + Artifact (45%, toggleable)
- Sidebar always visible
- Artifact viewer toggleable via button in header

### Mobile (<768px)
- Single column with hamburger menu
- Sidebar overlays as a drawer
- Artifact viewer takes full width when active
- Mobile header with app title

## 5. Accessibility Considerations

- All interactive elements have `aria-label` attributes
- Keyboard navigation with Tab/Enter on sessions
- Focus management on new chat and session switch
- `aria-current="page"` on active session
- Color contrast meets WCAG AA (light text on dark background)
- Auto-resizing textarea for comfortable typing
- Shift+Enter for multi-line input

## 6. Design Decisions

### Dark Theme
The dark theme reduces eye strain for extended use and creates a modern, premium feel. The gradient accents (indigo → cyan) provide visual interest without overwhelming.

### Source Citations as Pills
Pill-shaped links are compact, scannable, and clearly associated with the message. They link to the original Substack post when available.

### Artifact Viewer as Side Panel
Rather than modal or full-page, a side panel lets users reference both the conversation and the artifact simultaneously. The panel is 45% width on desktop, providing enough space for reading while keeping context visible.

### Loading Animation
Three pulsing dots are universally recognized as "typing" in chat interfaces. Combined with the avatar, it creates the sense of a responsive assistant.

### Starter Prompts
Four curated prompts help users understand what the system can do and provide immediate value. They cover the breadth of the dataset (growth, AI, product teams, essays).
