#!/usr/bin/env python3.10
# -*- coding=utf-8 -*-
# 2023, Noa Velasco
# pylint: disable=C0103

"""
Una aplicación que recorre poco a poco un diccionario
y entra en el _DPD_ para comprobar si existen los verbos.

Si se encuentra en el _DPD_, crea una nota personalizada
en un archivo de Markdown. Además de los datos del _DPD_,
también añade la definición del _Diccionario de la lengua española_.
"""

import time
import requests
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

url_base = "https://www.rae.es/dpd/"
# Para poder acceder a la web de la RAE, hay que decirle que somos humanos.
headers = {'User-Agent': 'Mozilla/5.0'}
# Para evitar un cuelgue indefinido, establecemos límite de 5 segundos.
timeout = 5

# Al scrapear de la página del DPD, los enlaces se rompen.
# Funciones para encontrar elementos con algún patrón:
def href_starts_with(tag):
    '''Encontrar elementos <a href> que empiecen por /dpd/'''
    return tag.name == 'a' and tag.get('href', '').startswith('/dpd/')


def href_not_starts_with(tag):
    '''Encontrar elementos <a href> que NO empiecen por /dpd/'''
    href = tag.get('href', '')
    return tag.name == 'a' and href and not href.startswith('/dpd/')


def has_class_k5_or_k6(tag):
    '''Encontrar clases k5 y k6 del DLE, que son locuciones y similares'''
    return tag.name == 'p' and ('k5' in tag.get('class', []) or 'k6' in tag.get('class', []))


def dle_rae(word):
    '''Scrapea la definición de una palabra del DLE.
    Para mantener el formato de cursivas, negritas, etc.,
    se sustituyen las clases concretas.'''

    url_rae = "https://dle.rae.es/"
    url_definicion = f'{url_rae}{word}'
    headers_dle = {'User-Agent': 'Mozilla/5.0'}
    timeout_dle = 5  # segundos

    try:
        response_dle = requests.get(
            url_definicion, headers=headers_dle, timeout=timeout_dle)

        if response_dle.ok:
            soup_dle = BeautifulSoup(response_dle.text, 'lxml')

            # La definición está en la etiqueta <article> y solo hay una.
            resultados = soup_dle.find('article')

            # Si la palabra existe en el diccionario, tiene esa etiqueta.
            if resultados is not None:
                # eliminar la palabra que se define; no nos interesa.
                title = resultados.find('header')
                title.decompose()

                # introducir '>' antes de cada línea para formato de callout md.
                p_tags = resultados.find_all('p')
                for p_tag in p_tags:
                    p_tag.insert(0, '>')

                # cambiar a cursiva los ejemplos.
                ejemplos = resultados.find_all('span', 'h')
                for ejemplo in ejemplos:
                    ejemplo.name = 'em'

                # cambiar a cursiva ciertas abreviaturas.
                abbrs = resultados.find_all('abbr', 'c')
                for abbr in abbrs:
                    abbr.name = 'em'

                # cambiar a may. preposiciones de ejemplos.
                preposiciones = resultados.find_all('span', 'i1')
                for prepo in preposiciones:
                    prepo.string = prepo.string.upper()

                # cambiar a negrita los números de acepción.
                n_acep = resultados.find_all('span', 'n_acep')
                for acep in n_acep:
                    acep.name = 'strong'

                # cambiar hiperenlaces por negrita.
                h_enlaces = resultados.find_all('a', 'a')
                for enlace in h_enlaces:
                    enlace.name = 'b'

                # cambiar locuciones y composiciones por negrita.
                locuciones = soup_dle.find_all(has_class_k5_or_k6)
                for locucion in locuciones:
                    locucion.insert_before('>  \n')

                # Convertimos el soup en formato markdown con este módulo.
                # Es el único que me ha respetado correctamente todo el formato.
                md_converter_dle = MarkdownConverter()
                markdown_string_dle = md_converter_dle.convert_soup(resultados)

                # eliminar los saltos innecesarios
                markdown = markdown_string_dle.replace('\n\n', '\n')
                markdown = markdown.replace('\n\n', '\n')

                return markdown

        else:
            print('Mala respuesta para', url_definicion, response.status_code)
    except requests.exceptions.ConnectionError as exc:
        print(exc)

