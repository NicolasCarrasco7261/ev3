# Revision de seguridad

## Alcance

Se reviso la aplicacion Flask definida en `vulnerable.py` y el pipeline de Jenkins usado para ejecutar validaciones continuas durante el ciclo de vida de desarrollo.

## Revisiones continuas realizadas

| Etapa | Revision | Herramienta o tecnica | Evidencia |
| --- | --- | --- | --- |
| Desarrollo | Revision manual del codigo | Analisis de `vulnerable.py` | Se identifico reflejo directo de entrada del usuario y ejecucion con modo debug. |
| Build | Instalacion controlada de dependencias | `pip install -r requirements.txt` o `.ci-requirements.txt` | El pipeline prepara un entorno virtual antes de probar la app. |
| Test | Pruebas automatizadas de seguridad | `pytest` | `test_vulnerable.py` valida escape de entrada y cabeceras de seguridad. |
| Analisis estatico | Revision de calidad y posibles issues | SonarQube | Stage `Analyze` del `Jenkinsfile`. |
| SCA | Revision de dependencias vulnerables | OWASP Dependency-Check en Docker | Stage `OWASP Dependency-Check`, con reportes en `dependency-check-report/`. |
| DAST | Revision dinamica de la app publicada | OWASP ZAP Baseline en Docker | Stage `OWASP ZAP`, con reportes en `zap-report/`. |

## Vulnerabilidades identificadas y mitigaciones

| Vulnerabilidad | Riesgo | Archivo | Correccion aplicada | Mitigacion |
| --- | --- | --- | --- | --- |
| Cross-Site Scripting reflejado | Un atacante podia enviar HTML o JavaScript en `name` y lograr que la respuesta lo reflejara sin escape. | `vulnerable.py` | Se usa `markupsafe.escape()` sobre el parametro `name`. | La entrada se codifica antes de construir la respuesta, por lo que etiquetas como `<script>` se devuelven como texto seguro. |
| Modo debug habilitado | Si la app se ejecutaba directamente, Flask arrancaba con `debug=True`, exponiendo informacion sensible y herramientas de depuracion. | `vulnerable.py` | Se cambio `app.run(debug=True)` por `app.run(debug=False)`. | La app ya no expone el debugger interactivo en ejecuciones directas. |
| Falta de cabeceras de seguridad | La respuesta HTTP no definia politicas basicas contra clickjacking, sniffing, permisos del navegador, cache y carga de contenido. | `vulnerable.py` | Se agrego un hook `after_request` con cabeceras de seguridad. | Se reduce la superficie frente a clickjacking, sniffing MIME, filtrado por referer, cache local y uso de APIs del navegador. |

## Pruebas agregadas

Se agrego `test_vulnerable.py` con los siguientes controles:

- Verifica que `/hello?name=CI` responda correctamente.
- Verifica que una carga como `<script>alert(1)</script>` no se refleje como HTML ejecutable.
- Verifica que las cabeceras de seguridad esten presentes en cada respuesta.

## Resultado esperado

Luego de estos cambios, el pipeline debe ejecutar pruebas unitarias, analisis estatico, revision de dependencias y escaneo dinamico. Los reportes generados por Dependency-Check y ZAP quedan archivados por Jenkins para demostrar las revisiones realizadas.
