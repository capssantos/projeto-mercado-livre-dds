# Ativar opções do selenium
from selenium.webdriver.chrome.options import Options as ChromeOptions
# Responsável por gerar o navegador
from selenium import webdriver
# Busca de elementos na tela
from selenium.webdriver.common.by import By
# Exceção de Elementos na tela
from selenium.common.exceptions import NoSuchElementException
# Programar tempo na tela
from selenium.webdriver.support.ui import WebDriverWait
# Tratar tentativas de localização na tela
from selenium.webdriver.support import expected_conditions as EC
# Tratar pop-ups que aparecem na janela
from selenium.webdriver.common.alert import Alert
# Responsável pelas opções do navegador
from selenium.webdriver.chrome.options import Options
# Instanciar serviço do navegador
from selenium.webdriver.chrome.service import Service
# Enviar comandos do teclado na tela do navegado
from selenium.webdriver.common.keys import Keys

from banco import *

connection = PostgreSQLConnection(
    dbname="mecado_livre_produtos",
    user="postgres",
    password="senai2024",
    host="10.130.18.41",
    port="5432"
)

# connection = PostgreSQLConnection(
#     dbname="mercado_livre_produtos",
#     user="postgres",
#     password="postgres",
#     host="localhost",
#     port="5432"
# )

produto = Produto(connection=connection)

options = ChromeOptions()
options.set_capability('se:name', 'Mercado Livre - Captura de Produtos')

# Abrir Navegador
# navegador = webdriver.Remote(options=options, command_executor="http://localhost:4444/wd/hub")
navegador = webdriver.Chrome(options=options)

wait = WebDriverWait(navegador, 60)
navegador.set_page_load_timeout(300)
navegador.get("https://www.mercadolivre.com.br/ofertas")


wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "items-with-smart-groups")))
lista = navegador.find_element(By.CLASS_NAME, "items-with-smart-groups")
for item in lista.find_elements(By.CLASS_NAME, 'andes-card'):
    title = item.find_element(By.CLASS_NAME, "poly-component__title").text
    link = item.find_element(By.CLASS_NAME, "poly-component__title").get_attribute("href")
    link_image = link = item.find_element(By.TAG_NAME, "img").get_attribute("src")
    current_price_element = item.find_element(By.CLASS_NAME, "poly-price__current").text
    
    current_price_text = current_price_element.split('\n')
    price = ''.join([current_price_text[1], current_price_text[2] if ',' in current_price_text[2] else '', current_price_text[3] if ',' in current_price_text[2] else '', ]).replace(".", "").replace(",", ".").strip()

    if not produto.produtos(where=' WHERE NOME = %s', values=(title, )).get('data'):

        # print(title, link, float(price))

        produto.insert_produto(
            empresa="Mercado Livre",
            nome=title,
            preco = float(price),
            imagem=link_image,
            url=link
        )
    
    else:
        print('Produto já cadastrador!')

navegador.quit()