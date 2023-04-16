# Scraping verbos del Diccionario Panhispánico de Dudas

Una aplicación que recorre poco a poco un diccionario y entra en el _DPD_ para comprobar si existen los verbos.  

Si se encuentra en el _DPD_, crea una nota personalizada en un archivo de Markdown. Además de los datos del _DPD_, también añade la definición del _Diccionario de la lengua española_.  

El código utiliza los módulos:
- time
- requests\*
- bs4 (BeautifulSoup)\*
- markdownify\*  

_\* requiere instalación PIP._

Este es un proyecto personal para un compendio de notas de corrección en Obsidian, pero viene documentado para realizar cualquier cambio de forma sencilla y adaptarlo a otras necesidades.

Para no saturar la red de la RAE, en lugar de realizar un raspado completo de los +10000 verbos de un diccionario de verbos, va comprobando un verbo cada 2 segundos hasta llegar a 100 por sesión. El diccionario es de [este repositorio](https://github.com/olea/lemarios.git) (gracias a Ismael Olea).  

## Uso
Para ejecutar la herramienta tal y como está pensada, hay que asegurarse de que el contenido de `lista_verbos\llistalistas.txt` empieza por `lista_001.txt` y sigue de forma consecutiva hasta el 108. Si no es el caso, solo hay que usar el contenido de `lista_verbos\listalistas_bckp.txt` o ejecutar este código al final del archivo de Jupyter Notes (o crearlo en la carpeta raíz del proyecto): 

```python
listalistas = []
nombrefile = 'lista_'
for i in range(1,109):
    listalistas.append(f'{nombrefile}{i:03d}.txt')

print(listalistas[0])
with open('lista_verbos/listalistas_bckp.txt', 'w', encoding='utf-8') as f:
    for l in listalistas:
        f.write(l + '\n')
```

Se puede cambiar el código para ir más rápido modificando o eliminando la siguiente línea:

```python
    time.sleep(2)
```

Pero para comprobar todos los verbos de una sola vez hay que modificar el archivo `listalistas.txt`. Solo hay que sustituir todo el contenido por `verbos-espanol.txt`. De este modo, la herramienta encontrará que es la lista que hay que usar.

En la consola de la terminal se irá mostrando el progreso del 001 al 100:

> 001 - anastomosarse: no existe  
> 002 - anatematizar: añadido  
> 003 - anatemizar: añadido  
> 004 - anatomizar: no existe  
> 005 - anchar: no existe  
> 006 - anchoar: no existe  
> …  
> 100 - aparar: no existe  
> Se han añadido 21 verbos.  
> Terminado  
