from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from collections import Counter, OrderedDict
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from uuid import uuid4
from statistics import mean
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import numpy as np
import re as re
import time
import string

PALAVRAS_POSTS = []

wordnet_lemmatizer = WordNetLemmatizer()
 
def post_filter(post):
  
  qt_likes = post.find('span', class_ = "social-details-social-counts__reactions-count")

  if qt_likes == None:
      return False

  qt_likes_formatado = "".join(str(qt_likes.string).split('.'))

  return int(qt_likes_formatado) > 50

def Scrape_func_passo1(hashtags):
    
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    
    while True:
    
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
  
      time.sleep(1)
  
      newHeight = driver.execute_script("return document.body.scrollHeight")
  
      if newHeight == lastHeight:
          break
  
      lastHeight = newHeight

    company_page = driver.page_source   

    linkedin_soup = bs(company_page.encode("utf-8"), "html")
    linkedin_soup.prettify()

    posts = linkedin_soup.findAll("div", class_ = "occludable-update ember-view")

    posts_qt_min_likes = list(filter(post_filter, posts))
    
    for post in posts_qt_min_likes:
      
      caixa_texto = post.find("div", class_ = "feed-shared-update-v2__description-wrapper")

      links_hashtags = caixa_texto.findAll("a", string = re.compile(r'^\#\w+$'))

      for link in links_hashtags:
        hashtags.append(str(link.string))

def Scrape_func_passo2():

  res = []
  
  lastHeight = driver.execute_script("return document.body.scrollHeight")
  
  while True:
  
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(1)

    newHeight = driver.execute_script("return document.body.scrollHeight")

    if newHeight == lastHeight:
      break

    lastHeight = newHeight

  company_page = driver.page_source   

  linkedin_soup = bs(company_page.encode("utf-8"), "html")
  linkedin_soup.prettify()

  posts = linkedin_soup.findAll("div", class_ = "occludable-update ember-view")

  posts_qt_min_likes = list(filter(post_filter, posts))

  stop_words = set(stopwords.words('english'))
  
  for post in posts_qt_min_likes:

    post_res = {}

    post_res["id"] = uuid4()

    nome_publicante_campo = post.find('span', class_ = "feed-shared-actor__title")

    nome_publicante = nome_publicante_campo.find('span', dir = "ltr").string

    post_res["publicante"] = nome_publicante

    qt_likes = post.find('span', class_ = "social-details-social-counts__reactions-count")
    
    post_res["interacoes"] = int(qt_likes.string) if qt_likes is not None else 0

    caixa_texto = post.find("div", class_ = "feed-shared-update-v2__description-wrapper")

    texto = caixa_texto.text

    tokens_texto = word_tokenize(texto)

    tokens_texto_filtrado = [p.lower() for p in tokens_texto if not p.lower() in stop_words and not p in string.punctuation]

    tokens_texto_lemmatizado = [wordnet_lemmatizer.lemmatize(t) for t in tokens_texto_filtrado]

    post_res["palavras"] = tokens_texto_lemmatizado

    PALAVRAS_POSTS.extend(tokens_texto_lemmatizado)

    res.append(post_res)

  return res

USUARIO = "contitadowow123@gmail.com"
SENHA = "vickdark123"
HASHTAG = "sass"

driver = webdriver.Chrome()
driver.get("https://www.linkedin.com/login/pt")

time.sleep(3)

email = driver.find_element_by_id("username")
email.send_keys(USUARIO)
print(str(email))

senha = driver.find_element_by_id("password")
senha.send_keys(SENHA)
print(str(senha))

enviar = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
enviar.click()

time.sleep(3)

driver.get("https://www.linkedin.com/feed/hashtag/" + HASHTAG + "/")

time.sleep(3)

# hashtags = []

# Scrape_func_passo1(hashtags)

POSTS = Scrape_func_passo2()

driver.quit()

INTERACOES_MAX = sorted([post["interacoes"] for post in POSTS])[0]

palavras_posts_counter = Counter(PALAVRAS_POSTS)

palavras_posts_count_ordenadas = OrderedDict(palavras_posts_counter.most_common())

SOMA_CONTAGEM_PALAVRAS = sum(palavras_posts_count_ordenadas.values())

def extrair_frequencia_media_palavras(palavras):

  return mean(map(lambda p: palavras_posts_count_ordenadas[p] / SOMA_CONTAGEM_PALAVRAS, palavras))

def extrair_interacoes_normalizadas(interacoes_post):

  return (interacoes_post - 50) / (INTERACOES_MAX - 50)

for post in POSTS:
  post["frequencia_media_palavras"] = extrair_frequencia_media_palavras(post["palavras"])
  post["interacoes_normalizadas"] = extrair_interacoes_normalizadas(post["interacoes"])
  post["coordenadas"] = (post["frequencia_media_palavras"], post["interacoes_normalizadas"])

kmeans = KMeans()

array_coords = np.array([post["coordenadas"] for post in POSTS])

kmeans.fit(array_coords)

plt.scatter(array_coords[:, 0], array_coords[:, 1], c=kmeans.predict(array_coords), s=50, cmap='viridis')

centers = kmeans.cluster_centers_

plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)

plt.plot()

# hashtags_normalizadas = []

# for hashtag in hashtags:
    
#     hashtag_minuscula = hashtag.lower()

#     if (hashtag_minuscula[1:] != HASHTAG):
#         hashtags_normalizadas.append(hashtag_minuscula)

# contagem_hashtags = Counter(hashtags_normalizadas)
# wordcloud = WordCloud(width = 1000, height = 500).generate_from_frequencies(contagem_hashtags)

# plt.figure(figsize=(15,8))
# plt.imshow(wordcloud)
# plt.axis("off")
# plt.show()
# plt.savefig('wordcloud-' + HASHTAG + '.png', bbox_inches='tight')
# plt.close()
