<p align="center">
  <a href="" rel="noopener">
 <img src="images/digisearch.png" alt="Project logo"></a>
</p>


**Digisearch** is a Python CLI pipeline for discovering [Digikala](https://www.digikala.com/) categories and crawling product data into structured local files.

---

## ✨ Features

* **Category filtering** – include or exclude categories by keyword.
* **Product crawling** – crawl product data, reviews, and Q&As from Digikala.
* **Data processing** – build canonical product records and search documents.
* **Semantic search** – BGE-M3 embeddings for natural-language product retrieval.
* **Resumable crawling** – continue from the last saved checkpoint.
* **Live monitoring** – real-time crawling progress with `rich`.
* **CLI interface** – run ingestion, processing, and search through `digisearch`.

---

## 📦 Requirements

- Python 3.9+
- Internet connection (to access Digikala APIs)
- Disk space for the crawled data (expect several GB for large categories)

Dependencies are listed in `pyproject.toml` and `requirements.txt` – they will be installed automatically when you install the package.

---

## 🚀 Installation

### Option 1 – Install from source (recommended)

#### clone over HTTPS

```bash
git clone https://github.com/artahaam/digisearch.git
cd digisearch
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install .
```
or

#### clone over SSH
```bash
git clone git@github.com:artahaam/digisearch.git
cd digisearch
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install .
```

<!-- then run:
```bash
digisearch --filters "men,clothes" --ignore "gold,silver" --output "men.csv"
``` -->

### Option 2 – Manual (without installation)

#### clone over HTTPS
```bash
git clone https://github.com/artahaam/digisearch.git
cd digisearch
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
or 
#### clone over SSH

```bash
git clone git@github.com:artahaam/digisearch.git
cd digisearch
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
<!-- then run
```bash
python run_pipeline.py --filters "men,clothes" --ignore "gold,silver" --output "men.csv""
``` -->

> **⚠️ Important:** Do **not** run the scripts directly from a terminal outside the project root, and do **not** create the virtual environment elsewhere.
> The `paths.py` module locates the project root by walking up from its own location until it finds `pyproject.toml`. If you run scripts from the wrong
> directory, this lookup fails and **raises a `RuntimeError`**.

#### ❗Why this matters

`find_project_root()` searches **parent directories** starting from `__file__` until it finds `pyproject.toml`. If the venv or the working directory is placed outside the project, that search fails and the script crashes before doing anything.

#### Quick checklist

| Requirement | Must be? |
|-------------|----------|
| venv location | Inside project directory (`.venv`) |
| Install method | `pip install .` |
| Run from | Project root directory |

---
## 🛠 Usage

The DigiSearch CLI provides three main commands:

1. **Ingest** – discovers and filters Digikala categories, then crawls their products.
2. **Process** – processes the crawled products, builds canonical records and search documents, and generates BGE-M3 embeddings.
3. **Search** – performs semantic search over the generated product embeddings.

### 1. Ingest products

Use `ingest` to discover categories, filter them, and crawl the selected products.

```bash
digisearch ingest \
    --filters "men,clothes" \
    --ignore "gold,silver,jewelry,keyring,traditional,espadrilles,women,accessories,sets,bracelet,face,mask" \
    --output "men.csv"
```

#### Ingest arguments

| Argument    | Type   | Default          | Description                                                                                         |
| ----------- | ------ | ---------------- | --------------------------------------------------------------------------------------------------- |
| `--filters` | string | `""`             | Comma-separated keywords to **include**. Categories whose `code` contains any keyword are selected. |
| `--ignore`  | string | `""`             | Comma-separated keywords to **exclude**. Categories whose `code` contains any keyword are skipped.  |
| `--id` | string | `""` | Comma-separated category IDs to **select**. Only categories whose IDs match the provided values will be processed. |
| `--output`  | string | `categories.csv` | CSV file containing the filtered category list used by the crawler.                                  |

For example:

```bash
digisearch ingest --filters "men,clothes" --ignore "accessories" --output "men.csv"
```
or

```bash
digisearch ingest --id "6825,9457,9460,9470" --output "clothes.csv"
```


To crawl all categories without filtering:

```bash
digisearch ingest --output "all_categories.csv"
```

> **Note:** Filters are case-insensitive and match against the category `code` field.

---

### 2. Process products

After crawling the products, run the processing pipeline:

```bash
digisearch process
```

The `process` command runs the following stages in order:

```text
list_products.py
        ↓
canonicalize.py
        ↓
search_document.py
        ↓
embedding.py
```

These stages:

* Build `data/canonical/product_list.json`
* Generate canonical product records under `data/canonical/products/`
* Generate search documents under `data/search_documents/products/`
* Generate BGE-M3 embeddings under `data/embeddings/bge-m3/`

The `process` command does not require any additional arguments.

---

### 3. Search for products

Once the processing pipeline has generated the embeddings, use `search` to perform semantic product retrieval:

```bash
digisearch search "کلاه نارنجی که روش گلدوزی کاکتوس داره"
```

You can control the number of retrieved products with `--topk`:

```bash
digisearch search "کلاه نارنجی که روش گلدوزی کاکتوس داره" --topk 12
```

#### Search arguments

| Argument | Type    | Default      | Description                                       |
| -------- | ------- | ------------ | ------------------------------------------------- |
| `query`  | string  | **required** | Natural-language retrieval query.                 |
| `--topk` | integer | `10`         | Number of the most relevant products to retrieve. |

The query is a **positional argument**, so it is provided directly after `search`:

```bash
digisearch search "sport tshirt"
```
---

### Complete example

A complete workflow using the CLI is:

#### 1. Ingest

```bash
digisearch ingest \
    --filters "men,clothes" \
    --ignore "gold,silver,jewelry,keyring,traditional,espadrilles,women,accessories,sets,bracelet,face,mask" \
    --output "men.csv"
```

#### 2. Process

```bash
digisearch process
```

#### 3. Search

```bash
digisearch search "کلاه نارنجی که روش گلدوزی کاکتوس داره" --topk 12
```

> **Note:** Each stage may take from minutes to hours depending on the amount of data being processed. For testing, keep the target categories as small as possible.

> **Note**: All filters are case‑insensitive and match against the `code` field (e.g., `clothing-men`).  
> If neither `--filters` nor `--ignore` is given, **all** categories are crawled.

---

## 📂 Output structure

After a successful run, your project directory will contain:

```
digisearch/
├── data/
│   ├── raw/
│   │   └── category/
│   │       └── <category_id>/
│   │           ├── page/
│   │           │   └── page_1.json, page_2.json, ...
│   │           └── product/
│   │               └── <product_id>/
│   │                   ├── details.json
│   │                   ├── comments.json
│   │                   └── questions.json
│   │
│   ├── canonical/
│   │   ├── product_list.json        # index of all crawled products
│   │   └── products/
│   │       └── <product_id>.json    # structured product record
│   │
│   ├── search_documents/
│   │   └── products/
│   │       └── <product_id>.txt     # search-documents to generate embeddings
│   │
│   ├── embeddings/
│   │   └── bge-m3/
│   │       └── <product_id>.json    # BGE-M3 product embedding
│   │
│   ├── checkpoints/
│   │   └── checkpoint.csv           # crawler resume point
│   │
│   └── logs/
│       ├── crawler.log              # detailed crawler logs
│       ├── pipeline.log             # overall pipeline logs
│       └── process.log              # processing pipeline logs
├── <output>.csv                     # filtered category list (e.g., men.csv)
└── ...
```


- `data/raw/category/<category_id>/page` – raw API responses for each product‑listing pages per category.
- `data/raw/category/<category_id>/product/<product_id>` contains product details, comments and questions.
 . `details.json` – full product information.
 . `comments.json` – all user reviews for that product.
 . `questions.json` – all customer Q&A entries.
- `data/canonical/product_list.json` – index of all crawled products with their raw file paths and category.
- `data/canonical/products` – contains canonical products
- `data/search_documents/products/` – search documents created from canonical products used for embedding generation
- `data/embeddings/bge-m3` – generated embeddings with the BGE-M3 model
- `data/logs` – contains logs for each section


---

## 🎛 Live Dashboard for Crawling

While crawling, a **Rich** dashboard updates in real time:

<p align="center">
  <a href="" rel="noopener">
 <img src="images/screenshot.png" alt="screenshot"></a>
</p>



Press `Ctrl+C` at any time to interrupt the crawl – it will resume from the last checkpoint on the next run.

---

## 🔄 Resuming a Crawl

If the pipeline stops (due to interruption, network error, etc.), simply run the **same command** again.  
The crawler reads the checkpoint file and continues from the last saved category and page number.  
No data is duplicated; checkpoints are written after every page.

---

<!-- ## 🧪 Example

Fetch all categories containing `"clothes"` or `"men"`, but ignore those with `"gold"` or `"accessories"`, and name the output `my_categories.csv`:

```
digisearch --filters "clothes,men" --ignore "gold,accessories" --output "my_categories.csv"
```
To crawl **all** categories (no filtering):

```
digisearch --output "all_categories.csv"
```
--- -->

## docs

- [data_inspection.md](docs/data_inspection.md) – Explains what information about a product do we use.
- [details_sample.json](docs/details_sample.json) – Shows how a product details sample looks like.
- [comments_sample.json](docs/comments_sample.json) – Shows how a product comments sample looks like.
- [questions_sample.json](docs/questions_sample.json) – Shows how a product questions sample looks like.
- [canonical_sample.json](docs/canonical_sample.json) – Shows how a canonical product structure looks like.
- [search_document_sample.json](docs/search_document_sample.json) – Shows how a search document looks like.
- [embedding_sample.json](docs/embedding_sample.json) – Shows how a product embedding looks like.
  

### BGE Embeddings

- Product List is generated from the raw products stored in `data/raw/`
- Canonical prodcuts are generated from raw product records using `product_list.json` and saved as `data/canonical/products/`.
- Search documents are generated from canonical product records and saved as `data/canonical/products`.
- Embeddings are generated from search documents using the `BGE-M3` model and stored in the `data/embeddings/bge-m3` directory.
- Retrieval is done by finding the highest dot-product of the query-vector and the product embeddings.


<!-- ### Running manlually

If you want to run stages manually:

#### 1. Generate the filtered category list
```
python get_categories.py --filters "men" --output "men.csv"
```
####  2. Crawl the categories (uses the CSV as input)
```
python crawl.py --output "men.csv"
```
#### 3. Build the canonical dataset
```
python src/digisearch/processing/list_products.py           # scans raw data → data/canonical/product_list.json
python src/digisearch/processing/canonicalize.py            # builds structured records → data/canonical/products
```
#### 4. Generate search documents and embeddings
```
python src/digisearch/processing/search_documents.py        # builds search docs → data/search_documents
python src/digisearch/processing/embedding.py               # generates BGE embeddings
```
#### 5. Search and Retrieve products
```
python src/digisearch/processing/retrieval.py               # retrieve related products
```

--- -->
## Logging

- Pipeline logs (stage start/end, arguments) → `logs/pipeline.log`
- Detailed crawler logs (per‑page, per‑product) → `logs/crawler.log`
- Process logs (canonical, embeddings, retrieval) → `logs/process.log` 
---

## Roadmap

### Phase 1: Data Pipeline (✅)
- [x] 1.1 Category discovery and filtering.
- [x] 1.2 Product Details, Reviews and Q&As extraction.
- [x] 1.3 Resumable checkpoints.

### Phase 2: Data Cleaning and Dataset Preparation
- [x] 2.1 Data inspection
- [x] 2.2 Canonical dataset
- [x] 2.3 Data cleaning and normalization
- [x] 2.4 Search document construction
- [x] 2.5 Embedding generation
- [x] 2.6 Vector retrieval
- [ ] 2.7 Vector Database

<!-- ### Phase 3: Semantic Search (🚧)
- [ ] 3.1 Semantic product search API
- [ ] 3.2 Vector search integration
- [ ] 3.3 Search UI/CLI -->

## 📄 License

MIT – see [LICENSE](LICENSE) file.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


---

## 📬 Contact

**Author**: artahaam  
**Email**: alireza.thm03@gmail.com  
**GitHub**: [@artaham](https://github.com/artahaam)
