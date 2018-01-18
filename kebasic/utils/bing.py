import html
import json
import logging

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from utils.logger import initialize_logger
from utils.taxonomy import read_reverse_taxonomy

unwanted_elements = ["effective_query", "requested_by", "requested_at", "scrape_method",
                     "search_engine_name", "status", "id"]

unwanted_domains = ['bing', 'google', 'yahoo', 'facebook', 'scribd', 'amazon', 'ebay']

unwanted_extensions = ['.pdf', '.ppt', '.xml', '.doc', '.epub']


def pop_elements(query_result):
    for element in unwanted_elements:
        query_result.pop(element)

    return query_result


def detect_lang(text):
    text = html.unescape(text)
    try:
        lang = detect(text)
    except LangDetectException as e:
        lang = ""
    return lang


def clean_query(query):
    for keyword in ["domain:es.wikipedia.com", "loc:ES", "-ext:pdf", "language:es", "inbody:", "intitle:"]:
        query = query.replace(keyword, "")

    return query.strip()


def get_category(query, taxonomy):
    cleaned_query = clean_query(query)
    if not cleaned_query:
        return False, False
    if cleaned_query in taxonomy:
        return cleaned_query, taxonomy[cleaned_query]

    raise Exception


def filter_results(results):
    cleaned = []
    for result in results:
        if any([x in result['domain'] for x in unwanted_domains]):
            continue

        if result['link_type'] == "ads_main":
            continue

        result.pop('link_type')
        result['language'] = detect_lang(result['snippet'])
        cleaned.append(result)

    return cleaned


def bing_cleaner(path, out, taxonomy):
    with open(path, "rt", encoding="utf-8") as inf:
        file = json.load(inf)

    filtered_result = []
    size = len(file)
    i = 0
    for query_result in file:
        i += 1
        filtered_query = pop_elements(query_result).replace("\"", "").strip()
        filtered_query['results'] = filter_results(filtered_query['results'])
        filtered_query['num_results'] = str(len(filtered_query['results']))
        cleaned_query, category = get_category(filtered_query['query'], taxonomy)
        if not cleaned_query:
            continue
        filtered_query.update(category)
        filtered_query['query_cleaned'] = cleaned_query

        if not len(filtered_query['results']):
            continue

        filtered_result.append(filtered_query)

        percent = i / size * 100
        logging.info(percent)

    with open(out, "wt", encoding="utf8") as outf:
        json.dump(filtered_result, outf, indent=4, sort_keys=True, ensure_ascii=False)


def bing2json(path, out, taxonomy):
    with open(path, "rt", encoding="utf-8") as inf, open(out, "wt", encoding="utf8") as outf:
        file = json.load(inf)

        for query in file:
            cleaned_query = query['query'].replace("\"", "").strip()
            category = taxonomy[cleaned_query]
            results = query['results']
            for result in results:
                url = result['link']
                webpage = {'url': url}
                webpage.update(category)
                json_page = json.dumps(webpage, ensure_ascii=False)
                outf.write(json_page + "\n")


if __name__ == '__main__':
    initialize_logger("./")
    path = "../../output/scraper/GoogleScraper_bing_quoted_query.json"
    out = "../../output/scraper/GoogleScraper_bing_quoted_query_categorized.json"
    taxonomy_path = "../../resources/ES/taxonomy/taxonomy.csv"
    taxonomy = read_reverse_taxonomy(taxonomy_path)
    bing2json(path, out, taxonomy)
