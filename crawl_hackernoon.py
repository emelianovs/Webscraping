import requests
import re
from bs4 import BeautifulSoup
from typing import Generator


# TODO saving to database


LINK = 'https://hackernoon.com'


def get_links(link: str) -> Generator:
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")

    articles = soup.select('h2 a')

    for article in articles:
        yield article['href']


def create_subpage_links(article_links: Generator) -> Generator:
    for link in article_links:
        yield LINK + link

# TODO set proper exceptions


def get_single_article_text(article_link: str) -> dict:
    page = requests.get(article_link)
    soup = BeautifulSoup(page.content, "html.parser")

    full_text = str(soup.select('script', type='application/ld+json'))

    title_pattern = r'(?<=\"Article\",\"name\":\")[\w+\s\D]+(?=\",\"headline\":)'
    author_pattern = r'(?<=\"Person\",\"name\":\")[\w+\s\D]+(?=\"},\"datePublished\")'
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    article_pattern = r'(?<=\"articleBody\":\")[\w+\s\D]+(?=\"}</script>)'

    return {
        'Title': search_pattern(title_pattern, full_text),
        'Author': search_pattern(author_pattern, full_text),
        'Date published': search_pattern(date_pattern, full_text),
        'Body': clear_text(search_pattern(article_pattern, full_text))
    }


def search_pattern(pattern: str, soup_text: str) -> str:
    result = re.search(pattern, soup_text)
    if result is not None:
        return result.group(0)
    else:
        return 'Could not scrape'


def get_article_content(articles_list: Generator) -> Generator:
    for article_link in list(articles_list):
        yield get_single_article_text(article_link)


def clear_text(text: str) -> str:
    return text.replace('&apos;', "'").replace(r'\n', ' ').replace(r'\\', ' ').replace('**', '').replace('__', '')


if __name__ == '__main__':
    links_list = get_links(LINK)
    subpages = create_subpage_links(links_list)
    print(list(get_article_content(subpages)))
