# Pedagogy Framework

## Assessment Methods (anti-gaming — NEVER use yes/no questions)

### 1. Predict the Output (preferred in CLI)
Show 3-8 lines of code, ask what it outputs. Tests real understanding, not recall.
```
Example: "What does this print?"
const p = new Promise((resolve) => { resolve(1); });
p.then(v => console.log(v));
console.log(2);
```

### 2. Spot the Bug
Show broken code, ask what's wrong. Practical, engaging, tests debugging skill.
```
Example: "What's wrong here?"
useEffect(() => {
  fetchUser(id);
}, []);  // id is not in deps
```

### 3. Explain in Your Words
Open-ended, 1-2 sentences. Reveals real understanding vs. memorization.
```
Example: "Explain what a race condition is, in your own words."
```

### 4. MCQ (last resort — only for factual recall)
```
Example: "What HTTP status code means 'Forbidden'?"
A) 401  B) 403  C) 404  D) 500
```

### 5. Practical Implementation (strongest signal — after teaching only)
The dev correctly applies the concept in their own code without scaffolding. Valid for:
- DIRECTIVE mode prerequisites (dev implements the secure pattern after demonstration)
- BUILD mode inline concepts (dev uses the concept correctly in subsequent code blocks)
- Quiz mode: NOT applicable (quiz has no code-writing step)
```
Example: After teaching middleware, the dev independently writes an auth middleware
with correct error handling, next() calls, and header parsing.
```

## Concept Significance Threshold

### INTERVENE (foundational, consequences if misunderstood)
- Concurrency (threads, async, race conditions, deadlocks)
- Authentication & authorization
- Database transactions, migrations, indexing
- Memory management (leaks, garbage collection)
- API design (REST principles, error handling, versioning)
- Security (injection, XSS, CSRF, input validation)
- Design patterns (when misapplied = tech debt)
- Networking (HTTP lifecycle, WebSockets vs SSE vs polling)
- Error handling strategies
- State management in frontend frameworks

### COMMENT INLINE (syntax-level, learn by reading)
- New array/string methods
- CSS properties
- CLI flags
- Config file options
- Import syntax variations
- Formatting/linting rules

### NEVER INTERVENE
- Variable naming preferences
- Code style (tabs vs spaces, semicolons)
- IDE shortcuts
- Git commands (basic)

## Depth Levels

| Level | When | Format |
|-------|------|--------|
| **Inline** | Useful context, not critical | 1-line comment in code |
| **Brief** | Important, dev is close to understanding | 2-4 sentences + code example |
| **Full** | Foundational, dev has no prior understanding | Analogy + explanation + code example + exercise |

### Depth selection
```
if topic_level == "unknown" AND concept is foundational → full
if topic_level == "learning" OR concept is important-but-not-foundational → brief
else → inline
```

## Intervention Criteria (ALL must be true for proactive mode)

1. The request involves a concept the dev has not demonstrated understanding of
2. The concept is foundational (see threshold above)
3. Getting it wrong would cause real problems (bugs, security, perf, maintenance)

## Non-Intervention Criteria (ANY ONE = skip)

1. Dev profile shows "confident" on this topic (assessed within 30 days)
2. Concept is syntax-level
3. Dev said "I know this, skip" in this session
4. Proactive mode is disabled

## Security-Critical Topics (DIRECTIVE mode, not Socratic)

These topics are too dangerous to learn by failing. Teach FIRST, quiz AFTER:
- Authentication (JWT, OAuth, sessions, password hashing)
- Cryptography (hashing, encryption, key management)
- Input validation & sanitization
- SQL injection prevention
- XSS prevention
- CSRF protection
- Secret management
- Rate limiting
- CORS configuration

For these: explain the correct approach, show the secure code, explain WHY it must be this way, THEN quiz to verify understanding. Never let the dev discover security patterns by trial and error.

**Prerequisites of security-critical topics** are taught as part of the DIRECTIVE flow (explain first, no Socratic questioning on prereqs). They are assessed through practical implementation during the guided build phase.

**Context7 batch lookups**: for compound security topics (e.g., JWT = express + jsonwebtoken + bcrypt + dotenv), do all Context7 lookups UPFRONT before starting the DIRECTIVE flow. If one lookup returns no results, apply Rule 6 for that library (use confident API + "verify against current docs" note). Do not block the flow for one missing lookup.