# Comprobamos cuál es la siguiente lista de verbos que vamos a emplear.
# Como estamos iterando +10000 verbos, he creado 108 listas con 100 verbos cada una.
# La manera de seguir el orden es consultando la lista de listas, coger la primera
# y luego borrarla de la lista para ir en orden.
with open('lista_verbos/listalistas.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
lista_actual = lines[0].strip()
url_lista = f'lista_verbos/{lista_actual}'

# Ahora extraemos los 100 verbos de la lista que nos toca
with open(url_lista, 'r', encoding='utf-8') as fh:
    urls = fh.readlines()

# Esto es para mostrar avances en la consola.
contador = 1
encontrados = 0

for url in urls:
    # Vamos a esperar un poco entre scrapeos para no saturar la red.
    # Entre 0.5 y 2 segundos, por ejemplo.
    time.sleep(2)
    # Cada verbo de la lista tiene al final un salto que necesitamos quitar:
    url = url.strip()
    url_total = f'{url_base}{url}'
    try:
        response = requests.get(url_total, headers=headers, timeout=timeout)
        if response.ok:
            soup = BeautifulSoup(response.text, 'lxml')
            resultados_entry = soup.find('entry')
            if resultados_entry is not None:
                # Estos son los enlaces estropeados que hay que corregir.
                # Encuentra los elementos que coinciden con el patrón y
                # modifica el atributo href de los elementos encontrados:
                a_tags = soup.find_all(href_not_starts_with)
                for a_tag in a_tags:
                    a_tag['href'] = url_total + a_tag['href']

                a_tags = soup.find_all(href_starts_with)
                for a_tag in a_tags:
                    a_tag['href'] = 'https://www.rae.es' + a_tag['href']

                img_tags = soup.find_all('img')
                for img_tag in img_tags:
                    img_tag['src'] = 'https://www.rae.es' + img_tag['src']

                md_converter = MarkdownConverter()
                markdown_string = md_converter.convert_soup(resultados_entry)
                file = f'verbos/{url}.md'

                definicion = dle_rae(url)

                with open(file, 'w', encoding='utf-8') as f:
                    f.write(f'# {url}\n[[_index|índice]]\n')
                    f.write(markdown_string)
                    f.write(f'>[!DICCIONARIO]\n>**{url}**')
                    f.write(definicion)
                    f.write(
                        '\n---\n[[_index | índice]]\n[[verbos]]\n[[tiempos verbales]]\n#verbos')

                # Cuando crea una nueva nota de un verbo, lo señala.
                with open('lista_verbos/verbos_scrapeados.txt', 'a', encoding='utf-8') as f:
                    f.write(f'{url}\n')
                print(f'{contador:03d} - {url}: añadido')
                encontrados += 1

            else:
                # Cuando no se encuentra el verbo, lo señala.
                with open('lista_verbos/verbos_failed.txt', 'a', encoding='utf-8') as f:
                    f.write(f'{url}\n')
                print(f'{contador:03d} - {url}: no existe')
        else:
            print('Mala respuesta para', url, response.status_code)
            with open('lista_verbos/verbos_failed.txt', 'a', encoding='utf-8') as f:
                f.write(f'{url}\n')

    except requests.exceptions.ConnectionError as exc2:
        print(exc2)
        with open('lista_verbos/verbos_failed.txt', 'a', encoding='utf-8') as f:
            f.write(f'{url}\n')
    contador += 1

# Elimina la primera lista de 'listalistas.txt'
lines.pop(0)
with open('lista_verbos/listalistas.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l)

print(f'Se han añadido {encontrados} verbos.\nTerminado')
