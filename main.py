#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import argparse #do pobierania parametrów
import tkinter
from tkinter import messagebox

# ukrywa wyskakujące okenko
root = tkinter.Tk()
root.withdraw()


# Generuj token (client credentials)
def post_generate_token(host,client_id,client_secret):

#print(f'client_id: {client_id} client_secret: {client_secret}')

    url = f'https://{host}/oauth2/token'

    query = {
        'grant_type': 'client_credentials',
        'client_id': f'{client_id}',
        'client_secret': f'{client_secret}'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(
            url,
            #headers
            headers=headers,
            #body
            data=query
         )
    except requests.exceptions.RequestException as e:
        messagebox.showerror(title="ConnectionError", message=SystemExit(e))
        raise SystemExit(e)



    jsonResponse = response.json()

    if response.status_code == 200:
        return (jsonResponse["access_token"])
    elif response.status_code == 400:
        print('Error 400: '+jsonResponse["error_description"])
        messagebox.showerror(title="post_generate_token", message='Error 400: '+jsonResponse["error_description"])
        exit()
    else:
        print('Error '+response.status_code+': ' + jsonResponse["error_description"])
        messagebox.showerror(title="post_generate_token", message='Error '+response.status_code+': ' + jsonResponse["error_description"])
        exit()

#Kolejka komunikatów oczekujących
def get_messages_queue(host,access_token):


    url = f'https://{host}/api/v1/events-queue/messages'
    #print(f'host: {url}')

    headers = {'accept': 'application/json',
               'Authorization': f'Bearer {access_token}'
               }
    try:
        response = requests.get(
            url,
            # headers
            headers=headers

        )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)



    if response.status_code == 204:
        print("Brak komunikatów w kolejce")
        return '204','',''
    if response.status_code == 200:

        jsonResponse = response.json()
        print ("Pierwszy komunikat oczekujący w kolejce")

        #Komunikat informujący o błędzie w procesie wysyłania dokumentu
        try:
            if  jsonResponse["sentDocumentErrorMessage"]:
                documentId = jsonResponse["sentDocumentErrorMessage"]["documentId"]
                messageId = jsonResponse["sentDocumentErrorMessage"]["messageId"]
                errorCode = jsonResponse["sentDocumentErrorMessage"]["errors"]

                print(f'sentDocumentErrorMessage|{documentId}|{messageId}|{errorCode}')
                return '200', messageId, errorCode
        except:
            pass
        #Komunikat informujący o zmianie statusu wysłanego dokumentu.
        try:
            if jsonResponse["sentDocumentStatusChangedMessage"]:
                documentId = jsonResponse["sentDocumentStatusChangedMessage"]["documentId"]
                messageId = jsonResponse["sentDocumentStatusChangedMessage"]["messageId"]
                status = jsonResponse["sentDocumentStatusChangedMessage"]["status"]

                print(f'sentDocumentStatusChangedMessage|{documentId}|{messageId}|{status}')
                return '200', messageId,documentId
        except:
            pass
        try:

            #Komunikat informujący o zmianie statusu odebranego dokumentu. Komunikat zostanie wygerowany jeśli status dokumentu został zminiony za pomocą innego kanału (aplikacji WEB lub aplikacji desktop).
            if jsonResponse["receivedDocumentStatusChangedMessage"]:
                documentId = jsonResponse["receivedDocumentStatusChangedMessage"]["documentId"]
                messageId = jsonResponse["receivedDocumentStatusChangedMessage"]["messageId"]
                status = jsonResponse["receivedDocumentStatusChangedMessage"]["status"]

                print(f'receivedDocumentStatusChangedMessage|{documentId}|{messageId}|{status}')
                return '200', messageId,documentId
        except:
            pass

        try:
            #Komunikat informujący o otrzymaniu dokumentu. Treść dokumentu można pobrać za pomocą operacji getDocumentContent().
            if jsonResponse["documentReceivedMessage"]:
                documentId = jsonResponse["documentReceivedMessage"]["documentId"]
                messageId = jsonResponse["documentReceivedMessage"]["messageId"]
                documentType = jsonResponse["documentReceivedMessage"]["documentType"]
                #Raport z kontroli biznesowej
                reportDate = jsonResponse["documentReceivedMessage"]["businessValidationReport"]["reportDate"]
                warnings = jsonResponse["documentReceivedMessage"]["businessValidationReport"]["reportDate"]
                print(f'documentReceivedMessage|{documentId}|{messageId}|{documentType}|{reportDate}|{warnings}')
                return '200', messageId,documentId
        except:
            pass


        try:
            #Komunikat informujący, że ze skrzynki obsługiwanej przez ten system, wysłano dokument innym kanałem (z aplikacji WEB lub aplikacji desktop). Treść dokumentu można pobrać za pomocą operacji getDocumentContent().
            if jsonResponse["documentSentFromOtherSourceMessage"]:
                documentId = jsonResponse["documentSentFromOtherSourceMessage"]["documentId"]
                messageId = jsonResponse["documentSentFromOtherSourceMessage"]["messageId"]
                documentType = jsonResponse["documentSentFromOtherSourceMessage"]["documentType"]

                print(f'documentReceivedMessage|{documentId}|{messageId}|{documentType}')
                return '200', messageId,documentId
        except:
            pass



    if response.status_code == 401:
        jsonResponse = response.json()
        print("Błąd uwierzytelnienia")
        print (jsonResponse["description"])
        return '401','',''
    if response.status_code == 403:
        jsonResponse = response.json()
        print("Błąd autoryzacji")
        print (jsonResponse["description"])
        return '403','',''
    if response.status_code == 500:
        jsonResponse = response.json()
        print("Błąd wewnętrzny serwera")
        print (jsonResponse["errorId"]+' '+jsonResponse["description"])

        messagebox.showerror(title="get_messages_queue",message='Error ' + response.status_code + ': Błąd wewnętrzny serwera')

        return '500','',''

