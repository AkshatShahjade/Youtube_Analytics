# Youtube_Analytics

## Project Overview

This project is a Python-based data analytics tool designed to reverse-engineer the success factors of YouTube videos within specific niches. Its a toolkit for my personal use to be able to research the existing youtube landscape, get a rough idea of what works and what doesn't and to be able to devise strategies to better optimize my own video titles and thumbnails - and sometimes even things like content length and topics.

The system automates the collection of video metadata, performs natural language processing (NLP) on titles, and applies computer vision techniques to thumbnails to derive actionable insights for content strategy optimization.


## Key Features

* **Automated Data Extraction:** Scrapes video metadata (views, likes, duration, thumbnail URLs) using the YouTube Data API v3.
* **Custom Performance Metric:** Calculates a View-to-Subscriber (V/S) ratio to normalize performance across different channel sizes, filtering out "noise" from large channels.
* **Performance Tiering:** Automatically classifies videos into three distinct categories:
* * Viral: V/S Ratio > 2.0 (Outperformed channel size by 200%)
* * Average: V/S Ratio between 0.1 and 2.0
* * Flop: V/S Ratio < 0.1
Comparative Keyword Mining (N-Grams):



* **Sentiment Analysis:** Utilizes VADER (Valence Aware Dictionary and sEntiment Reasoner) to correlate title sentiment intensity with viral success.
* **Comparative Keyword Mining:** Extracts n-grams (unigrams and bigrams) to identify vocabulary specific to viral videos while excluding generic search terms and common stopwords.
* * Viral Keywords: Identifies the most frequent unigrams and bigrams within the "Viral" tier to pinpoint successful hooks.
* * Unique Flop Keywords: Generates a list of keywords found in underperforming videos but excludes any terms also present in the viral list. This subtraction logic eliminates generic niche terms (e.g., "tutorial," "guide") to isolate specific vocabulary associated with failure.
* **Thumbnail Analytics:**
* * **Dominant Color Extraction:** Uses K-Means clustering to identify high-performing color palettes.



## Technical Architecture

### 1. Data Collection (Scraper)

A standalone Python script (`youtube_scraper.py`) fetches data based on a search query. It handles pagination, retrieves channel statistics for ratio calculations, and filters content by type (Shorts vs. Long-form). The output is a structured Excel dataset.

### 2. Analytical Engine (Analysis)

A Jupyter/Colab notebook processes the raw dataset to generate insights:

* **NLP Pipeline:** Tokenization, stopword removal, and sentiment scoring using NLTK.
* **Image Processing Pipeline:** Asynchronous fetching of thumbnail images, pixel analysis, and face detection using `cv2` and `scikit-learn`.
* **Statistical Analysis:** Correlation matrices and box plots to visualize relationships between variables (e.g., Title Length vs. Views).

## Installation and Requirements

The project requires Python 3.8+ and the following dependencies:

```bash
pip install pandas google-api-python-client isodate openpyxl nltk opencv-python-headless seaborn scikit-learn requests matplotlib

```

## Usage

**Step 1: Data Extraction**
Configure the `API_KEY` and `SEARCH_QUERY` variables in `youtube_scraper.py` and run the script:

```bash
python youtube_scraper.py

```

*Output: `youtube_data_[query].xlsx*`

**Step 2: Analysis**
Load the generated Excel file into the analysis environment (Jupyter Notebook or Google Colab). The analysis script will:

1. Compute Sentiment Scores and Thumbnail Metrics.
2. Generate visualization dashboards (Correlation Heatmaps, Sentiment Box Plots).
3. Output lists of "Viral" vs. "Unique Flop" keywords.

## Methodology: The Viral Ratio

Standard metrics like "Total Views" are biased toward established channels. This project evaluates content quality using the following formula:

`Viral Ratio = Video Views / Channel Subscribers`

* **Ratio > 1.0:** Indicates the video was recommended to non-subscribers (algorithmically successful).
* **Ratio < 0.1:** Indicates the video failed to engage even the core audience.

## Future Improvements

* Implementation of OCR (Optical Character Recognition) to analyze text overlay on thumbnails.
* Integration of a dashboard frontend (Streamlit) for real-time analysis.
* Expansion of the dataset to support multi-query comparative analysis.
