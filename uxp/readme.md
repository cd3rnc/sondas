
## Repositio codigo sonda UXP


### Como usar este repositorio

1. Clonar este repositorio a una ubicación local
2. Para crear un nuevo test que hará la sonda, desarrollar el codigo en un nuevo archivo .py ubicado en el directorio `plugins`. La estructura del nombre del archivo debe ser `{test}_plugin.py`, donde `{test}` es el nombre del test que realizará el plugin. Ejemplo: `mtr_plugin.py`. 
3. En el archivo mtr_plugin.py instanciar la clase `TestPlugin` usando base_plugin.py

    ```sh
    from plugins.base_plugin import TestPlugin
    ...

    class MTRTest(TestPlugin):

    ```
4. Cualquier configuración que el plugin use internamente, debe ser creada en en el mismo directorio `plugins` con el mismo nombre del archivo .py. Ejemplo: `mtr_plugin.yaml`
5. Cualquier libreria adicional agregar a `requirements.txt`
6. Para probar el test (se recomienda usar venv):

    ```sh
    ./main.py mtrtest
    ```
6. Revisar `ping_plugin.py` como ejemplo básico
7. Para programar la ejecución del test, editar el archivo `sonda.cron`
8. Construir y desplegar la imagen

### Para construir la imagen de la sonda 

La imagen de la sonda se puede construir en cualquier host que tenga acceso a la red `zero-tier` y a este repositorio.

Como ejemplo usaremos `zt-master-01`, usando el usuario `soporte`.

En `/home/soporte/uxp` ya existe un clone de este repositorio por lo que debe actualizarse a su ultima version para que refleje los ultimos cambios.

1. Actualizar el repositorio git (esto deshace cualquier cambio local!)

    ```sh
    git fetch --all
    git reset --hard origin/main
    ```

2. Luego se construye la imagen docker en zt-master-01 y se publica al Registry:

    En zt-master-01 ya existe el builder (buildx) llamado uxpbuilder, se creó asi:

    ```sh
    docker buildx create --name uxpbuilder --driver docker-container --config ./buildkitd.toml --use
    ```
    `buildkitd.toml` permite usar el registry sin validar el certificado (o insecure)
    
    La imagen multi-arch se crea asi:
    ```sh
    docker buildx build --platform linux/amd64,linux/arm64/v8 --no-cache -t 172.30.236.20:5000/gss/sonda:last . --push
    ```

    Generar la imagen multi-arch nos permite hacer pruebas en un Linux x86_64 sin necesidad de hacer configuración particular en el archivo `docker-compose.yaml` que levanta la sonda.
    

3. Para desplegar esta imagen se usa ansible desde la carpeta `/home/soporte/ansible` del host `zt-master-01`.
4. Dentro del directorio `inventory` actualizar el inventario desde zerotier usando:

    ```sh
    ./inventory.py > upx.yaml
    ```

5. Teniendo el inventario actualizado, procedemos a cambiar el hostname de la sonda (para que refleje el de zerotier). Esto reiniciará la sonda.

    ```sh
    ansible-playbook -i inventory/upx.yaml update_hostname.yaml --limit 86d1047954
    ```
    En este ejemplo limitamos la ejecución playbook solo a la sonda 86d1047954

6. Posterior al cambio de hostname desplegamos la sonda con el comando:

   ```sh
    ansible-playbook -i inventory/upx.yaml deploy_upx.yaml --limit 86d1047954
    ```
7. Se puede verificar con:

   ```sh
    ansible 86d1047954 -i inventory/upx.yaml -a "docker ps"
   ```

###

