# Embeddings — Complete Theory

---

## 1. What is an Embedding?

An **embedding** is a learned, dense, low-dimensional representation of high-dimensional discrete or continuous data (words, sentences, images, users, products, graphs, etc.) in a continuous vector space (**ℝⁿ**).

The core idea:
> **Semantically similar items should be geometrically close in embedding space.**

Instead of one-hot encoding (sparse, no semantic meaning), embeddings capture **relationships**, **context**, and **meaning** as learnable real-valued vectors.

```
"king"  → [0.25, 0.71, -0.33, ...]   (n-dimensional vector)
"queen" → [0.24, 0.70, -0.31, ...]   (close in space)
"apple" → [-0.80, 0.10, 0.55, ...]   (far from "king"/"queen")
```

---

## 2. Why Embeddings?

| Problem with Raw Representations | Embeddings Fix This |
|---|---|
| One-hot vectors are sparse and huge | Dense, compact vectors |
| No notion of similarity | Geometry encodes similarity |
| Curse of dimensionality | Low-dimension representation |
| No transfer of knowledge | Pre-trained embeddings transfer knowledge |
| Categorical data can't be used in NNs directly | Continuous vectors work with any neural network |

---

## 3. Mathematical Foundation

### 3.1 Vector Space Model
An embedding is a function:

```
f : X → ℝᵈ
```

where `X` is an input space (vocabulary, image pixels, graph nodes) and `d` is the embedding dimension (e.g., 128, 256, 768).

### 3.2 Properties of a Good Embedding Space
- **Closeness = Similarity**: `sim(f(x₁), f(x₂))` is high when `x₁` and `x₂` are semantically similar.
- **Linearity / Compositionality**: Arithmetic in embedding space is meaningful.
  ```
  f("king") - f("man") + f("woman") ≈ f("queen")
  ```
- **Smoothness**: Small perturbations in input → small change in embedding.
- **Isometry (ideal)**: Distances in embedding space reflect true semantic distances.

### 3.3 Dimensionality
- Too low → **underfitting**, can't capture all relationships.
- Too high → **overfitting**, sparse, computationally expensive.
- Typical values: 50–300 (words), 768–4096 (LLMs), 128–512 (items/users).

---

## 4. Types of Embeddings

### 4.1 Word Embeddings

#### Word2Vec (2013, Mikolov et al.)
Two architectures:

**a) CBOW (Continuous Bag of Words)**
- Predicts the **center word** from surrounding context words.
- Input: context window words → Output: center word.
- Faster, works better for frequent words.

**b) Skip-Gram**
- Predicts the **surrounding context words** from a center word.
- Input: center word → Output: context words.
- Better for rare words and larger datasets.

**Training Objective (Skip-Gram):**
```
Maximize:  Σ Σ log P(wₒ | wᵢ)
            i  o∈context(i)
```

**Negative Sampling:** Instead of softmax over entire vocabulary, sample a few "negative" (incorrect) words, making training efficient.

---

#### GloVe (Global Vectors, 2014, Pennington et al.)
- Combines **global co-occurrence statistics** with local context.
- Builds a **co-occurrence matrix** `X` where `Xᵢⱼ` = how often word `i` appears near word `j`.
- **Objective:** Learn vectors `wᵢ, w̃ⱼ` such that:

```
wᵢᵀ · w̃ⱼ + bᵢ + b̃ⱼ ≈ log(Xᵢⱼ)
```

- Weighted least-squares loss:
```
J = Σᵢ,ⱼ f(Xᵢⱼ) (wᵢᵀw̃ⱼ + bᵢ + b̃ⱼ - log Xᵢⱼ)²
```

where `f(x)` is a weighting function that down-weights very frequent pairs.

---

#### FastText (2016, Facebook AI)
- Extends Word2Vec by representing words as **bags of character n-grams**.
- Word "apple" → {`<ap`, `app`, `ppl`, `ple`, `le>`, `<apple>`}
- Can generate embeddings for **Out-Of-Vocabulary (OOV)** words.
- Better for morphologically rich languages.

---

#### ELMo (Embeddings from Language Models, 2018)
- **Contextual embeddings**: the same word has **different** embeddings depending on context.
- Uses a **bi-directional LSTM** trained as a language model.
- "bank" in "river bank" vs "bank account" → different vectors.

---

