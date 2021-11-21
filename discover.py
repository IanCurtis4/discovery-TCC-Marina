from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from collections import Counter, OrderedDict
# from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from uuid import uuid4
from statistics import mean
from sklearn.cluster import KMeans
from langdetect import detect

import matplotlib.pyplot as plt
import numpy as np
import re as re
import time
import string
import nltk
import pprint
import stanza

stanza.download('pt')

nlp = stanza.Pipeline('pt')

PALAVRAS_POSTS = []

wordnet_lemmatizer = WordNetLemmatizer()

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
 
def post_filter(post):
  
  qt_likes = post.find('span', class_ = "social-details-social-counts__reactions-count")

  if qt_likes == None:
      return False

  qt_likes_formatado = "".join(str(qt_likes.string).split('.'))

  return int(qt_likes_formatado) > 5

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

  lista_ver_mais = driver.find_elements(By.XPATH, "//*[text()='...ver mais']")

  time.sleep(3)

  if lista_ver_mais is not None:
    for ver_mais in lista_ver_mais:
      ver_mais.click()

  time.sleep(3)

  company_page = driver.page_source   

  linkedin_soup = bs(company_page.encode("utf-8"), "html")
  linkedin_soup.prettify()

  posts = linkedin_soup.findAll("div", class_ = "occludable-update ember-view")

  posts_qt_min_likes = list(filter(post_filter, posts))

  stop_words = set(stopwords.words('english'))

  stop_words_pt = set(stopwords.words('portuguese'))
  
  for post in posts_qt_min_likes:

    post_res = {}

    post_res["id"] = str(uuid4())

    nome_publicante_campo = post.find('span', class_ = "feed-shared-actor__title")

    nome_publicante = nome_publicante_campo.find('span', dir = "ltr").string

    post_res["publicante"] = nome_publicante

    qt_likes = post.find('span', class_ = "social-details-social-counts__reactions-count")
    
    post_res["interacoes"] = int("".join(str(qt_likes.string).split('.'))) if qt_likes is not None else 0

    caixa_texto = post.find("div", class_ = "feed-shared-update-v2__description-wrapper")

    texto = caixa_texto.text

    if detect(texto) != "pt":
      
      tokens_texto = word_tokenize(texto)

      tokens_texto_filtrado = [p.lower() for p in tokens_texto if not p.lower() in stop_words and not p in string.punctuation]

      tokens_texto_lemmatizado = [wordnet_lemmatizer.lemmatize(t) for t in tokens_texto_filtrado]

      post_res["palavras"] = tokens_texto_lemmatizado

      PALAVRAS_POSTS.extend(tokens_texto_lemmatizado)
    
    else:

      tokens_texto_lemmatizado = [word.lemma for sentence in list(nlp(texto).sentences) for word in sentence.words if word.text not in stop_words_pt and word.text not in string.punctuation]

      post_res["palavras"] = tokens_texto_lemmatizado

      PALAVRAS_POSTS.extend(tokens_texto_lemmatizado)

    res.append(post_res)

  return res

USUARIO = "contitadowow123@gmail.com"
SENHA = "vickdark123"
HASHTAG = "csharp"

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

INTERACOES_MAX = sorted([post["interacoes"] for post in POSTS])[-1]

print(INTERACOES_MAX)

palavras_posts_counter = Counter(PALAVRAS_POSTS)

palavras_posts_count_ordenadas = OrderedDict(palavras_posts_counter.most_common())

PALAVRAS_MAX = sorted(palavras_posts_count_ordenadas.values())[-1]

print(PALAVRAS_MAX)

def extrair_frequencia_media_palavras(palavras):

  return mean(map(lambda p: palavras_posts_count_ordenadas[p] / PALAVRAS_MAX, palavras))

def extrair_interacoes_normalizadas(interacoes_post):

  return (interacoes_post - 5) / (INTERACOES_MAX - 5)

def extrair_frequencia_normalizada(frequencia):
  return frequencia / FREQUENCIAS_MAX

for post in POSTS:
  post["frequencia_media_palavras"] = extrair_frequencia_media_palavras(post["palavras"])
  post["interacoes_normalizadas"] = extrair_interacoes_normalizadas(post["interacoes"])

FREQUENCIAS_MAX = sorted([post["frequencia_media_palavras"] for post in POSTS])[-1]

for post in POSTS:
  post["frequencia_normalizada"] = extrair_frequencia_normalizada(post["frequencia_media_palavras"])
  post["coordenadas"] = (post["frequencia_normalizada"], post["interacoes_normalizadas"])

# pprint.pprint(POSTS)

post_max_curtidas = list(filter(lambda p: p["interacoes_normalizadas"] == 1.0, POSTS))[0]

pprint.pprint(post_max_curtidas)

kmeans = KMeans()

array_coords = np.array([post["coordenadas"] for post in POSTS])

kmeans.fit(array_coords)

plt.scatter(array_coords[:, 0], array_coords[:, 1], c=kmeans.predict(array_coords), s=50, cmap='viridis')

centers = kmeans.cluster_centers_

plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)

plt.show()
plt.close()

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
