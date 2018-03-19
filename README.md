== Installation

You need to install Libreoffice and, in some systems, the
libreoffice-script-provider-python package and related UNO packages. In 
Ubuntu this would be:

```bash
sudo apt install libreoffice libreoffice-script-provider-python uno-libs3 python3-uno python3
```

== Usage

- Open Libroffice with the command line:

```bash
soffice --accept='socket,host=localhost,port=8100;urp;StarOffice.Service'
```
