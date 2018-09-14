from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from geopy.geocoders import Nominatim

import json
import argparse
import collections
import os



def linux_conf():
    outfile = "/srv/shiny-server/kebasic/KeBaSiC/paginas.json"
    chromedriverpath="/srv/shiny-server/kebasic/KeBaSiC/chromedriver"

    return outfile, chromedriverpath

def windows_conf():
    outfile = "D:/Documenti/kebasic/KeBaSiC/paginas.json"
    chromedriverpath="D:/Documenti/kebasic/KeBaSiC/chromedriver.exe"

    return outfile, chromedriverpath

def ir_paginas_amarillas_web(cadena, city, geolocator):
    
    
    display = Display(visible=0, size=(1024, 768))
    display.start()

    #outfile, chromedriverpath = windows_conf()
    outfile, chromedriverpath = linux_conf()

    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox");    
    options.add_argument("--disable-dev-shm-usage"); 

    os.environ["webdriver.chrome.driver"] = chromedriverpath
    
    driver = webdriver.Chrome(executable_path=chromedriverpath, chrome_options=options)
    
    
    #Página a la que queremos acceder
    driver.get("https://www.paginasamarillas.es/")
    lista_datos = []
    try:
        #Verificamos si el elemento con ID="whatInput" ya está cargado, este elemento es la caja de texto donde se hacen las busquedas
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "whatInput")))
        #Obtenemos la caja de texto de busquedas
        input_nombre = driver.find_element_by_id("whatInput")
        #Enviamos la cadena que estamos buscando
        input_nombre.send_keys(cadena)
        #Verificamos si el elemento con ID="whereInput" ya está cargado, este elemento es la caja de lugar donde se hacen las busquedas
        input2_nombre = driver.find_element_by_id("whereInput")
        #Enviamos la ciudad que estamos buscando
        input2_nombre.send_keys(city)
        #Obtenemos el botón que ejecuta la búsqueda
        boton = driver.find_element_by_id("submitBtn")
        #Damos click al botón
        boton.click()
    except:
        #Mostramos este mensaje en caso de que se presente algún problema
        print ("El elemento no está presente")
    try:
        #Si se encuentran resultados la página los muestra en elementos de nombre "listado-item"
        #Para ello esperamos que estos elementos se carguen para proceder a consultarlos
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "listado-item")))
    except:
        print ('Elementos no encontrados')
        #Obtenemos en una lista los elementos encontrados

    resultados = driver.find_elements_by_class_name("listado-item")

    i = 0
    risultati = {}
    risultati['competitors'] = []

    for resultado in resultados:
        if i<10:
            try:
                tmp = {}
                el = resultado.find_element_by_class_name("box")
                tmp['url'] = el.find_element_by_class_name("web").get_attribute("href")
                tmp['name'] = el.find_element_by_class_name("comercial-nombre").find_element_by_tag_name("span").text
                tmp['description'] = el.find_element_by_class_name("col-xs-8").text
                address = el.find_element_by_class_name("location").find_element_by_tag_name("span").text
                location = geolocator.geocode(address)
                if location is not None:
                    tmp['lat'] = location.latitude
                    tmp['long'] = location.longitude
                else:
                    tmp['lat'] = ''
                    tmp['long'] = ''
                ordered_tmp = collections.OrderedDict(sorted(tmp.items()))
                risultati['competitors'].append(ordered_tmp)
                i += 1

            except:
                i+=1

    


    with open(outfile, "w") as f:
        f.write(json.dumps(risultati, ensure_ascii=True))


    driver.close()
    display.stop()
    return lista_datos

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-keywords", default="")
    #parser.add_argument("-location", default="")
    args = parser.parse_args()
    geolocator = Nominatim(user_agent="KebTest")
    ir_paginas_amarillas_web(vars(args)['keywords'],"", geolocator)
    #return(ir_paginas_amarillas_web('derecho',''))
main()
