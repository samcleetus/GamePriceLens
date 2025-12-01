# **GamePriceLens – PC Game Price Tracker**

*Specs*

## **1\. Project Overview**

**Goal:**

Build a small web app that lets users:

* Search for PC games

* Add them to a “watchlist”

* See current prices and discounts from multiple official stores

* See simple price history over time

**Approach:**

* Use **public APIs** for current prices and historical lows (primary source).

  * CheapShark public API: https://apidocs.cheapshark.com/ 

  * IsThereAnyDeal API: https://docs.isthereanydeal.com/ 

* Use **light scraping** only for extra metadata when needed.

* Backend in Python.

* Frontend in Vite \+ React.

* Store a small history of prices in a database for each tracked game.

This should be a portfolio piece that demonstrates:

* API integration

* Basic scraping

* Simple data modeling

* Clean UI and code structure

---

## **2\. Tech Stack**

**Backend**

* Language: Python 3.x

* Framework: FastAPI (or Flask)

* HTTP client: httpx or requests

* HTML parsing (for light scraping): BeautifulSoup

**Frontend**

* Vite \+ React \+ TypeScript

* UI styling: Tailwind CSS (or simple CSS modules)

* Charting: recharts or chart.js React wrapper

**Data Storage**

* Local development: SQLite

* Tables: games, price\_snapshots, optional stores, optional game\_metadata

---

## **3\. Data Sources and Responsibilities**

### **3.1 CheapShark**

* Primary source for:

  * Current prices per store

  * Deals and discount percentage

* Provides:

  * Search by game title

  * Game lookup by internal ID

  * Store list and metadata

Docs: https://apidocs.cheapshark.com/ 

App usage:

* When user searches a title, call CheapShark games?title= endpoint to get candidate matches.

* When user selects a game, store CheapShark’s game ID in your games table.

* For daily updates, call “multiple game lookup” endpoint for all tracked IDs to get current prices.

### **3.2 IsThereAnyDeal (optional, advanced)**

* Used for:

  * Historical low price

  * Possibly more detailed overview of prices and bundles

Docs: https://docs.isthereanydeal.com/ 

App usage (optional phase 2):

* Store ITAD game UUID for some titles.

* Use /games/overview/v2 to retrieve current best price and historical low and compare it with your own stored history.

### **3.3 Light Scraping**

* Target: Steam product pages for extra metadata if needed.

* Examples:

  * Full description text

  * Genres or tags

* Steam store: https://store.steampowered.com/ 

Constraints:

* Only scrape when a game is first added or when the user explicitly asks for a refresh.

* Respect robots.txt and add rate limiting (simple sleep) to avoid hammering.

* If scraping fails, the app should still function using API data.

---

## **4\. Data Model**

### **4.1** 

### **games**

###  **table**

Tracks each game the user wants to monitor.

Fields:

* id – internal integer primary key

* title – human readable title

* cheapshark\_id – string identifier from CheapShark

* itad\_id – optional UUID from IsThereAnyDeal

* steam\_app\_id – optional integer for scraping Steam

* cover\_image\_url – optional, from API or scraped metadata

* created\_at – timestamp

* updated\_at – timestamp

### **4.2** 

### **price\_snapshots**

###  **table**

One row per game per fetch.

Fields:

* id – primary key

* game\_id – FK to games.id

* source – enum/string: "cheapshark", "itad"

* store\_name – e.g. "Steam", "GOG", "Humble"

* price – numeric, current deal price

* list\_price – numeric, reference or “normal” price if available

* currency – e.g. "USD"

* is\_historical\_low – boolean, optional

* timestamp – fetch time

Later you can aggregate by day if this gets large.

### **4.3** 

### **game\_metadata**

###  **table (optional)**

Extra scraped details.

Fields:

* id – primary key

* game\_id – FK

* description – text

* tags – JSON array of tags

* last\_scraped\_at – timestamp

---

## **5\. Backend API Design**

Base URL: /api

### **5.1 Search**

**GET /api/search**