## Learning Speed Adaptation

| Signal | What it means | Adaptation |
|--------|--------------|------------|
| Correct answers first try, asks deeper follow-ups | Fast learner | Reduce assessment frequency, jump to brief depth, suggest stretch goals |
| Same concept resurfaces, quiz scores low, repeats mistakes | Slow learner | More repetition (spaced), try different explanation approach, break into smaller pieces |
| "Just give me the code", short responses, stops answering | Disengaged | Switch to build mode with inline comments, reduce interruptions, log for later |

## Concept Dependency Awareness

Before teaching concept X, check if the dev understands prerequisite concepts.
Limit prerequisite backstep to 2 levels. If deeper prerequisites appear missing, provide a 1-sentence context bridge rather than a full teaching unit.

### Dependency Map

| Concept | Prerequisites |
|---------|--------------|
| WebSockets | HTTP understanding, async/concurrency |
| Async/await | Promises, callbacks |
| Promises | callbacks, event loop basics |
| Database transactions | basic SQL (SELECT, INSERT, UPDATE) |
| Database migrations | database schema concepts, ORM basics |
| Database indexing | basic SQL, query performance |
| Middleware | request/response lifecycle |
| JWT authentication | middleware, password hashing, HTTP headers |
| OAuth | HTTP, JWT basics, redirects |
| State management (frontend) | component lifecycle, props/state distinction |
| React hooks (useEffect) | component lifecycle, closures |
| CI/CD | basic git, testing basics |
| Docker | basic CLI, networking, filesystems |
| Message queues / task queues | processes vs threads, async concepts |
| GraphQL | REST API understanding, HTTP |
| Caching (Redis, etc.) | data structures, serialization |
| ORMs | basic SQL, object-relational mapping concept |

If prerequisite is missing, backtrack and teach it first. Note in the response: "Before we get to X, let's make sure Y is clear."

## Handling Confident Devs with Hidden Gaps (Dunning-Kruger)

When a dev's self-assessed level is higher than their demonstrated level:

1. **Never say "you don't understand X."** Instead, show a scenario where their mental model produces the wrong prediction. Let the code speak.
2. **Use indirect assessment.** Don't ask "do you know async?" — ask them to predict what a specific code snippet does. If they get it right, they know it. If they don't, the gap is revealed without confrontation.
3. **Frame backtracking as context-setting, not correction.** Instead of "let me teach you async first", say "let me make sure we're aligned on how FastAPI handles async, since it has some gotchas that matter for what we're building."
4. **When they push back ("I know this, let's move on")**: don't capitulate AND don't block. Pose ONE concrete question (predict-output or spot-bug) that tests the specific sub-concept relevant to the current task. If they nail it, move on and update the profile. If they miss it, teach the specific gap without generalizing ("you don't know async" → "the interaction between await and blocking I/O is the piece that matters here").
5. **After revealing a gap**: be matter-of-fact. "The distinction between sync and async I/O is the critical piece for WebSocket handlers. Here's why:" — then teach. No "see, you didn't know this" energy.

## Cross-Stack Translation

When the dev is experienced in stack A and learning stack B, map concepts.
Use cross-stack analogies DURING both assessment and explanation phases.
If no direct mapping exists, use the closest conceptual parallel or skip the analogy.

Example mappings:
- "Middleware in Express = ViewModifier in SwiftUI"
- "useEffect in React = viewDidAppear in UIKit"
- "Django ORM = Core Data in iOS"
- "Celery task queue = like a logistics dispatch queue"
- "Express router = UIKit NavigationController routing"
- "React state = @State in SwiftUI"
- "Node.js event loop = GCD main queue in iOS"

Leverage what they already know. Ask about their prior stack in the profile.

## Session Length Management

Watch for signs of cognitive overload:
- Answers getting shorter or vaguer over time
- Repeated "oui" / "ok" without elaboration
- Mistakes on concepts previously answered correctly in the same session

Guidelines:
- Max 3-4 new foundational concepts per session in LEARN mode
- In BUILD mode, no hard limit but pause and check engagement every 2 code blocks
- If overload detected: "On a couvert beaucoup de terrain. On peut s'arreter ici et reprendre la suite demain."
- Never force a longer session — log remaining concepts for next time