#Potwierdzenie odebrania komunikatu.
def delete_messages_queue(host,access_token,messageId):


    url = f'https://{host}/api/v1/events-queue/messages/{messageId}'
    #print(f'host: {url}')

    headers = {'accept': '*/*',
               'Authorization': f'Bearer {access_token}'
               }

    try:
        response = requests.delete(
            url,
            # headers
            headers=headers

        )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


    if response.status_code == 204:
        print("Przyjęto potwierdzenie odebrania komunikatu delete_messages_queue")
        return ('204')
    if response.status_code == 401:
        jsonResponse = response.json()
        print("Błąd uwierzytelnienia")
        print (jsonResponse["description"])
        return ('401')
    if response.status_code == 403:
        jsonResponse = response.json()
        print("Błąd autoryzacji")
        print (jsonResponse["description"])
        return ('403')
    if response.status_code == 404:
        jsonResponse = response.json()
        print("Błędne messageId. kolejka komunikatów jest pusta lub pierwszy oczekujący komunikat ma inny identyfikator")
        print (jsonResponse["description"])
        return ('403')
    if response.status_code == 500:
        jsonResponse = response.json()
        print("Błąd wewnętrzny serwera")
        print (jsonResponse["description"])
        messagebox.showerror(title="delete_messages_queue",message='Error ' + response.status_code + ': Błąd wewnętrzny serwera')
        return ('500')

#Pobranie treści dokumentu
#Operacja pozwala pobrać treść (w formacie Ubl) dokumentu odbieranego lub wysyłanego z innego źródła. Treść dokumentu jest dostępna przez 7 dni od czasu odebrania komunikatu o nowym dokumencie. Typ dokumentu powinien zostać przekazny w nagłówku X-PEF-DocumentType.
def get_documents_content(host,access_token,documentId,documentType,path_file):


    url = f'https://{host}/api/v1/documents/{documentId}/content'
    #print(f'host: {url}')

    headers = {'accept': 'application/xml',
               'Authorization': f'Bearer {access_token}',
               'X-PEF-DocumentType': f'{documentType}'
               }

    try:
        response = requests.get(
            url,
            # headers
            headers=headers

        )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)



    if response.status_code == 200:
        print("Treść dokumentu")
        print(response.text)
        f = open(path_file, "wb")
        f.write(response.text.encode())
        f.close()
        return ('200')

    if response.status_code == 401:
        jsonResponse = response.json()
        print("Błąd uwierzytelnienia")
        print (jsonResponse["description"])
        return ('401')
    if response.status_code == 403:
        jsonResponse = response.json()
        print("Błąd autoryzacji")
        print (jsonResponse["description"])
        return ('403')
    if response.status_code == 404:
        jsonResponse = response.json()
        print("Brak dokumentu o podanym identyfikatorze")
        print ('404|'+jsonResponse["description"])
        return ('404')
    if response.status_code == 500:
        jsonResponse = response.json()
        print("Błąd wewnętrzny serwera")
        print (jsonResponse["description"])
        messagebox.showerror(title="delete_messages_queue",message='Error ' + response.status_code + ': Błąd wewnętrzny serwera')
        return('500')