### 4.2 Sentence / Paragraph Embeddings

#### Doc2Vec (Le & Mikolov, 2014)
- Extends Word2Vec; adds a **paragraph/document ID** vector that is also trained.
- Two variants: **PV-DM** (Distributed Memory) and **PV-DBOW** (Distributed Bag of Words).

#### Sentence-BERT (SBERT, 2019)
- Fine-tunes BERT with **siamese / triplet network** structure.
- Produces fixed-size sentence embeddings suitable for semantic similarity and retrieval.
- Loss functions: Softmax classification loss, cosine similarity loss, triplet loss.

#### Universal Sentence Encoder (USE, Google 2018)
- Two variants: **Transformer-based** (higher accuracy) and **DAN-based** (faster).
- Multi-task trained on various NLP tasks for general-purpose sentence embeddings.

---

### 4.3 Contextual / Transformer Embeddings

#### BERT (Bidirectional Encoder Representations from Transformers, 2018)
- Pre-trained on **Masked Language Modeling (MLM)** and **Next Sentence Prediction (NSP)**.
- Produces **token-level** contextual embeddings.
- `[CLS]` token embedding often used as a sentence-level representation.

#### GPT Family
- **Autoregressive** language model, left-to-right context.
- GPT-2/3/4 produce contextual token embeddings.
- Sentence embedding typically taken from the last token or averaged.

#### OpenAI text-embedding-ada-002 / text-embedding-3-*
- Commercial dense embeddings optimized for semantic search, retrieval, and clustering.
- 1536-dimensional (ada-002) or 3072-dimensional (text-embedding-3-large).

---

### 4.4 Image Embeddings

| Model | Technique |
|---|---|
| CNN Features | Extract activations from penultimate FC layer |
| CLIP (OpenAI) | Contrastive image-text training, shared embedding space |
| ViT (Vision Transformer) | Patch-based transformer for image embeddings |
| SimCLR / MoCo | Self-supervised contrastive learning |
| DINO | Self-distillation with no labels |

---

### 4.5 Graph Embeddings

Embeds **nodes, edges, or entire graphs** into vector space.

| Method | Approach |
|---|---|
| DeepWalk | Random walks + Word2Vec |
| Node2Vec | Biased random walks (BFS/DFS balance) |
| LINE | Preserves 1st-order and 2nd-order proximity |
| GraphSAGE | Inductive; aggregates neighbor features |
| GCN (Graph Conv Network) | Spectral convolutions on graph |
| GAT (Graph Attention Net) | Attention-weighted neighbor aggregation |

---

### 4.6 Multimodal Embeddings and Vector Matching

Multimodal embeddings map data from different modalities (e.g., text, image, audio, video) into a **single, shared continuous vector space**. The core idea is that a picture of a dog, the text "a picture of a dog", and the audio of a dog barking should all have nearly identical embedding vectors.

**Key Models:**
- **CLIP (OpenAI)**: Learns a shared space for image and text.
- **ImageBind (Meta)**: Aligns 6 different modalities (image, text, audio, depth, thermal, IMU) into one space.
- **Flamingo**: A vision-language model with cross-modal embeddings used heavily for reasoning.

**How Vector Matching Works in Multimodal Systems:**
1. **Shared Embedding Space**: Models utilize a contrastive learning objective (like InfoNCE). A text encoder (e.g., Transformer) and an image encoder (e.g., ViT) are trained jointly.
2. **Contrastive Alignment**: In a batch of `N` (image, text) pairs, the model maximizes the cosine similarity for the `N` correct pairs and minimizes it for the `N*(N-1)` incorrect (negative) pairs. Both modalities are pushed into the exact same latent space.
3. **Cross-Modal Retrieval**: 
   - *Text-to-Image*: Encode a text query into a vector space. Search a vector database populated entirely with image embeddings using cosine similarity. The closest image vectors are retrieved as they match the text semantics.
   - *Image-to-Text*: Encode an image into the space to retrieve matching text documents.
4. **Late Fusion vs Early Fusion**: 
   - *Late Fusion / Dual Encoder* (e.g., CLIP): Modalities are encoded separately, and only their final vectors are compared via dot product or cosine similarity. This is highly efficient and required for fast vector database search.
   - *Early Fusion* (e.g., Flamingo): Modalities are combined early and processed by a single transformer. Much better for complex reasoning but too slow for large-scale retrieval.

