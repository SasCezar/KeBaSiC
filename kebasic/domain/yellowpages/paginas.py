from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import argparse
from geopy.geocoders import Nominatim
#from pyvirtualdisplay import Display


def ir_paginas_amarillas_web(cadena, city, geolocator):
    #display = Display(visible=0, size=(900,600))
    #  #display.start()

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    chromedriverpath=r'C:\Users\marco\Desktop\KeBaSiC\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=chromedriverpath, options=options)

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
        if i<=10:
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

                risultati['competitors'].append(tmp)
                i += 1

            except:
                i+=1


    with open("C:/users/marco/desktop/paginas.json", "w") as f:
        f.write(json.dumps(risultati, ensure_ascii=True))


    driver.close()
    return lista_datos

def main():
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-keywords", default="")
    parser.add_argument("-location", default="")
    args = parser.parse_args()
    geolocator = Nominatim(user_agent="KebTest")
    ir_paginas_amarillas_web(vars(args)['keywords'],vars(args)['location'],geolocator)
    '''
    ir_paginas_amarillas_web(vars(args)['keywords'], vars(args)['location'], geolocator)
    #return(ir_paginas_amarillas_web('derecho',''))
main()
