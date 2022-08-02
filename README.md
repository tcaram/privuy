[![GPL-3.0 license][license-shield]][license-url]

<div align="center">
  <h3 align="center">PrivUY</h3>

  <p align="center">
    Detectando patrones de rastreo y aprovechamiento privado de datos en sitios web gubernamentales
  </p>
</div>

<details>
  <summary>Tabla de Contenidos</summary>
  <ol>
    <li>
      <a href="#sobre-el-proyecto">Sobre el proyecto</a>
      <ul>
        <li><a href="#sobre-el-softwaren">Sobre el software</a></li>
      </ul>
      <ul>
        <li><a href="#desarrollado-con">Desarrollado con</a></li>
      </ul>
    </li>
    <li>
      <a href="#guía-de-uso">Guía de uso</a>
      <ul>
        <li><a href="#requerimientos">Requerimientos</a></li>
        <li><a href="#instalación">Instalación</a></li>
      </ul>
    </li>
    <li><a href="#licencia">Licencia</a></li>
    <li><a href="#contacto">Contacto</a></li>
  </ol>
</details>


## Sobre el proyecto

Múltiples estudios <sup><a href="https://dl.acm.org/doi/10.1145/2976749.2978313">1</a></sup> <sup><a href="https://ieeexplore.ieee.org/document/9289071">2</a></sup> han demostrado que hoy en día, un 70% de los sitios más populares integran sistemas de rastreo que se ejecutan en segundo plano sin el consentimiento de los usuarios. Herramientas que a priori pueden parecer inofensivas, como un mapa interactivo o una herramienta para generar analíticas <sup><a href="https://blog.google/products/marketingplatform/analytics/take-control-how-data-used-google-analytics/">3</a></sup>, pueden comprometer la privacidad de los usuarios, generando la posibilidad de que sus datos y comportamientos en la web terminen siendo comercializados o utilizados para entregar publicidad personalizada <sup><a href="https://www.eff.org/deeplinks/2020/03/google-says-it-doesnt-sell-your-data-heres-how-company-shares-monetizes-and">4</a></sup>.
En un contexto donde el Gobierno Digital está teniendo cada vez más importancia, es menester para ejercer una ciudadanía digital responsable conocer cómo es tratada nuestra información cuando hacemos uso de los servicios en línea del Estado. En esta investigación se recopilará información de más de 700 sitios del Estado y se analizará la presencia de rastreadores y proveedores de hosting extranjeros.

### Sobre el software

PrivUY simula de manera autónoma la navegación normal que tendría un usuario tipo en una lista de servicios web del Estado (indicados en la lista ```input/domain_list.txt```). Durante esta navegación, se recopilan diversos datos del sitio web: scripts para generar analíticas, cargas de multimedia (imágenes, videos, etc.), botones sociales (Compartir en Facebook, Twitter, etc.), cualquier carga o petición hacia sitios externos, y la dirección IP del servidor donde se aloja el sitio web. Con ayuda de la herramienta Privacy Badger se detectan cuáles de estos artilugios efectivamente realizan tareas de rastreo. Posteriormente se verifica también en los registros de ICANN, a qué empresa pertenece la dirección IP asociada al sitio web para detectar si dicho sitio está siendo alojado en servidores del Estado. Luego de procesar los sitios, para cada sitio detalla cuántos rastreadores, dónde está alojado y si el servidor pertenece al gobierno. A partir de esa información se puede obtener una idea general de cuál es el estado actual.

### Desarrollado con

* [![Python][Python]][Python-url]
* [![Selenium][Selenium]][Selenium-url]

## Guía de uso

Debajo se detalla el software y dependencias requeridas para ejecutar localmente el proyecto y los pasos para su instalación. Luego, se explica cómo ejecutarlo y generar reportes. 

### Requerimientos

* [Python 3][https://python.org]
* Linux con entorno gráfico (o xvfb en su defecto [la instalación queda por fuera del alcance de este manual])
* Navegador Chrome

### Instalación

1. Clonar repositorio
  ```sh
  git clone https://github.com/tcaram/privuy
  ```
2. Instalar dependencias
  ```sh
  python3 -m pip install -r requirements.txt
  ```
3. Descargar última versión de Privacy Badger
  ```sh
  wget https://www.eff.org/files/privacy_badger-chrome.crx
  ```

### Ejecución

Para generar el reporte de cada sitio:

```sh
python3 privuy.py
```

Luego de generar el reporte, se puede "digerir" y generar analíticas:
```sh
python3 analytics.py
```

Tanto el reporte como las analíticas, quedan guardados en el directorio ``output``.

## Licencia

Distribuido bajo la licencia GNU GPL V3. Ver `LICENSE.txt` para más información.

## Contacto

Tomás Caram <tomas.caram (at) fing.edu.uy>

[license-shield]: https://img.shields.io/github/license/tcaram/privuy.svg?style=for-the-badge
[license-url]: https://github.com/tcaram/privuy/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.png
[Python]: https://img.shields.io/badge/Python-ffff00?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org/
[Selenium]: https://img.shields.io/badge/Selenium-ffff00?style=for-the-badge&logo=selenium&logoColor=white
[Selenium-url]: https://selenium.dev/