---

### 4.7 Entity / Item / User Embeddings (Recommender Systems)

- **Matrix Factorization**: Decomposes user-item rating matrix into user and item embedding matrices.
- **Neural Collaborative Filtering**: Uses neural nets to learn user/item embeddings.
- **Session-based embeddings**: Sequences of clicks/actions → GRU/Transformer embeddings.

---

## 5. Training Methodologies

### 5.1 Supervised Embedding Learning
- Train on labeled data; backpropagate loss to update embedding weights.
- Example: classification task trains class-discriminative embeddings.

### 5.2 Self-Supervised / Unsupervised
- No labels needed; derive supervision signal from data itself.
- **MLM** (BERT), **Next-token prediction** (GPT), **co-occurrence** (Word2Vec, GloVe).

### 5.3 Contrastive Learning
Key idea: pull **similar pairs closer**, push **dissimilar pairs apart** in embedding space.

**Contrastive Loss (Siamese Networks):**
```
L = (1 - y) · ½ · D² + y · ½ · max(0, margin - D)²
```
where `y=0` for similar, `y=1` for dissimilar, `D` is distance.

**Triplet Loss:**
```
L = max(0, d(anchor, positive) - d(anchor, negative) + margin)
```
- **Anchor**: reference sample
- **Positive**: sample similar to anchor
- **Negative**: sample dissimilar to anchor

**InfoNCE Loss (used in SimCLR, CLIP):**
```
L = -log [ exp(sim(zᵢ, zⱼ) / τ) / Σₖ exp(sim(zᵢ, zₖ) / τ) ]
```
where `τ` = temperature parameter controlling distribution sharpness.

### 5.4 Knowledge Distillation for Embeddings
- Train a smaller **student** model to mimic embeddings of a larger **teacher** model.
- Used in sentence transformers for efficient deployment.

### 5.5 Fine-tuning Pre-trained Embeddings
- Start from a pre-trained embedding model (BERT, etc.).
- Fine-tune on domain-specific data or downstream task.
- **Adapters / LoRA**: parameter-efficient fine-tuning without updating all weights.

---

## 6. Similarity and Distance Metrics

Once embedded, similarity is measured using:

### 6.1 Cosine Similarity
```
cos(A, B) = (A · B) / (‖A‖ · ‖B‖)
```
- Range: [-1, 1]. 1 = identical direction, 0 = orthogonal, -1 = opposite.
- **Most common** for NLP embeddings; independent of vector magnitude.

### 6.2 Euclidean Distance (L2)
```
d(A, B) = √(Σ(Aᵢ - Bᵢ)²)
```
- Sensitive to magnitude; use when magnitude carries meaning.

### 6.3 Dot Product
```
sim(A, B) = A · B = Σ Aᵢ · Bᵢ
```
- Proportional to cosine similarity when vectors are normalized.
- Used in attention mechanisms and ANN search engines.

### 6.4 Manhattan Distance (L1)
```
d(A, B) = Σ |Aᵢ - Bᵢ|
```

### 6.5 Inner Product (Bilinear)
```
sim(A, B) = Aᵀ · W · B
```
- `W` is a learned weight matrix; used in knowledge graph embeddings.

---

## 7. Dimensionality Reduction of Embeddings

High-dim embeddings are often projected down for **visualization** or **efficiency**:

| Method | Description |
|---|---|
| **PCA** | Linear projection; preserves maximum variance |
| **t-SNE** | Non-linear; preserves local neighborhood structure (viz only) |
| **UMAP** | Non-linear; faster than t-SNE, preserves global structure better |
| **Autoencoder** | Encoder-decoder; learns compressed latent space |
| **Matryoshka Representation Learning (MRL)** | Embeddings that work well at multiple truncated dimensions |

---

## 8. Vector Databases and Approximate Nearest Neighbor (ANN) Search

A **vector database** stores high-dimensional embeddings and supports efficient similarity search. It is the backbone of semantic search, RAG, recommendations, and multimodal retrieval.

**Vector embeddings + Vector DB**: Embeddings are produced by embedding models; the vector database indexes and retrieves them. The DB doesn't create embeddings—it stores and searches them.

### 8.1 Exact Search
- Brute-force dot product / cosine over all vectors.
- `O(n·d)` per query; infeasible for millions of vectors.

