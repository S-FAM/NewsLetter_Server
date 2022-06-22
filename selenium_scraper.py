from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
from NewsLetter_Server.news import News
from time import sleep


class NewsScraper:
    """
    뉴스 스크래핑 클래스입니다.
    """

    def __init__(self):
        self.__driver = webdriver.Chrome("./chromedriver")
        self.__categories = {
            "정치": "100",
            "경제": "101",
            "사회": "102",
            "생활|문화": "103",
            "세계": "104",
            "IT|과학": "105",
            # "연예": "106",
            # "스포츠": "107",
        }

    def __del__(self):
        self.close()

    def __open_url(self, url):
        """
        프로퍼티인 url 값을 가지고 url을 엽니다.
        """
        self.__driver.get(url)
        sleep(1)

    def __structuralization(self, news) -> News:
        """
        셀레니움으로 가지고 온 데이터를 가지고 News 객체를 만들어 반환합니다.
        """
        url = news.find_element_by_tag_name("a").get_attribute("href")
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15"
        }
        html = requests.get(url, headers=headers)
        soup = BeautifulSoup(html.text, "html.parser")
        publish_date = soup.find("span", {"class": "_ARTICLE_DATE_TIME"}).text
        try:
            return News(
                title=news.find_elements_by_tag_name("dt")[-1].text,
                description=news.find_element_by_class_name("lede").text,
                image=news.find_element_by_tag_name("img").get_attribute("src"),
                url=url,
                publish_date=publish_date,
            )
        except NoSuchElementException:  # 이미지 없는 단순 텍스트 뉴스인 경우
            return News(
                title=news.find_elements_by_tag_name("dt")[-1].text,
                description=news.find_element_by_class_name("lede").text,
                image=None,
                url=url,
                publish_date=publish_date,
            )

    def get_news(self, category: str, page: int) -> list:
        """
        카테고리와 페이지를 인자로 받아서 해당 카테고리의 해당 페이지의 뉴스를 리스트로 반환합니다.

        Parameter
        ---------
        category: str
            카테고리를 의미하는 문자열입니다.

        page: int
            페이지를 의미하는 정수입니다.


        Returns
        -------
        list
            해당 카테고리의 해당 페이지의 뉴스를 리스트로 반환합니다.
        
        """
        # 존재하는 카테고리가 아니라면 즉시리턴
        if category not in self.__categories:
            return

        #  뉴스 가져오기
        url = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={self.__categories[category]}#&date=%2000:00:00&page={page}"
        self.__open_url(url)

        # 원하는 뉴스 내용을 태그로 찾기
        news_body = self.__driver.find_element_by_class_name("section_body")
        news_list = []

        for news_struct in [
            news_body.find_element_by_class_name("type06_headline"),
            *news_body.find_elements_by_class_name("type06"),
        ]:
            news_list.extend(news_struct.find_elements_by_tag_name("li"))

        # 찾은 뉴스의 내용물을 구조화시키자
        news_list = list(map(lambda news: self.__structuralization(news), news_list))

        return news_list

    def save_news_to_csv(
        self, path: str, category: str, pages: tuple, verbose: bool = False
    ) -> bool:
        """
        뉴스를 가지고 csv로 저장합니다.

        Parameter
        ---------
        path: str
            csv 파일의 경로입니다.
        category: str
            카테고리를 의미하는 문자열입니다.
        pages: tuple
            시작 페이지와 끝 페이지를 의미하는 정수타입 튜플입니다.

        Returns
        -------
        bool
            저장 성공 여부를 반환합니다.
        """
        try:
            news_list = []
            # 카테고리와 페이지를 인자로 받아서 해당 카테고리의 해당 페이지의 뉴스를 리스트로 반환합니다.
            for page in range(pages[0], pages[1] + 1):
                if verbose:
                    print(f"{category} {page} saving...")
                news_list.extend(self.get_news(category, page))
                if verbose:
                    print(f"{category} {page} saved.")

            # csv로 저장하기
            with open(path, "w", encoding="utf-8") as f:
                if verbose:
                    print(f"{category} csv saving...")

                f.write("title|description|image|url|date\n")
                for news in news_list:
                    f.write(
                        f"{news.title}|{news.description}|{news.image}|{news.url}|{news.publish_date}\n"
                    )
                if verbose:
                    print(f"{category} csv saved.")
        except Exception as e:
            print(f"{category} csv saving failed.")
            print(f"{page=}")
            print(e)
            return False
        else:
            return True

    def save_all_news_to_csv(self, pages: tuple, verbose: bool = False) -> bool:
        """
        전체 뉴스를 csv로 저장합니다.

        Parameter
        ---------
        path: str
            csv 파일의 경로입니다.
        pages: tuple
            시작 페이지와 끝 페이지를 의미하는 정수타입 튜플입니다.
        """
        for category in self.__categories:
            if verbose:
                print(category, "scraping...")

            success = self.save_news_to_csv(
                f"./{category}.csv", category, pages, verbose
            )
            if not success:
                return False

            if verbose:
                print(category, "scraping done.")
        return True

    def close(self):
        self.__driver.close()


if __name__ == "__main__":
    scraper = NewsScraper()

    print(scraper.save_all_news_to_csv((1, 50), verbose=True))
