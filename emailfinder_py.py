import sys  # para poder usar argumentos no terminal
import re  # será usado para pegar os emails usando expressões regulares

import requests  # necessário a instalação para uso: pip install requests
from bs4 import BeautifulSoup  # necessário a instalação: pip install bs4

TO_CRAWL = []  # url inicial para iniciar o crawling
CRAWLED = set()  # url já passadas - usamos o "set" pois com ele é mais fácil de verificar se já foi ou não
EMAILS = []  # para não pegar emails repetidos


def request(url):  # transformando a resposta do URL para text
    # alguns sites não aceitam conexão que não sejam de browsers, para contar isso vamos criar um HEADER falso
    header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"}
    try:
        resposta = requests.get(url, headers=header)
        return resposta.text
    except KeyboardInterrupt:
        sys.exit(0)  # para poder encerrar o programa como CTRL+C
    except:
        pass


def pegar_links(html):  # função para pegar os links no crawling
    links = []  # lista dos links obtidos
    try:
        # o soup que será usado para poder pegar as tags no HTML
        # as tags "a" com o "href" são as que contém os links e serão as que vou pegar para gerar o crawling
        soup = BeautifulSoup(html, "html.parser")
        tags_a = soup.find_all("a", href=True)  # para encontrar todas as tags "a" no HTML
        # como nem todas as tags de "a" tem o href, temos que determinar que vamos pegar apenas as que tenham

        # agora para cada tag que ele pegar, ele vai pegar um link que está no "href"
        for tag in tags_a:
            link = tag["href"]

            # nem sempre no href vai ter um link, com isso vamos pegar e tirar tudo que não começa com HTTPS
            if link.startswith("http") or link.startswith("www"):
                links.append(link)  # adicionando o link na lista "links"

        return links
    except:
        pass


def pegar_emails(html):
    # aqui vamos pegar por padrões de email
    # pode-se usar dois padrões do regex para validar emails:
    # simples: \w[\w\.]+\w@\w[\w\.]+\w
    # completa: ^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))*$

    emails = re.findall(r"\w[\w\.]+\w@\w[\w\.]+\w", html)
    return emails


def crawl():  # função do crawling
    while True:
        if TO_CRAWL:  # precisa ter algo no TO_CRAWL para funcionar
            # nesse caso ele vai retirar um elemento do TO_CRAWL e vai transfomar em uma url
            url = TO_CRAWL.pop()  # se ele estiver vazio, pode dar erro também por isso precisamos confirmar o link
            html = request(url)
            if html:
                links = pegar_links(html)

                # agora vai verificar se o link está na lista TO_CRAWL ou CRAWLED.
                # caso não ele vai adicionar no TO_CRAWL e fazer o crawling nesse link
                if links:
                    for link in links:
                        if link not in CRAWLED and link not in TO_CRAWL:
                            TO_CRAWL.append(link)

                emails = pegar_emails(html)
                for email in emails:
                    if email not in EMAILS:  # para garantir que não tenham emails duplicados na lista
                        print(email)
                        EMAILS.append(email)

                CRAWLED.add(url)
            else:
                CRAWLED.add(url)
        else:
            print("Done")
            break


if __name__ == "__main__":
    url = sys.argv[1]
    try:
        TO_CRAWL.append(url)
        crawl()
    except Exception as e:
        print(f"Erro: {e}")
        pass