### 8.2 ANN Algorithms

| Algorithm | Key Idea |
|---|---|
| **HNSW** (Hierarchical Navigable Small World) | Graph-based; navigates layers of proximity graphs |
| **IVF** (Inverted File Index) | Clusters vectors; searches only relevant clusters |
| **PQ** (Product Quantization) | Compresses vectors into codes; fast approximate distance |
| **LSH** (Locality Sensitive Hashing) | Hash similar vectors to same bucket |
| **ScaNN** (Google) | Anisotropic quantization for high recall |

### 8.3 Kinds of Vector Databases and Their Strengths

Vector databases can be broadly categorized into three types based on their architecture and origin.

#### 1. Native / Purpose-Built Vector Databases
These systems are built from the ground up specifically to store and retrieve vector embeddings at scale. They excel at performance, handling massive vector dimensions, and advanced ANN indexing.
- **Pinecone**: 
  - *Type*: Managed SaaS / Serverless.
  - *Strengths*: Purely cloud-native, zero infrastructure management. Offers built-in hybrid search (dense + sparse vectors). Excellent for teams wanting immediate production-ready semantic search without maintenance overhead.
- **Milvus**: 
  - *Type*: Open-source, Distributed.
  - *Strengths*: Highly scalable, handles billions of vectors. Cloud-native architecture separates storage and compute. Best for massive enterprise ML pipelines.
- **Qdrant**: 
  - *Type*: Open-source (Rust).
  - *Strengths*: Extremely fast and resource-efficient. Excels at **payload filtering** (filtering vector search by strict metadata conditions). Provides native vector quantization for saving memory.
- **ChromaDB**: 
  - *Type*: Open-source.
  - *Strengths*: Incredibly simple Python-first API, runs embedded natively. Best for rapid prototyping, local LLM/RAG app development, and small-to-medium deployments.
- **Weaviate**: 
  - *Type*: Open-source.
  - *Strengths*: Designed to integrate deeply with AI workflows, acting as an "AI-native" database. Uses GraphQL and has built-in embedding modules (can automatically vectorize text/images on insertion). 

#### 2. Vector-Capable SQL / Relational Databases
Traditional relational databases that have added vector search extensions.
- **pgvector (PostgreSQL)**: 
  - *Strengths*: Allows you to keep your vectors right next to your relational application data. Supports full ACID compliance, standard SQL querying, and performing JOINs between exact relational matches and similarity search. Perfect for apps already heavily relying on Postgres.
- **SingleStore / AlloyDB**: 
  - *Strengths*: Highly optimized distributed SQL systems that added vector capabilities. Good for real-time analytics combined with vector search.

#### 3. Vector-Capable NoSQL & Search Engines
Existing NoSQL databases and traditional inverted-index search engines that retrofitted ANN capabilities.
- **Elasticsearch (kNN) / OpenSearch**: 
  - *Strengths*: The industry standard for traditional BM25 keyword search. Integrating vectors allows for powerful **Hybrid Search** (combining lexical and semantic search) in a single system. Best for systems migrating from keyword search to semantic search.
- **Redis Stack**: 
  - *Strengths*: Sub-millisecond latency. Operates fully in-memory. Combines traditional extremely fast caching capabilities with vector search. Best for real-time applications and low-latency retrieval.
- **FAISS**: 
  - *Strengths*: Library (not a full DB) that provides extremely fast in-memory indexing and supports GPU acceleration. Best for offline batch search, research, and in-process retrieval.
- **Vespa**: 
  - *Strengths*: Peerless for large-scale production ranking. Allows defining complex machine learning models directly in the database to re-rank vector search results dynamically.

### 8.4 Choosing a Vector Database

| Need | Preferred Option |
|---|---|
| Zero ops, fast setup | Pinecone |
| Multimodal (text + image in one index) | Weaviate, Pinecone |
| Maximum performance, self-hosted | Qdrant |
| Billions of vectors, distributed | Milvus |
| Prototyping / local dev | ChromaDB |
| Vectors + relational data in one DB | pgvector |
| Offline / batch / research | FAISS |
| Lowest latency with existing Redis | Redis Stack |

---

## 9. Applications of Embeddings

### 9.1 Semantic Search / Information Retrieval
- Encode query and documents as vectors.
- Retrieve top-k nearest vectors using ANN.
- **Bi-encoder**: query and document encoded independently (fast).
- **Cross-encoder**: query+document together (slower but more accurate).

