import io


class Convert2PDF():
    #curl --request POST https://utils-api.sasabz.it/forms/libreoffice/convert --form files=@test.docx -o test.pdf

    @classmethod
    def convert2pdf(self, fname: str,  io_file: io.BytesIO):
        import requests
        response = requests.post('http://gotenberg:3000/forms/libreoffice/convert',
                                 files={fname: io_file.read()})
        print(response.status_code)
        return response.content