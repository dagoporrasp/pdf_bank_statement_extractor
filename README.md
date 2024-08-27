# Bank Statement Extractor

**Bank Statement Extractor** es una aplicación de escritorio desarrollada en Python que permite extraer información útil de extractos bancarios en formato PDF. La aplicación está diseñada para soportar extractos de los bancos más populares en Colombia, con una interfaz de usuario sencilla y moderna.

## Características

- **Extracción de datos**: Procesa extractos bancarios en PDF y extrae información clave como fechas, montos, tipos de transacción, saldos, etc.
- **Interfaz gráfica**: La aplicación utiliza `Tkinter` para la interfaz de usuario, con estilos personalizados mediante `ttkbootstrap` para una apariencia moderna y amigable.
- **Compatibilidad**: Actualmente, soporta extractos de 6 bancos colombianos: Banco de Bogotá, Bancolombia, Davivienda, Banco de Occidente, BBVA Colombia, y Banco Caja Social.

## Requisitos Previos

Asegúrate de tener Python 3.x instalado en tu sistema. Además, necesitarás instalar las siguientes dependencias:

```bash
pip install -r requirements.txt
```

## Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/tu-usuario/bank-statement-extractor.git
   ```

2. Navega al directorio del proyecto:

   ```bash
   cd bank-statement-extractor
   ```

3. Instala las dependencias necesarias:

   ```bash
   pip install -r requirements.txt
   ```

## Uso

Para ejecutar la aplicación, simplemente utiliza el siguiente comando:

```bash
python extractosPDF_app.py
```

1. Esto abrirá la interfaz gráfica donde podrás seleccionar los archivos PDF de los extractos bancarios y procesarlos para extraer la información.

<p align="center">
<!-- ![Alt text](static\Home_Extractos_app.jpg "Home") -->
<img src="static\Home_Extractos_app.jpg" alt="drawing" width="300"/>
</p>

LLena el formulario y elige si desear procesar únicamente un archivo ó un directorio que contenta los extractos Bancarios.

<p align="center">
<img src="static\form_Extractos_app.jpg" alt="drawing" width="300"/>
</p>

## Estructura del Proyecto
- **/bank_parsers**: Módulos para procesar extractos bancarios específicos de cada banco.
- **extractosPDF_app.py**: Archivo principal que ejecuta la aplicación.

## Contribución

Las contribuciones son bienvenidas. Si deseas contribuir, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios y haz commit (`git commit -m 'feat: Añadir nueva funcionalidad'`).
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](./LICENSE) para más detalles.

