# Priodex

**Priodex** is a tech-news aggregator. It pulls articles from 12 technology, AI and startup publications, writes a short AI summary for each one with Groq, and shows a single ranked feed in a React web app.

The project also uses classic data structures in a real application:

- a **max heap** ranks the feed by priority,
- a **trie** powers prefix search over titles and keywords,
- an **in-memory hash map** serves article lookups without a database round trip.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Available Commands](#available-commands)
- [API Reference](#api-reference)
- [News Sources](#news-sources)
- [Project Structure](#project-structure)
- [Known Issues and Areas for Improvement](#known-issues-and-areas-for-improvement)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Multi-source ingestion:** 12 RSS-based scrapers. Where the feed text is too thin, they fetch and clean the full article page.
- **AI summaries:** each new article is summarized in 2–3 sentences by Groq (`openai/gpt-oss-20b`).
- **Priority feed:** articles are scored by recency and category, and the top 25 are served from a max heap.
- **Instant search:** debounced, as-you-type prefix search over title words and extracted keywords, backed by a trie.
- **Article detail view:** a modal shows the full text, categories, keywords, a link to the original and an on-demand summary.
- **Scheduled refresh:** the Python worker scrapes and summarizes on startup, then every 24 hours.

---

## Architecture

Priodex has three services that share one MongoDB database (`tech-radar`):

```text
                  ┌──────────────────────────┐
  RSS feeds  ───► │  python-service          │
  article pages   │  scrapers + scheduler    │ ──── Groq API (summaries)
                  └────────────┬─────────────┘
                               │ insert articles / summaries
                               ▼
                  ┌──────────────────────────┐
                  │  MongoDB  (tech-radar)   │
                  │  articles · summaries    │
                  └────────────┬─────────────┘
                               │ read all articles at startup
                               ▼
                  ┌──────────────────────────┐
                  │  backend (Express)       │
                  │  Map cache · Trie · Heap │
                  └────────────┬─────────────┘
                               │ REST / JSON  (port 5001)
                               ▼
                  ┌──────────────────────────┐
                  │  frontend (React + Vite) │  (port 5173)
                  └──────────────────────────┘
```

**Data flow**

1. `scheduler.py` runs every scraper. Each scraper reads its RSS feed and inserts up to 1–2 new articles into `articles` with `processed: false`.
2. The summarizer picks up every unprocessed article, calls Groq, writes the result to `summaries`, and sets `processed: true`.
3. When the backend starts, it loads **all** articles once and builds its cache, trie and heap.
4. The frontend fetches the top 25 articles. It runs searches and fetches summaries on demand.

> **Important:** the backend's indexes are built only at startup. Articles scraped while the backend is running don't appear until the backend restarts.

---

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, Vite 7, React Router 7, Zustand, Axios, Tailwind CSS 3, daisyUI 4, react-hot-toast |
| Backend | Node.js (ES modules), Express 5, Mongoose 9, CORS, dotenv |
| Ingestion | Python 3, requests, BeautifulSoup4, `xml.etree`, pymongo, schedule, python-dotenv |
| AI | Groq Chat Completions API, model `openai/gpt-oss-20b` |
| Database | MongoDB |

---

## How It Works

### Data model

**`articles`**

| Field | Type | Notes |
| --- | --- | --- |
| `title` | string | Required |
| `url` | string | Unique index (created by Mongoose when the backend starts) |
| `source` | string | Publication name, e.g. `TechCrunch` |
| `content` | string | Cleaned article text, or the feed description as a fallback |
| `scrapedDate` | date / ISO string | Time the article was **scraped**, not when it was published |
| `categories` | string[] | Taken directly from the RSS `<category>` tags, with a per-scraper fallback |
| `keywords` | string[] | Matched against a fixed per-scraper keyword list (max 8) |
| `processed` | boolean | `true` once a summary exists |

**`summaries`**: `articleId` (unique, references `articles._id`), `summary`, `generatedAt`.

### Priority scoring

Defined in [backend/src/utils/priorityScore.js](backend/src/utils/priorityScore.js):

```text
recencyScore  = 100 × e^(−hoursOld / 24)        // 100 → ~37 after 24 h → ~14 after 48 h
categoryScore = highest weight among the article's categories (default 3)
priority      = 0.7 × recencyScore + 0.3 × categoryScore
```

Category weights range from `AI: 10` and `Startups: 9` down to `Hardware: 5`. Any category not in the table gets 3.

Every article's score goes into a `MaxHeap`. `GET /api/articles` clones the heap and extracts the top 25.

### Search

[backend/src/services/searchService.js](backend/src/services/searchService.js) inserts each title word longer than 2 characters (plus the word `AI`) and each keyword into a `Trie`, together with the article ID. A query walks the trie to its prefix node and collects every article ID below it. The first 15 matches are then looked up in the cache.

### Caching

[backend/src/services/cacheService.js](backend/src/services/cacheService.js) keeps a `Map<articleId, document>` holding every article, so `GET /api/articles/:id` and search results never hit MongoDB.

---

## Getting Started

### Prerequisites

| Requirement | Notes |
| --- | --- |
| Node.js 18+ and npm | Developed with Node 22 |
| Python 3.10+ | Developed with Python 3.13 |
| MongoDB | Local (`mongod`, Homebrew, or Docker) or MongoDB Atlas |
| Groq API key | Free at [console.groq.com](https://console.groq.com). Only the summarizer needs it |

To start MongoDB locally with Docker:

```bash
docker run -d --name priodex-mongo -p 27017:27017 mongo:7
```

### 1. Clone the repository

```bash
git clone <repository-url> priodex
cd priodex
```

### 2. Configure environment variables

Create **`backend/.env`**:

```dotenv
MONGODB_URI=mongodb://127.0.0.1:27017/tech-radar
PORT=5001
```

Create **`python-service/.env`**:

```dotenv
MONGODB_URI=mongodb://127.0.0.1:27017/tech-radar
GROQ_API_KEY=your-groq-api-key
```

Rules for these files:

- **The URI must end in `/tech-radar`.** The Python service always writes to the `tech-radar` database, whatever the URI says. The backend reads from the database named in the URI, and Mongoose falls back to `test` when there isn't one. For Atlas, use `mongodb+srv://user:pass@cluster.example.net/tech-radar?retryWrites=true`.
- **`PORT` must be `5001`.** The frontend has `http://localhost:5001` hard-coded. If `PORT` is missing, Express picks a random port.
- Both `.env` files are git-ignored. Never commit them.

### 3. Install dependencies

```bash
# Backend
cd backend
npm install

# Frontend
cd ../frontend
npm install

# Python service
cd ../python-service
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install pymongo python-dotenv requests beautifulsoup4 schedule
```

### 4. Run the project

Start the services **in this order**, each in its own terminal.

**Terminal 1: ingest data** (run this first so the database has articles)

```bash
cd python-service
source .venv/bin/activate
python scheduler.py
```

This runs all scrapers and the summarizer once (about 21 articles per run), then stays running and repeats every 24 hours. Stop it with `Ctrl+C`. To scrape a single source for testing, run that scraper on its own, for example `python -m scrapers.techcrunch_scraper`.

**Terminal 2: backend API**

```bash
cd backend
node index.js
```

A successful start prints:

```text
Database connected
Article cache built with N articles
Search index built
Priority heap built
Server is running on port:5001
```

> Use `node index.js`. `npm run dev` and `npm test` are currently broken (see [Known Issues](#known-issues-and-areas-for-improvement)).

**Terminal 3: frontend**

```bash
cd frontend
npm run dev
```

Open **http://localhost:5173**.

### 5. Verify

```bash
curl http://localhost:5001/                         # {"message":"Priodex is running"}
curl http://localhost:5001/api/articles             # {"success":true,"count":N,"data":[...]}
curl "http://localhost:5001/api/articles/search?q=startup"
```

---

## Available Commands

### Backend (`backend/`)

| Command | Status | Purpose |
| --- | --- | --- |
| `node index.js` | ✅ Works | Start the API |
| `npm run dev` | ❌ Broken | Points to the missing `src/index.js`. `nodemon` isn't listed as a dependency either |
| `npm test` | ❌ Broken | Points to the missing `src/index.js`. No test suite exists |

### Frontend (`frontend/`)

| Command | Status | Purpose |
| --- | --- | --- |
| `npm run dev` | ✅ Works | Vite dev server on port 5173 |
| `npm run build` | ✅ Works | Production build to `frontend/dist` |
| `npm run preview` | ✅ Works | Serve the production build locally |
| `npm run lint` | ⚠️ Fails | 3 unused-variable errors and 1 hook-dependency warning |

### Python service (`python-service/`)

| Command | Purpose |
| --- | --- |
| `python scheduler.py` | Scrape, summarize, then repeat every 24 h |
| `python -m scrapers.<name>_scraper` | Run one scraper once |
| `python ai_processor.py` | Summarizes the first stored article and saves the result, which tests the Groq key. Fails if that article already has a summary |

---

## API Reference

Base URL: `http://localhost:5001`. Article endpoints are mounted under `/api` so they can't collide with frontend page routes such as `/articles`. All endpoints are unauthenticated `GET` requests that return JSON.

| Endpoint | Description | Success response |
| --- | --- | --- |
| `/` | Liveness check | `{ "message": "Priodex is running" }` |
| `/api/articles` | Top 25 articles by priority | `{ "success": true, "count": 25, "data": [Article] }` |
| `/api/articles/search?q=<term>` | Prefix search, at least 2 chars, at most 15 results | `{ "success": true, "count": n, "data": [Article] }` |
| `/api/articles/:id` | One article from the cache | `{ "success": true, "data": Article }` |
| `/api/articles/:id/summary` | AI summary for an article | `{ "success": true, "data": { "articleId", "summary", "generatedAt" } }` |

**Errors:** `400` when the query is shorter than 2 characters, `404` when the article or summary is missing, `500` on server errors. A malformed `:id` on `/summary` currently returns `500` instead of `400`.

---

## News Sources

| Source | Scraper | Feed | Articles per run |
| --- | --- | --- | --- |
| TechCrunch | `techcrunch_scraper.py` | techcrunch.com/feed | 2 |
| VentureBeat | `venturebeat_scraper.py` | venturebeat.com/feed | 2 |
| Wired (AI / Science / Ideas only) | `wired_scraper.py` | wired.com/feed/rss | 2 |
| Engadget | `engadget_scraper.py` | engadget.com/rss.xml | 1 |
| GitHub Blog | `github_scraper.py` | github.blog/feed | 2 |
| The New Stack | `newsstack_scraper.py` | thenewstack.io/blog/feed | 2 |
| IEEE Spectrum (AI) | `ieee_scraper.py` | spectrum.ieee.org/…/artificial-intelligence.rss | 1 |
| AI News | `ainews_scraper.py` | artificialintelligence-news.com/feed | 2 |
| AI TechPark | `aitechpark_scraper.py` | ai-techpark.com/category/ai/feed | 2 |
| Crunchbase News | `crunchbase_scraper.py` | news.crunchbase.com/feed | 2 |
| Tech.eu (Deep Tech) | `techeu_scraper.py` | tech.eu/category/deep-tech/feed | 1 |
| Indie Hackers | `indiehackers_scraper.py` | feed.indiehackers.world/posts.rss | 2 |

To change how many articles a scraper takes per run, edit the `count=` default in its `fetch_*` function.

---

## Project Structure

```text
priodex/
├── backend/
│   ├── index.js                      Express entry point; builds the indexes on startup
│   └── src/
│       ├── config/database.js        MongoDB connection
│       ├── controllers/              Request handlers for /api/articles
│       ├── routes/                   Route definitions
│       ├── models/                   Article and Summary Mongoose schemas
│       ├── dsa/                      MaxHeap and Trie implementations
│       ├── services/                 Cache, search (trie) and heap services
│       ├── utils/priorityScore.js    Ranking formula
│       └── jobs/                     Empty placeholder files (unused)
├── frontend/
│   ├── index.html
│   └── src/
│       ├── main.jsx, App.jsx         App bootstrap and routes
│       ├── components/Navbar.jsx     Logo and debounced search box
│       ├── pages/HomePage.jsx        Feed grid, article modal, summary button
│       ├── store/feedStore.js        Zustand store (feed, search, summaries)
│       └── lib/axios.js              API client
└── python-service/
    ├── scheduler.py                  Entry point: scrape → summarize → repeat every 24 h
    ├── app.py                        MongoDB client and collections
    ├── ai_processor.py               Groq summarization
    └── scrapers/                     One module per news source
```

---

## Known Issues and Areas for Improvement

These findings come from a full review of the codebase. They are grouped by impact. Each issue links to where it lives.

### 1. Data freshness and pipeline integrity (highest impact)

| Issue | Where | Effect | Suggested fix |
| --- | --- | --- | --- |
| The backend indexes are built only once, at startup | [backend/index.js](backend/index.js) | New articles stay invisible until a manual restart. Priority scores are frozen at their startup values. | Rebuild periodically (e.g. every 15 min) or use MongoDB change streams. The empty `src/jobs/` files look like they were meant for this. |
| Four scrapers never check for duplicates | `github`, `newsstack`, `wired`, `indiehackers` scrapers | With the unique `url` index in place, the first already-stored item throws `DuplicateKeyError`, and the scraper aborts and saves nothing. Without the index, duplicates are inserted. | Use `update_one({"url": url}, {"$setOnInsert": doc}, upsert=True)` in every scraper. |
| Scrapers hide their own failures | All scrapers (`except Exception: return []`, bare `except:`) | A broken feed or selector fails silently. The `Scraper failed` log in `scheduler.py` never fires, because the scrapers catch every error themselves. | Log errors with the source name, or let them propagate to the scheduler. |
| Different database-name rules | [python-service/app.py](python-service/app.py) vs [backend/src/config/database.js](backend/src/config/database.js) | Python always writes to `tech-radar`, while the backend reads the database named in the URI. A URI without a database name gives an empty feed with no error. | Read the database name from one shared env var in both services. |
| The server accepts requests before MongoDB connects | [backend/index.js](backend/index.js) | `app.listen` runs first, so early requests get an empty feed. `connectDB` logs failures and carries on, and the process exits only ~10 s later on a Mongoose buffering timeout. | Connect and build the indexes first, call `listen` last, and exit on connection failure. |

### 2. Ranking and search quality

| Issue | Where | Effect | Suggested fix |
| --- | --- | --- | --- |
| Recency dominates the score | [priorityScore.js](backend/src/utils/priorityScore.js) | Recency contributes up to 70 points, while the whole category range adds only 0.9–3. For fresh articles that difference equals less than an hour of age, so categories barely matter. | Normalize both terms to 0–1 before weighting, or multiply by the category weight instead of adding. |
| Scrape time is used instead of publish time | All scrapers (`scrapedDate`) | RSS `<pubDate>` is ignored, so a week-old article looks brand-new when first scraped. | Parse `pubDate` into a `publishedAt` field and rank on that. |
| Mixed timezones in timestamps | 7 scrapers use `datetime.utcnow()`, 5 use `datetime.now()`. All store naive ISO strings | JavaScript reads offset-less strings as local time, so on a UTC+5 machine the UTC-stamped sources look 5 h older. That costs about 13 priority points. | Store real BSON dates in UTC: `datetime.now(timezone.utc)`. Don't call `.isoformat()`. |
| Categories don't match the weight table | Scrapers vs `categoryWeights` | Feeds produce `AI` and `Artificial intelligence`, `Venture` and `venture`, even people's names. Only exact matches get a weight, so most articles fall back to 3. `'Cloud': '7.2'` is a string; it happens to work only because `Math.max` converts it. | Map raw feed categories to a fixed list of canonical categories inside the scrapers. |
| Keyword matching uses raw substrings | `kw in text` in every scraper | `ai` matches *said*, *again*; `app` matches *approach*. Almost every article gets tagged `ai`, so searching "ai" returns nearly the whole collection. | Match on word boundaries (`re.search(rf"\b{kw}\b", text)`) or use a keyword library (e.g. YAKE, KeyBERT). |
| Search results aren't ranked, and multi-word titles aren't matched | [articles.controller.js](backend/src/controllers/articles.controller.js), [trie.js](backend/src/dsa/trie.js) | The 15 results come out in trie order, not by priority. Queries are matched as a single prefix, so a phrase like `open source` matches keyword entries but not title words. | Sort matches by priority score. Split the query into terms and intersect the result sets. |
| The search query isn't URL-encoded | [feedStore.js](frontend/src/store/feedStore.js) | `C++` reaches the server as `C  ` and becomes a 1-character prefix (it matched 12 unrelated articles in testing). `&` and `#` break the query entirely. | `axiosInstance.get('/articles/search', { params: { q } })` (the `/api` prefix comes from the axios base URL). |

### 3. Correctness bugs

- **The search never clears when the input is emptied by typing.** [Navbar.jsx](frontend/src/components/Navbar.jsx) checks `inputValue === 0` (a number). Deleting the text with Backspace leaves stale results on screen; only the ✕ button clears them. Fix: `inputValue.length === 0`.
- **The search spinner gets stuck after an error.** `performSearch` doesn't reset `isSearching` in its `catch` block. Out-of-order responses from fast typing can also overwrite newer results.
- **An invalid ObjectId returns 500.** `new mongoose.Types.ObjectId(id)` throws on bad input in `displaySummarizedArticle`. Validate with `mongoose.isValidObjectId(id)` and return 400. The same handler's 404 uses the key `summary` instead of `message`.
- **Schema defaults are evaluated once.** `default: Date.now()` in both models fixes the timestamp at server start. Use `default: Date.now` (no call).
- **`content: required` vs. reality.** Python bypasses Mongoose validation, so the database may hold documents the backend schema considers invalid.
- **The homepage shows sources that no longer exist.** The scrolling tags in [HomePage.jsx](frontend/src/pages/HomePage.jsx) list Medium and DevTo, whose scrapers were removed. Several real sources (AI News, Tech.eu) are missing. Generate this list from the data instead.
- **A dead field.** `ai_processor.py` reads `article["fullContentAvailable"]`, which no scraper ever writes.

### 4. Build, tooling and deployment

- **Broken backend scripts.** `"dev": "nodemon src/index.js"` and `"test": "node src/index.js"` point to a file that doesn't exist, and `nodemon` isn't a dependency. Change both to `index.js` (or use `node --watch index.js`), and replace `test` with a real runner.
- **No Python dependency manifest.** Add `requirements.txt` (or `pyproject.toml`) with pinned versions.
- **11 unused backend dependencies.** `axios`, `bull`, `dayjs`, `express-rate-limit`, `express-validator`, `helmet`, `ioredis`, `joi`, `mongodb`, `morgan` and `winston` are installed but never imported. Either wire up the useful ones (`helmet`, `express-rate-limit`, `morgan`) or remove them.
- **Production builds can't reach the API.** In production, [axios.js](frontend/src/lib/axios.js) uses base URL `/`, but nothing serves the frontend and the API from the same origin, and no proxy is configured. Use a `VITE_API_URL` env var, or a Vite dev proxy plus a reverse proxy in production. The CORS origin is also hard-coded to `http://localhost:5173`.
- **Lint fails.** There are unused variables in `Navbar.jsx` and `feedStore.js`.
- **No tests, CI, Docker setup or process manager.** A `docker-compose.yml` with `mongo`, `backend`, `python-service` and `frontend` would reduce setup to one command.

### 5. Scalability and code health

- **Three full collection scans at startup.** The cache, trie and heap each run `Article.find({})` and keep full Mongoose documents in memory. Query once with `.lean()` and a projection, then build all three from that result.
- **`GET /api/articles` costs O(n log n) per request.** It rebuilds a full heap copy on every call. Keep a precomputed sorted top-N list instead, refreshed whenever the indexes rebuild.
- **Unbounded trie traversal.** A 2-character prefix collects every ID below it, with repeated array concatenation and `Set` building at each level. Cap the number of results while traversing.
- **Duplicated scraper code.** 12 scrapers × ~150 lines repeat the same `get_text`, `clean_html`, `extract_keywords` and insertion logic. Move this into a shared base module plus one config entry per source (feed URL, selectors, fallback category). `feedparser` would replace the hand-written XML parsing.
- **No pagination or filtering.** The feed is capped at 25 items, with no way to page, filter by source or category, or sort.
- **No logging framework.** Output is `console.log` and `print` only, with emoji, and stray debug logs run on every search.
- **Smaller issues.** `HomePage` is exported as `Example`. One modal is rendered for each of the 25 articles. `datetime.utcnow()` is deprecated in Python 3.12+. The "✓ Loaded N articles" toast fires on every page load.

### Suggested roadmap

1. **Make it reliable:** fix the backend scripts, add `requirements.txt`, make all inserts idempotent, surface scraper errors, connect to the database before listening.
2. **Keep it fresh:** rebuild the indexes on a timer or with change streams. Store `publishedAt` as UTC BSON dates.
3. **Rank it well:** normalize categories, use word-boundary keyword matching, rebalance the priority formula, sort search results by score.
4. **Ship it:** add Docker Compose, env-based API URL and CORS, `helmet`, rate limiting, input validation, and tests with CI.
5. **Grow it:** pagination, source and category filters, a shared scraper framework.

---

## Security Considerations

The current setup is meant for **local development**, not public deployment.

- The API has no authentication, rate limiting, input validation or security headers (`helmet` and `express-rate-limit` are installed but unused).
- CORS is not access control. Non-browser clients can call the API directly.
- Scraped URLs are rendered as outbound links without checking the scheme. Allow only `http:` and `https:` before storing or rendering them.
- Scrapers fetch URLs taken from third-party feeds. Add scheme and host validation, redirect limits and egress restrictions to reduce SSRF risk.
- Article text goes straight into the Groq prompt. Treat it as untrusted (prompt injection), and keep the existing 5,000-character cap.
- The Groq request has no timeout and doesn't call `raise_for_status()`, so a slow or failing provider can stall the summarizer.
- Use a least-privilege MongoDB user, keep the database on a private network, and never commit `.env` files or API keys.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Feed is empty | No data yet, or the backend reads a different database | Run `python scheduler.py` first. Make sure both URIs end in `/tech-radar`. Restart the backend. |
| New articles don't appear | Indexes are built only at startup | Restart the backend (`node index.js`). |
| Frontend shows network errors | Backend not on port 5001 | Set `PORT=5001` in `backend/.env`. |
| `Cannot find module .../src/index.js` | Broken `npm run dev` / `npm test` script | Run `node index.js` instead. |
| `buffering timed out after 10000ms` | MongoDB unreachable | Start MongoDB and check `MONGODB_URI`. |
| "No summary available" for an article | Summarizer hasn't run, or the Groq call failed | Check `GROQ_API_KEY` and the `scheduler.py` output, then rerun it. |
| `ModuleNotFoundError: pymongo` / `schedule` | venv not active or packages not installed | `source .venv/bin/activate`, then install the packages from step 3. |
| A scraper inserts nothing | Duplicate URL, feed change, or a silently swallowed error | Run that scraper alone and add logging to its `except` blocks. |
