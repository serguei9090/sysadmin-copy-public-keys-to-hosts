# Manual de Script de Copia de Llaves Públicas SSH

Este es un script de Python diseñado para copiar llaves públicas SSH a múltiples hosts de forma automática. A continuación, se detallan los pasos para utilizar el script:

1. **Requisitos previos**

- Tener instalado Python 3.6 o superior en tu sistema.
- Tener instalado el paquete `sshpass` en tu sistema. Puedes instalarlo en Debian/Ubuntu ejecutando el siguiente comando:

2. **Preparar las llaves públicas SSH**

- Crea una carpeta llamada `ssh_pub` en la misma ubicación donde se encuentra el archivo del script.
- Coloca todas las llaves públicas SSH que deseas copiar en la carpeta `ssh_pub`. Asegúrate de que todas las llaves tengan la extensión `.pub`.

3. **Preparar el archivo de usuarios y contraseñas**

- Crea un archivo llamado `users` en la misma ubicación donde se encuentra el archivo del script.
- En cada línea del archivo, escribe un usuario y una contraseña separados por dos puntos (`:`). Por ejemplo:

`usuario1:contraseña1` \
`usuario2:contraseña2`

4. **Dar permisos de ejecución al archivo del script**

- Abre una terminal y navega a la ubicación donde se encuentra el archivo del script.
- Ejecuta el siguiente comando para dar permisos de ejecución al archivo:

5. **Ejecutar el script**

- Abre una terminal y navega a la ubicación donde se encuentra el archivo del script.
- Ejecuta el archivo utilizando el siguiente comando:

- El script te pedirá que ingreses un rango de direcciones IP (desde y hasta). Ingresa el rango de direcciones IP que deseas incluir.
- El script buscará todas las llaves públicas SSH que se encuentran en la carpeta `ssh_pub`, y las copiará a cada host en el rango de direcciones IP especificado, utilizando cada usuario y contraseña del archivo `users`.
- El script mostrará un mensaje de resumen al final, indicando el número total de intentos de autenticación y el número de autenticaciones exitosas.

Siguiendo estos pasos, podrás utilizar el script de copia de llaves públicas SSH en tu sistema Linux. Recuerda que es importante tener cuidado al proporcionar contraseñas en el archivo `users` y al ejecutar el script en un rango de direcciones IP, ya que esto podría comprometer la seguridad de tus sistemas.