### 9.2 Retrieval-Augmented Generation (RAG)
1. Embed knowledge base documents → store in vector DB.
2. Embed user query → retrieve relevant chunks.
3. Feed retrieved context to LLM for grounded generation.

### 9.3 Recommendation Systems
- Embed users and items in same vector space.
- Recommend items with high similarity to user embedding.
- **Two-Tower Model**: separate encoders for user and item, trained with contrastive loss.

### 9.4 Anomaly Detection
- Embed normal data; anomalies are far from cluster centers.

### 9.5 Clustering
- K-Means, DBSCAN, hierarchical clustering on embedding vectors.

### 9.6 Classification
- Use embedding as feature input to classifier (SVM, logistic regression, MLP).

### 9.7 Deduplication
- Find near-duplicate records by embedding similarity.

### 9.8 Machine Translation
- Cross-lingual embeddings (mBERT, LaBSE) align multiple languages in one space.

### 9.9 Knowledge Graph Embeddings
- Embed entities and relations; predict missing links.
- Models: **TransE**, **RotatE**, **ComplEx**, **DistMult**.

---

## 10. Knowledge Graphs and Their Embeddings

### 10.1 What is a Knowledge Graph?
A **Knowledge Graph (KG)** is a structured representation of facts, consisting of entities (nodes) and the relationships between them (edges). Data is typically stored as **triplets**: `(Head, Relation, Tail)` or `(Subject, Predicate, Object)`.
- *Example*: `(Albert Einstein, born_in, Ulm)`, `(Ulm, located_in, Germany)`.

### 10.2 Why do we need Knowledge Graphs?
While LLMs and general vector embeddings capture *implicit*, statistical semantics, Knowledge Graphs capture *explicit*, deterministic, and structured facts.
- **Precision & Accuracy**: KGs do not hallucinate; they represent exact relationships.
- **Explainable Reasoning**: Querying a KG provides a traceable path (e.g., A -> B -> C), making inferences entirely interpretable.
- **Complex Multi-hop Queries**: KGs excel at questions that require traversing multiple relationships, which is often difficult for pure semantic vector search ("Find all directors who have worked with an actor born in London").

### 10.3 Uses of Knowledge Graphs
- **Graph RAG (Retrieval-Augmented Generation)**: Combining KGs with vector databases to provide LLMs with both exact factual data (Graph) and fuzzy semantic context (Vectors).
- **Search Engines**: Google's "Knowledge Panel" (the info box on the right of search results) is powered by a massive KG.
- **Fraud Detection**: Quickly identifying hidden patterns, rings, or circular relationships between accounts that traditional relational joins would struggle with.
- **Recommendation Systems**: Recommending items by traversing paths from a user to a product via shared properties, friends, or categories.

### 10.4 Knowledge Graph Embedding Models
To use KGs in machine learning (like predicting missing links), we learn low-dimensional vectors for both entities and relations.

#### TransE
- Relation `r` modeled as translation: `h + r ≈ t`
- `h` = head entity, `t` = tail entity, `r` = relation.
- Score: `-‖h + r - t‖`

#### RotatE
- Relation modeled as rotation in complex space.
- Can model symmetry, antisymmetry, inversion, composition.

#### ComplEx
- Uses complex-valued embeddings.
- Score: `Re(⟨h, r, t̄⟩)`

---

## 11. Embedding Evaluation

### 11.1 Intrinsic Evaluation
- **Word similarity tasks**: Compare cosine similarity to human judgments (e.g., SimLex-999, WordSim-353).
- **Analogy tasks**: `king - man + woman = ?` (should = queen).
- **Clustering quality**: Silhouette score, Davies-Bouldin index.

### 11.2 Extrinsic Evaluation
- Evaluate downstream task performance (sentiment, NER, QA, IR) when using the embeddings.
- Better real-world measure of embedding quality.

### 11.3 Benchmarks
| Benchmark | Task |
|---|---|
| MTEB | Massive text embedding benchmark (56 tasks) |
| STS Benchmark | Sentence semantic similarity |
| BEIR | Information retrieval |
| GLUE / SuperGLUE | NLU tasks |

---

## 12. Advanced Concepts

