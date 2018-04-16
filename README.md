(Spanish language, since this script is intended for writers, tldr; this is an OpenOffice linter for Spanish literary language).

## Intro

Pyterato es un sencillo script que comprueba errores comunes en textos
literarios en Español.

## Instalación

Tienes que instalar OpenOffice o LibreOffice (realmente sólo lo he probado con 
LibreOffice). También requiere el paquete script-provider-python.

En Ubuntu eso se haría de la siguiente forma:

```bash
sudo apt install libreoffice libreoffice-script-provider-python uno-libs3 python3-uno python3
pip3 install unotools
```

## Uso

- Abre LibreOffice con el siguiente comando:

```bash
soffice --accept='socket,host=localhost,port=8100;urp;StarOffice.Service'
```

- En LibreOffice, abre el documento que quieres examinar.

- Ejecuta pyterato (con Python3):

```bash
python3 pyterato.py
```

- Corrige errores...

Considera la mayoría de los mensajes como advertencias; actualmente el script
está en un estado muy inicial y simplemente comprueba usos de palabras (no tiene
aún procesado de lenguaje natural) por lo que en muchas ocasiones producirá falsos
positivos. Usa tu sentido común para determinar si las correcciones indicadas se
aplican al texto.

## Problemas

Si al ejecutarlo te da un error similar a éste:

```
Traceback (most recent call last):
  File "cli.py", line 9, in <module>
    import uno
  File "/usr/local/lib/python3.6/dist-packages/uno/__init__.py", line 4, in <module>
    from base import Element, Css, Payload, UnoBaseFeature, UnoBaseField
ModuleNotFoundError: No module named 'base'
```

Sigue estos pasos:

1. Desistala los módulos `uno` y `unotools` de pip:

```pip3 uninstall uno unotools```

2. Instala o reinstala los paquetes de tu distribución (ver más arriba para Ubuntu). 
Si usas `apt`, añade el parámetro `--reinstall`.

3. Reinstala el paquete:

```
pip3 install pyterato
```
