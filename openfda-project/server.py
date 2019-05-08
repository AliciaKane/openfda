import http.server
import socketserver
socketserver.TCPServer.allow_reuse_address = True
import requests
import http.client
import json
IP = "127.0.0.1"
PORT = 8000


class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def imprimir_pantalla(self, lista):

        imprimir_lista_completa = """
                        <html>
                            <head>
                                <title>Buscador OpenFDA</title>
                            </head>
                            <body>
                                <ul>
                                  """
        for i in lista:
            imprimir_lista_completa += "<li>" + i + "</li>"

        imprimir_lista_completa += """
                                </ul>
                            </body>
                        </html>
                                """
        return imprimir_lista_completa

    def do_GET(self):
        path_split = self.path.split('?')
        url = path_split[0] #/searchDrug

        if url == "/":
            formulario = """
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Buscador OpenFDA</title>
                    </head>
                <body>

                <h2>Bienvenido al buscador de OpenFDA</h2>
                Este formulario, le permitira buscar medicamentos por su ingrediente activo
                principal, las empresas proveedoras de los medicamentos y obtener una lista tanto de
                los medicamentos como de las empresas.

                <br>

                <h3>Buscador de medicamentos por <em>ingrediente activo</em>:</h3>
                <form action="searchDrug" method="get">
                Introduzca el componente activo del medicamento:
                <input type="text" name="active_ingredient" placeholder="Active ingredient">
                <input type="text" name="limit" placeholder="Limite">
                <br>
                <br>
                <input type="submit" value="Enviar Formulario">
                </form>

                <br>

                <h3>Buscador de <em>empresa proveedora</em>:</h3>
                <form action="searchCompany" method="get">
                Introduzca la empresa deseada:
                <input type="text" name="company" placeholder="Company">
                <input type="text" name="limit" placeholder="Limite">
                <br>
                <br>
                <input type="submit" value="Enviar Formulario">
                </form>

                <br>

                <h3>Lista de medicamentos:</h3>
                <form action="listDrugs" method="get">
                <input type="text" name="limit" placeholder="Limite">
                <input type="submit" value="Enviar Formulario">
                </form>

                <br>

                <h3>Lista de empresas:</h3>
                <form action="listCompanies" method="get">
                <input type="text" name="limit" placeholder="Limite">
                <input type="submit" value="Enviar Formulario">
                </form>

                <br>

                <h3>Lista de advertencias:</h3>
                <form action="listWarnings" method="get">
                <input type="text" name="limit" placeholder="Limite">
                <input type="submit" value="Enviar Formulario">
                </form>

                </body>
                </html>
                """

            # Send headers
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(bytes(formulario, "utf8"))
            print("File served!")
            return


        elif 'searchDrug' in self.path:

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            #Cojo el ingrediente activo introducido por el cliente (supuestamente)
            dato_metido = self.path.split("?") #lo he separado por el "?"
            dato_metido = dato_metido[1].split("&")  # separo por un lado <active_ingredient> y por otro <active_ingredient=aspirin & limit=10>
            ingrediente_activo_requerido = dato_metido[0].split("=") # separo active_ingredient de aspirin
            ingrediente_activo_requerido = ingrediente_activo_requerido[1] #saco aspirin

            try:
                limite = dato_metido[1].split("=") # separo limit de 10
                if limite[1] == "": # si no existe limit
                    limite = "&limit=10"
                else:
                    limite = "&limit="+limite[1] # si existe, saco su valor
            except IndexError:
                limite = "&limit=10"

            #Intetamos conectar
            url_searchedrug = str("https://api.fda.gov/drug/label.json?search=active_ingredient:"+ingrediente_activo_requerido+"=")+str(limite)
            #he puesto un string se url_searchcompany, porque sino no iba,
            #no entiendo muy bien el por qu?...
            conexion = requests.get(url_searchedrug)
            enlace_final = conexion.json()

            #print("Enlace final", enlace_final)

            lista_drogas = []
            try:
                for resultado in enlace_final['results']:

                    if ('generic_name' in resultado['openfda']):
                        lista_drogas.append(resultado['openfda']['generic_name'][0])

                    else:
                        lista_drogas.append('Nombre de medicamento no encontrado.')
            except KeyError:
                lista_drogas.append('Nombre erroneo.')

            respuesta_openFDA = self.imprimir_pantalla(lista_drogas)
            self.wfile.write(bytes(respuesta_openFDA, "utf8"))
            print("File served!")
            return

        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            #Cojo el ingrediente activo introducido por el cliente (supuestamente)
            dato_metido = self.path.split("?") #lo he separado por el "?"
            dato_metido = dato_metido[1].split("&")  # separo por un lado <active_ingredient> y por otro <active_ingredient=aspirin & limit=10>
            empresa_requerida = dato_metido[0].split("=") # separo active_ingredient de aspirin
            empresa_requerida = empresa_requerida[1] #saco aspirin

            try:
                limite = dato_metido[1].split("=") # separo limit de 10
                if limite[1] == "": # si no existe limit
                    limite = "&limit=10"
                else:
                    limite = "&limit="+limite[1] # si existe, saco su valor
            except IndexError:
                limite = "&limit=10"

            #Intetamos conectar
            url_searchcompany = str("https://api.fda.gov/drug/label.json?search=openfda.manufacturer_name:"+empresa_requerida+"=")+str(limite)
            #he puesto un string se url_searchcompany, porque sino no iba,
            #no entiendo muy bien el por qu?...
            conexion = requests.get(url_searchcompany)
            enlace_final = conexion.json()

            #print("Enlace final", enlace_final)

            lista_empresas = []
            try:
                for resultado in enlace_final['results']:

                    if ('manufacturer_name' in resultado['openfda']):
                        lista_empresas.append(resultado['openfda']['manufacturer_name'][0])
                    else:
                        lista_empresas.append('Desconocida')
            except KeyError:
                lista_empresas.append('Nombre erroneo.')

            respuesta_openFDA = self.imprimir_pantalla(lista_empresas)
            self.wfile.write(bytes(respuesta_openFDA, "utf8"))
            print("File served!")
            return

        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            #Cojo el ingrediente activo introducido por el cliente (supuestamente)
            dato_metido = self.path.split("=") #lo he separado por el "="
            limit = dato_metido[1]

            #Intetamos conectar
            url_listadrugs = str("https://api.fda.gov/drug/ndc.json?count=generic_name.exact&limit="+limit)
            #he puesto un string se url_listadrugs
            conexion = requests.get(url_listadrugs)
            enlace_final = conexion.json()

            #print("Enlace final", enlace_final)

            lista_drugs = []
            try:
                for resultado in enlace_final['results']:
                    if ('term' in resultado):
                        lista_drugs.append(resultado['term'])
                    else:
                        lista_empresas.append('Desconocida')
            except KeyError:
                lista_drugs.append('Nombre erroneo.')

            respuesta_openFDA = self.imprimir_pantalla(lista_drugs)
            self.wfile.write(bytes(respuesta_openFDA, "utf8"))
            print("File served!")
            return

        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            #Cojo el ingrediente activo introducido por el cliente (supuestamente)
            dato_metido = self.path.split("=") #lo he separado por el "="
            limit = dato_metido[1]

            #Intetamos conectar
            url_listacompany = str("https://api.fda.gov/drug/ndc.json?count=openfda.manufacturer_name.exact&limit="+limit)
            #he puesto un string se url_listacompany
            conexion = requests.get(url_listacompany)
            enlace_final = conexion.json()

            #print("Enlace final", enlace_final)

            lista_empresas = []
            try:
                for resultado in enlace_final['results']:
                    if ('term' in resultado):
                        lista_empresas.append(resultado['term'])
                    else:
                        lista_empresas.append('Desconocida')
            except KeyError:
                lista_empresas.append('Nombre erroneo.')

            respuesta_openFDA = self.imprimir_pantalla(lista_empresas)
            self.wfile.write(bytes(respuesta_openFDA, "utf8"))
            print("File served!")
            return

        elif 'listWarnings' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            #Cojo el ingrediente activo introducido por el cliente (supuestamente)
            dato_metido = self.path.split("=") #lo he separado por el "="
            limit = dato_metido[1]

            #Intetamos conectar
            url_listacompany = str("https://api.fda.gov/drug/label.json?limit="+limit)
            #he puesto un string se url_listacompany
            conexion = requests.get(url_listacompany)
            enlace_final = conexion.json()

            #print("Enlace final", enlace_final)

            lista_empresas = []
            try:
                for resultado in enlace_final['results']:
                    if ('warnings' in resultado):
                        lista_empresas.append(resultado['warnings'][0])
                    else:
                        lista_empresas.append('Desconocida')
            except KeyError:
                lista_empresas.append('Nombre erroneo.')

            respuesta_openFDA = self.imprimir_pantalla(lista_empresas)
            self.wfile.write(bytes(respuesta_openFDA, "utf8"))
            print("File served!")
            return

        elif 'secret' in self.path:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm= "blabla"')
            self.end_headers()
            return

        elif 'redirect' in self.path:
            self.send_response(302)
            self.send_header('Location', 'http://127.0.0.1:8000/')
            self.end_headers()
            return

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error = """El recurso solicitado no existe"""
            self.wfile.write(bytes(error, "utf8"))
            print("File served!")
            return




Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
        pass

httpd.server_close()
print("")
print("Server stopped!")