### 12.1 Matryoshka Representation Learning (MRL)
- Train embeddings that are meaningful at **multiple truncated dimensions**.
- `d=64`, `d=128`, `d=256`, ... all work well from the same model.
- Enables flexible latency/accuracy trade-offs.

### 12.2 Binary / Quantized Embeddings
- Convert float32 vectors to **1-bit binary** codes.
- Drastically reduces memory and enables bitwise XOR similarity.
- Hamming distance replaces cosine for ANN search.

### 12.3 Sparse Embeddings (SPLADE)
- Combine dense semantic understanding with sparse lexical matching.
- Output is a sparse high-dimensional vector (like TF-IDF but learned).
- Better for keyword-sensitive queries.

### 12.4 ColBERT (Late Interaction)
- Keep **all token embeddings** (not just CLS).
- MaxSim scoring: for each query token, find max similarity across all document tokens.
- Better recall, higher storage cost.

### 12.5 Embedding Alignment
- **Cross-lingual alignment**: Map separately trained monolingual embeddings into shared space (e.g., MUSE with adversarial training).
- **Domain adaptation**: Align embeddings from different domains using Procrustes analysis or fine-tuning.

### 12.6 Positional Embeddings (in Transformers)
Used to inject sequence order into attention-based models.

| Type | Description |
|---|---|
| **Sinusoidal** (original BERT) | Fixed; `sin/cos` at different frequencies |
| **Learned** | Trainable position vectors (GPT-2) |
| **Relative (RPE)** | Encodes relative distance between tokens |
| **RoPE** (Rotary Position Embedding) | Rotates query/key vectors; used in LLaMA, GPT-NeoX |
| **ALiBi** | Adds linear bias to attention scores |

---

## 13. Embedding in System Design

### Architecture Pattern: Embedding Service

```
                   ┌────────────────────────┐
User Query ──────► │   Embedding Service    │ ◄──── Batch Indexing Pipeline
                   │  (BERT / OpenAI API)   │
                   └──────────┬─────────────┘
                              │ Query Vector
                              ▼
                   ┌────────────────────────┐
                   │    Vector Database      │
                   │  (Pinecone / Qdrant)   │
                   └──────────┬─────────────┘
                              │ Top-K Results
                              ▼
                   ┌────────────────────────┐
                   │   Re-ranker (optional) │
                   │  (Cross-Encoder, LLM)  │
                   └──────────┬─────────────┘
                              │ Final Results
                              ▼
                         Response to User
```

### Key Design Considerations
- **Consistency**: Re-embed when the model is updated.
- **Latency**: Pre-compute and cache embeddings for known data.
- **Scalability**: Distribute ANN index (sharding by ID ranges or clusters).
- **Freshness**: Incremental embedding updates for new data.
- **Versioning**: Track model version with each stored vector.

---

## 14. Bias in Embeddings

- Word embeddings trained on biased corpora encode societal biases.
- Example: `doctor - man + woman ≈ nurse` (gender bias).
- **Debiasing techniques**:
  - **Hard Debiasing** (Bolukbasi et al.): project out the bias direction.
  - **Counterfactual Data Augmentation**: train on balanced datasets.
  - **Adversarial Debiasing**: add discriminator to penalize bias during training.

---

## 15. Summary Table — Embedding Models

| Model | Year | Type | Key Feature |
|---|---|---|---|
| Word2Vec | 2013 | Word | Skip-gram / CBOW, negative sampling |
| GloVe | 2014 | Word | Global co-occurrence statistics |
| FastText | 2016 | Word | Subword (character n-gram) aware |
| ELMo | 2018 | Word (contextual) | BiLSTM language model |
| BERT | 2018 | Token (contextual) | Bidirectional transformer, MLM |
| GPT | 2018 | Token (contextual) | Autoregressive transformer |
| Sentence-BERT | 2019 | Sentence | Siamese BERT, semantic similarity |
| CLIP | 2021 | Multimodal | Contrastive image-text alignment |
| text-embedding-ada-002 | 2022 | Sentence | OpenAI general-purpose |
| MRL | 2022 | Sentence | Matryoshka multi-granularity |
| text-embedding-3 | 2024 | Sentence | OpenAI, MRL-based, best quality |

---

*References: Mikolov et al. (2013), Pennington et al. (2014), Devlin et al. (2018), Radford et al. (2021), Reimers & Gurevych (2019), Kusupati et al. (2022)*
