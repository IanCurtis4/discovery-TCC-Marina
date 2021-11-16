from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from collections import Counter
from wordcloud import WordCloud

import matplotlib.pyplot as plt
import re as re
import time

def post_filter(post):
  
  qt_likes = post.find('span', class_ = "social-details-social-counts__reactions-count")

  if qt_likes == None:
      return False

  qt_likes_formatado = "".join(str(qt_likes.string).split('.'))
  return int(qt_likes_formatado) > 5

def Scrape_func(hashtags):
    
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

    posts = linkedin_soup.findAll("div", class_ = "occludable-update ember-view" )

    posts_qt_min_likes = list(filter(post_filter, posts))

    iterations = 0
    
    for post in posts_qt_min_likes:
      
      caixa_texto = post.find("div", class_ = "feed-shared-update-v2__description-wrapper" )

      links_hashtags = caixa_texto.findAll("a", string = re.compile(r'^\#\w+$'))

      for link in links_hashtags:
        hashtags.append(str(link.string))
      
      iterations += 1
      
      if (iterations == 1000):
          break

USUARIO = "contitadowow123@gmail.com"
SENHA = "vickdark123"
HASHTAG = "sass"

chrome_options = webdriver.ChromeOptions()

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

hashtags = []

Scrape_func(hashtags)

driver.quit()

hashtags_normalizadas = []

for hashtag in hashtags:
    
    hashtag_minuscula = hashtag.lower()

    if (hashtag_minuscula[1:] != HASHTAG):
        hashtags_normalizadas.append(hashtag_minuscula)

contagem_hashtags = Counter(hashtags_normalizadas)
wordcloud = WordCloud(width = 1000, height = 500).generate_from_frequencies(contagem_hashtags)

plt.figure(figsize=(15,8))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()
plt.savefig('wordcloud-' + HASHTAG + '.png', bbox_inches='tight')
plt.close()