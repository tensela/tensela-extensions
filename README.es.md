# El catálogo de extensiones de Tensela

[In English](README.md)

Las extensiones que se muestran en [tensela.com/es/extensions](https://tensela.com/es/extensions/): un archivo por
extensión en `extensions/<id>.json`. Tensela misma no lee este catálogo (no se conecta a nada): la gente encuentra una
extensión en el sitio, baja su `.zip` y la instala (**Extensiones → Gestionar extensiones… → Instalar desde un
archivo…**).

## Agregar tu extensión

1. Su código en un repositorio público, y una publicación (release) con su `.zip` (el flujo de la plantilla la arma:
   [extension-template](https://github.com/tensela/extension-template)).
2. Su archivo, hecho a partir del `.zip`:

   ```bash
   python tools/catalogue.py entry mi-extension-0.1.0.zip https://github.com/tu-usuario/mi-extension/releases/download/v0.1.0/mi-extension-0.1.0.zip > extensions/mi-extension.json
   ```

   Copia lo que dice su ficha (nombres, descripciones, permisos y para qué, enlaces) y calcula su huella (SHA-256).
   Léelo: lo que dice es lo que muestra el sitio.
3. Un pull request con ese archivo. La revisión automática corre sola (`tools/catalogue.py check --download`: el
   `.zip` es el que dice su huella, y su ficha coincide con su archivo). Después lo revisa una persona.

## Qué se revisa

- **Su código es público**, y el `.zip` tiene lo que dice ese código.
- **Sus permisos tienen sentido** para lo que hace, y cada uno dice para qué con palabras que una persona entiende.
  Internet, archivos fuera del proyecto, otros programas y hablar con otros programas de la computadora se piden en
  su ficha; una que hace algo que no pide no entra.
- **Nada escondido**: nada de código que se baja mientras corre, nada que mande datos de la persona a ningún lado sin
  decirlo, nada ofuscado.
- **Su ficha está completa**: un nombre, qué hace, quién la hace, su licencia, dónde está su código y dónde reportar
  un problema.

Los problemas de una extensión se reportan donde dice su archivo (`issues`), no aquí.

## Actualizarla

Una publicación nueva, y un pull request que cambie `version`, `download`, `sha256` y `updated` en su archivo (o que
lo vuelva a hacer con `tools/catalogue.py entry`).

## Para el sitio

`python tools/catalogue.py build catalogue.json` los junta en un solo archivo; el sitio lo lee al construirse.
