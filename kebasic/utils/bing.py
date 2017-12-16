import html
import json
import logging

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from utils.logger import initialize_logger
from utils.taxonomy import read_taxonomy

unwanted_elements = ["effective_query", "requested_by", "requested_at", "scrape_method", "search_engine_name", "status"]

unwanted_domains = ['bing', 'google', 'yahoo', 'facebook', 'scribd', 'amazon', 'ebay']


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
    if cleaned_query in taxonomy:
        return taxonomy[cleaned_query][1], taxonomy[cleaned_query][0], cleaned_query
    return None, cleaned_query


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
        filtered_query = pop_elements(query_result)
        filtered_query['query'] = filtered_query['query']
        filtered_query['results'] = filter_results(filtered_query['results'])
        filtered_query['num_results'] = str(len(filtered_query['results']))
        category_id, category, clened_query = get_category(filtered_query['query'], taxonomy)
        filtered_query['category_id'] = category_id
        filtered_query['category'] = category
        filtered_query['query_cleaned'] = clened_query

        i += 1

        if not len(filtered_query['results']):
            continue

        filtered_result.append(filtered_query)

        percent = i / size * 100
        logging.info(percent)

    with open(out, "wt", encoding="utf8") as outf:
        json.dump(filtered_result, outf, indent=4, sort_keys=True, ensure_ascii=False)


if __name__ == '__main__':
    initialize_logger("./")
    path = "C:/Users/sasce/Desktop/query_results loc.json"
    out = "C:/Users/sasce/Desktop/query_results loc_filtered.json"
    taxonomy_path = "C:\\Users\\sasce\\PycharmProjects\\KeBaSiC\\resources\\ES\\taxonomy\\taxonomy.csv"
    taxonomy = read_taxonomy(taxonomy_path)
    bing_cleaner(path, out, taxonomy)