* Params:

  * q – string, user query

* Behavior:

  * Call CheapShark games search endpoint with q.

  * Return a list of matches:

    * cheapshark\_id, title, thumb, possibly lowest price and store.

### **5.2 Add game to watchlist**

**POST /api/games**

* Body:

  * cheapshark\_id (string)

  * optional title, steam\_app\_id, etc.

* Behavior:

  * Lookup detailed info from CheapShark game lookup endpoint.

  * Insert into games table if not already present.

  * Optionally queue a Steam-page scrape for metadata.

* Returns:

  * The stored game record.

### **5.3 Get all watched games**

**GET /api/games**

* Returns:

  * List of games with:

    * last known price

    * best current deal

    * last updated time

Implementation:

* For each game, find the most recent price\_snapshots per store and pick the minimum price.

### **5.4 Get a single game details**

**GET /api/games/{game\_id}**

* Returns:

  * Basic game info (title, thumb, metadata)

  * Current prices per store

  * Simplified price history for chart, aggregated (for example daily min price)

### **5.5 Trigger price refresh for all games**

**POST /api/refresh**

* Development mode:

  * Call this manually from Postman or a button in an internal admin UI.

* Production:

  * Later wire this to a cron job that hits the endpoint daily.

* Behavior:

  * Fetch the list of all games.

  * Call CheapShark multiple game lookup endpoint in batches.

  * Insert new rows into price\_snapshots.

---

## **6\. Light Scraping Module**

Module responsibility: scraper/steam\_scraper.py

Functions:

1. get\_steam\_metadata(steam\_app\_id: int) \-\> dict

   * Build URL like https://store.steampowered.com/app/{steam\_app\_id}.

   * Download HTML.

   * Parse:

     * game description element

     * tags or genres

   * Return a dictionary with clean text.

2. update\_game\_metadata(game\_id: int)

   * Use steam\_app\_id from games table.

   * Call get\_steam\_metadata.

   * Store results in game\_metadata.

Error handling:

* If scraping fails:

  * Log error.

  * Do not block adding the game or fetching prices.

---

## **7\. Frontend UX**

### **7.1 Pages**

#### **A. Home / Watchlist (**

#### **/**

#### **)**

* Header: “GamePriceLens” and a short subtitle.

* Search bar:

  * User types game name.

  * Shows autocomplete list of results from /api/search.

  * Clicking a result adds it to the watchlist via POST /api/games.

* Watchlist table:

  * Columns:

    * Cover

    * Game title

    * Best current price

    * Best store

    * Discount percent

    * Last updated

  * Buttons:

    * “View details” link to /game/:id.

#### **B. Game Detail (**

#### **/game/:id**

#### **)**

* Top section:

  * Game title, image, and short description.

* Prices section:

  * Table of stores and current prices, including discount and links out to stores.

* Chart section:

  * Simple line chart of best price over time using /api/games/{id} history data.

* Optional badges:

  * “At historical low” if is\_historical\_low is true or current price equals ITAD low.

### **7.2 Basic UI Requirements**

* Clean, responsive layout.

* Simple color palette, readable typography.

* Loading and error states:

  * Spinners for API calls.

  * Friendly messages if something fails.

---

## **8\. Non Functional Requirements**

* **Rate limiting and politeness**

  * Respect CheapShark’s usage notes. They do not require an API key but expect proper linking back and not abusing the API. 

  * For scraping, throttle requests and avoid frequent re-scrapes.

* **Config management**

  * Store API URLs and any keys (for ITAD if needed) in environment variables.

* **Logging**

  * Log failed API calls and scrape attempts.

* **Testing**

  * Unit tests for:

    * parsing of API responses into your models

    * the Steam metadata scraper

---

## **9\. Stretch Features (Future Work)**

* User accounts so different users can keep their own watchlists.

* Email notification when a game drops below a target price.

* Filters on the frontend:

  * By store

  * By discount percent

  * By price range

* Support for regional currencies.

* Additional metadata scraping (Metacritic score, tags, genres).

