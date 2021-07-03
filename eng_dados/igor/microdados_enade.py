from scrapy import Request
import requests
import scrapy
import os

EXAMES = [
    'enade',
]
ANOS = [str(y) for y in range(2004, 2005)]

class Microdados(scrapy.Spider):
    name = 'microdados_enade'
    start_urls = [
        'https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados',
    ]
    def __init__(self, data_path, **kwargs):
        super().__init__(**kwargs)
        self.data_path = data_path

    def parse(self, response):
        cards = response.xpath(
            '/html/body/div[3]/div[1]/main/div[2]/div/div[3]/div/div/div/div/div'
        )
        links = cards.css('a::attr(href)').getall()

        for link in links:
            for exame in EXAMES:
                if exame in link:
                    yield Request(link, callback=self.parse_datasets)
    
    def parse_datasets(self, response):
        datasets = response.xpath(
            '/html/body/div[3]/div[1]/main/div[2]/div/div[5]'
        )
        links = datasets.css('a::attr(href)').getall()

        for link in links:
            for ano in ANOS:
                if ano in link and 'zip' in link:
                    file = link.split('/')[-1]
                    filepath = os.path.join(self.data_path, file)
                    file_content = requests.get(link, allow_redirects=True)

                    with open(filepath, 'wb') as f:
                        f.write(file_content.content)