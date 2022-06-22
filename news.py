class News:
    """
    뉴스 데이터클래스입니다.

    Properties
    ----------
    title: str
        뉴스기사의 제목입니다.

    description: str
        뉴스기사 요약문입니다.

    image: str
        간략한 뉴스기사 이미지입니다.

    url: str
        기사의 네이버 링크입니다.

    publish_date: str
        기사의 발행일입니다.
    """

    def __init__(self, title, description, image, url, publish_date) -> None:
        self.title = title
        self.description = description
        self.image = image
        self.url = url
        self.publish_date = publish_date
