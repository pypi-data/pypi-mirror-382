# `Opload`: Open Loading Server

## Local installation

You should be able to clone this repo and install the package:
```
$ pip install -e opload
```

For local testing, be sure to set the following env.variables: 
* `OPLOAD_BACKEND_SERVICE=STDLIB`

To facilitate endpoint calling while developing, you may also want to set `FRD_RESTAPI_DISABLE_AUTH=1`.

Start the server:
```
$ fred serve --classname RouterCatalog --classpath opload.router.catalog
```
* Or just `fred serve` if the env.variables are correctly set.
* Or use the direct `opload serve` command. 


A key that doesn't exist will return a `null` value (i.e., `"val":null`):

```
$ curl --request GET http://0.0.0.0:8000/get?key=demo/1.txt
```

You can define the holding value of a key via the `set` endpoint:

```
$ curl --request POST http://0.0.0.0:8000/set --data '
{
  "key": "demo/1.txt",
  "value": "Hello, world."
}
'
```