#Operacja umożliwia przekazanie dokumentu do Sytemu PEF.

def post_send_document(host,access_token,documentType,path_file):


    f = open(path_file, encoding="utf8")

    file_content = f.read()


    url = f'https://{host}/api/v1/documents'
    #print(f'host: {url}')

    headers = {'accept': 'application/json',
               'Content-Type': 'application/xml',
               'Authorization': f'Bearer {access_token}',
               'X-PEF-DocumentFormat': 'Ubl',
               'X-PEF-DocumentType': f'{documentType}'
               }

    try:
        response = requests.post(
            url,
            # headers
            headers=headers,
            data=file_content
        )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    jsonResponse = response.json()

    if response.status_code == 202:

        print("Unikalny identyfikator oraz aktualny status dokumentu")
        print('DocumentSend|'+jsonResponse["documentId"]+'|'+jsonResponse["status"])
        return ('202')
    if response.status_code == 400:
        print("Błędna treść żądania.")
        print (jsonResponse["errors"])
        return ('400')
    if response.status_code == 401:
        print("Błąd uwierzytelnienia")
        print (jsonResponse["description"])
        return ('401')
    if response.status_code == 403:
        print("Błąd autoryzacji")
        print (jsonResponse["description"])
        return ('403')
    if response.status_code == 404:
        print("Brak dokumentu o podanym identyfikatorze")
        print (jsonResponse["description"])
        return ('403')
    if response.status_code == 500:
        print("Błąd wewnętrzny serwera")
        print (jsonResponse["description"])
        messagebox.showerror(title="delete_messages_queue",message='Error ' + response.status_code + ': Błąd wewnętrzny serwera')
        return ('500')




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('parametr1', help='client_id') #pobiera id clienta
    parser.add_argument('parametr2', help='client_secret')#pobiera sekretny klucz
    parser.add_argument('parametr3', help='documentType') # pobiera jaki dokument się zaczytuje CREDIT_NOTE, DESPATCH_ADVICE, INVOICE, INVOICE_CORRECTION, ORDER, RECEIPT_ADVICE
    parser.add_argument('parametr4', help='documentReceivedMessagepath_file') # sciezka do zapisywania/odczytywania pliku
    parser.add_argument('parametr5', help='post_send_document') #flaga T/N do wysłania pliku
    parser.add_argument('parametr6', help='get_messages_queue') #flaga T/N do zaczytywania kolejki
    parser.add_argument('parametr7', help='delete_messages_queue')  # flaga T/N do czyszczenia kolejki
    parser.add_argument('parametr8', help='get_documents_content')  # flaga ID_dokumentu/N do odczytania xmla, dokumentu o podanym id dokumentu

    args = parser.parse_args()
    #args.parametr2 #odwołanie sie do parametru

    host = 'api-int-integrator.lab.brokerinfinite.efaktura.gov.pl'
    client_id = args.parametr1
    client_secret = args.parametr2
    documentType = args.parametr3
    path_file = args.parametr4

    access_token = post_generate_token(host,client_id,client_secret)
    #print (access_token)

    if args.parametr5 == 'T':
        post_send_document(host, access_token, documentType, path_file)

    if args.parametr6 == 'T':
        messages_queue = '0'
        # przepytywanie kolejki
        while messages_queue != '204':
            messages_queue , messageId, documentId  = get_messages_queue(host, access_token)
            #print ('aaaa'+messages_queue)

            #ustawienie flagi na N powoduje przerwanie while
            if args.parametr7 == 'N':
                messages_queue = '204'

            # usuwanie danych z kolejki
            if messages_queue == '200' and args.parametr7 == 'T':
                #print ('delete_messages_queue')
                delete_messages_queue(host,access_token,messageId)

    if args.parametr8 != 'N':
        # dodoać pod parametr documentId
        documentId = args.parametr7
        get_documents_content(host, access_token, documentId, documentType, path_file)