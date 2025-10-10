# sysnet-pyutils

SYSNET Python Utilities

Knihovna obsahuje základní, v aplikacích hojně používané, utility.

## sysnet-pyutils.utils

Hlavní modul

### Třídy

* **Singleton**: Vzor všech singletonů. 

        class ConfigFlag(object, metaclass=Singleton):

* **ConfigFlag**: Pomocný singleton. Používá se pro inicializaci konfigurace.
* **Config**: Singleton konfigurace aplikace. Konfigurace se ukládá do souboru YAML.

        from sysnet_pyutils import utils as pu
        ...
        CC = pu.Config(config_path=CONFIG_FILE_PATH, config_dict=CONFIG_INIT)
        if CC.loaded:
            LOG.logger.info("CONFIG loaded")
        CONFIG = CC.config    # konfigurační dictionary

* **ConfigError**: Chyba konfigurace
* **Log**: Logovací singleton. Centralizuje logování v aplikaci. Umožňuje použití externího loggeru (např. pro Django nebo Flask)
* **LoggedObject**: Třída s vnitřním logováním. Vhodné pro singletony typu factory. 

### Funkce
----------------------------------------------------------------
#### api_key_generate(length: int):
Vygeneruje API klíč
* param length: Dělka API klíče
* return: API Key
----------------------------------------------------------------
#### api_key_next(name, length=16):
Vygeneruje slovník API key {API Key: name}
* param name:    Název API klíče
* param length:  Délka API klíče
* return: Slovník {API Key: name}
----------------------------------------------------------------
#### api_keys_init(agenda='main', amount=4):
Vygeneruje klíče pro API
* param agenda: Název agendy, pro kterou se klíče generují
* param amount: Počet vygenerovaných klíčů
* return: seznam vygenerovaných klíčů
--------------------------------------------------------
#### convert_hex_to_int(id_hex):
Konvertuje hex string na int
* param id_hex:  Hexadecimální string
* return: int
--------------------------------------------------------
#### cron_to_dict(cron):
Konvertuje cron text do slovníku
* param cron: cron text (například '35 21 * * *')
* return: dict of cron
--------------------------------------------------------
#### cs_bool(value=None):
Vrátí českou textovou hodnotu 'ano'/'ne' pokud je bool(value) True/False
* param value: Obecný objekt
* return: 'ano' or 'ne'
--------------------------------------------------------
#### date_to_datetime(date_value):
Konvertuje date na datetime v lokální časové zóně
* param date_value:  hodnota  
* return: hodnota date v lokální časové zóně
--------------------------------------------------------
#### decode_b64_string(b64_data: str, encoding='utf-8'):
Dekóduje base64 data na string
* param b64_data: data v base64 
* param encoding: kódování
* return:
--------------------------------------------------------
#### decode_b64_to_file(b64_data: str, filepath, encoding='utf-8'):
Uloží base64 data do souboru
* param b64_data: data v base64 
* param filepath: cesta k cílovému souboru
* param encoding: kódování
* return: cesta k cílovému souboru
--------------------------------------------------------
#### encode_file_b64(filepath, encoding='utf-8'):
Načte soubor do base64
* param filepath: cesta ke zdrojovému souboru
* param encoding: kódování
* return: data base64
--------------------------------------------------------
#### encode_string_b64(data: str, encoding='utf-8'):
Zakóduje string do base64
* param data: zdrojový text
* param encoding: kódování
* return: výstupní data base64
---------------------------------------------------------------- 
#### hash_md5(text):
Vytvoří md5 checksum ze zdrojového textu (zastaralé, nepoužívat)
* param text: zdrojový text 
* return: výstupní hash
--------------------------------------------------------
#### hash_sha1(text):
Vytvoří sha1 checksum ze zdrojového textu
* param text: zdrojový text 
* return: výstupní hash
--------------------------------------------------------
#### hash_sha256(text):
Vytvoří sha256 checksum ze zdrojového textu
* param text: zdrojový text 
* return: výstupní hash
--------------------------------------------------------
#### hash_sha383(text):
Vytvoří sha383 checksum ze zdrojového textu
* param text: zdrojový text 
* return: výstupní hash
----------------------------------------------------------------
#### id12_next(three_char_prefix=None):
Vygeneruje korektní 12místný alfanumerický identifikátor s pevným prefixem
* param three_char_prefix: Tříznakový prefix identifikátoru
* return: 12místný alfanumerický identifikátor
----------------------------------------------------------------
#### increment_date(date_str=None, days=1):
Inkrementuje datum v textovém formátu ISO o daný počet dní
* param date_str:    ISO datum v textovém formátu ISO
* param days: počet dní
* return:        ISO datum v textovém formátu ISO
----------------------------------------------------------------
#### is_base64(body):
Kontrola, zda jsou data kódována base64
* param body: Vstupní data (str, bytes) 
* return: True/False
----------------------------------------------------------------
#### is_valid_ico(ico):
Kontrola validity IČO
* param ico: IČO
* return: True/False
----------------------------------------------------------------
#### is_valid_pid(value):
Kontrola textové validity PID
* param value: PID 
* return: True/False
----------------------------------------------------------------
#### is_valid_uuid(value):
Kontrola validity uuid
* param value: uuid
* return: True/False
----------------------------------------------------------------
#### iso_to_local_datetime(isodate):
ISO string datum do lokálního datetime
* param isodate: Textové datum v ISO
* return: lokální datetime
----------------------------------------------------------------    
#### pid_check(pid):
Zkontroluje korektnost PID
* param pid: Vstupní PID
* return: True/False
----------------------------------------------------------------
#### pid_correct(pid):
Opraví PID
* param pid: Vstupní PID 
* return: Opravený PID
----------------------------------------------------------------    
#### pid_next():
Vygeneruje korektní PID
* return: PID 
----------------------------------------------------------------
#### remove_empty(source_list):
Odstraní prázdné položky ze seznamu
* param source_list: zdrojový seznam
* return: cílový seznam
----------------------------------------------------------------
#### repair_ico(ico):
Opraví IČO
* param ico:  IČO 
* return: opravené IČO
----------------------------------------------------------------
#### to_base64(body):
Zajistí, aby data byla v base64
* param body: vstupní data 
* return: data v base64
----------------------------------------------------------------
#### today():
Vrací ISO 8601 text datum dnešního dne
* return:    ISO 8601 datum dnešního dne
----------------------------------------------------------------
#### tomorrow():
Vrací ISO 8601 datum zítřejšího dne
* return:    ISO 8601 datum
----------------------------------------------------------------
#### unique_list(input_list):
Vyřadí opakující se položky ze seznamu
* param input_list:   Vstupní seznam
* return: Unikátní seznam
----------------------------------------------------------------
#### url_safe(url):
Upraví URL, aby neobsahovalo nepovolené znaky
* param url: Vstupní URL
* return: Upravené URL
--------------------------------------------------------------------------------------------------------------------------------
#### uuid_next(uuid_type=4):
Vygeneruje UUID
* param uuid_type: Lze použít pouze typ 1 nebo 4 (od verze 1.0.5 implicitně 4)
* return: uuid
--------------------------------------------------------------------------------------------------------------------------------
#### who_am_i():
Vrátí název aktuální funkce
* return: název funkce, odkud je voláno  
* například:   `__name__ = who_am_i()`  
--------------------------------------------------------------------------------------------------------------------------------
### Verze 1.0.3
#### to_camel(s):
Převede text z hadí_notace do VelbloudíNotace
* param s: text v hadí notaci
* return: text ve velbloudí notaci  
--------------------------------------------------------------------------------------------------------------------------------
#### to_snake(s):
Převede text z VelbloudíNotace do hadí_notace 
* param s: text ve velbloudí notaci
* return: text v hadí notaci  
--------------------------------------------------------------------------------------------------------------------------------
#### to_camel_dict(d):
Rekurzivně převede klíče ve slovníku z hadí_notace do VelbloudíNotace
* param d: dictionary s klíči v hadí notaci
* return: dictionary s klíči ve velbloudí notaci  
--------------------------------------------------------------------------------------------------------------------------------
#### to_snake_dict(d):
Rekurzivně převede klíče ve slovníku z VelbloudíNotace do hadí_notace 
* param d: dictionary s klíči ve velbloudí notaci
* return: dictionary s klíči v hadí notaci  
--------------------------------------------------------------------------------------------------------------------------------
#### xml_to_dict(xml_text):
Parsuje XML string do XML dictionary 
podle pravidel viz https://github.com/martinblech/xmltodict
* param xml_text:    XML text
* return: XML dictionary
--------------------------------------------------------------------------------------------------------------------------------
#### dict_to_xml(xml_dict):
Parsuje XML dict do XML textu podle 
pravidel viz https://github.com/martinblech/xmltodict
* param xml_dict:    XML dictionary
* return:    XML text
--------------------------------------------------------------------------------------------------------------------------------
### verze 1.0.4
#### order_to_cites(order: int):
Konvertuje celočíselnou hodnotu na písmennou
* param order: celočíselná hodnota např. 1458
* return: znaková hodnota např. 'BDB'
--------------------------------------------------------------------------------------------------------------------------------
#### cites_to_order(cites: str):
Konvertuje písmennou hodnotu na celočíselnou
* param cites: znaková hodnota např. 'BDB' 
* return: celočíselná hodnota např. 1458
--------------------------------------------------------------------------------------------------------------------------------
### verze 1.0.5

#### local_now():
Vrací aktuální časovou značku v lokální časové zóně.
* return: datetime.datetime

#### is_valid_unid(unid):
Kontrola validity HCL Notes UNIID
* param unid: univerzální ID ke kontrole 
* return: True/False
--------------------------------------------------------------------------------------------------------------------------------

#### domino.DdsDictionaryFactory
Třída **domino.DdsDictionaryFactory** slouží pro získávání hodnot z dokumentu Notes v podobě dictionary, 
které vrací služba HCL Domino Data Service 

    dds_factory = DdsDictionaryFactory(reply)
    general_item_value = dds_factory.get_value(<general_item_name>)
    string_item_value:str = dds_factory.get_value_string(<string_item_name>)
    bool_item_value:bool = dds_factory.get_value(<bool_item_name>)
    float_item_value:float = dds_factory.get_value_float(<float_item_name>, <float_spare_item_name>)
    int_item_value:int = dds_factory.get_value_int(<int_item_name>, <int_spare, item_name>)
    datetime_item_value:datetime = dds_factory.get_value_datetime(<datetime_item_name>)
    date_item_value:date = dds_factory.get_value_date(<datetime_item_name>)
--------------------------------------------------------------------------------------------------------------------------------

#### date_to_datetime_utc(date_value):
Konvertuje datum na tatum a čas v UTC. 
Vhodné pro MongoDB pro ukládání položek typu datum.
* param date_value:  hodnota
* return:    hodnota date v UTC 
--------------------------------------------------------------------------------------------------------------------------------

### verze 1.0.6

* #### S konfiguračním souborem YAML se nyní pracuje v _UTF-8_

* #### Nová třída _LoggedObject_
--------------------------------------------------------------------------------------------------------------------------------

### verze 1.0.8
 
* #### Nové utility pro práci s daty JSON _data_utils_
--------------------------------------------------------------------------------------------------------------------------------

#### is_valid_email(email: str) -> bool:
Kontrola validity emailové adresy
* param email: hodnota 
* return: True/False
--------------------------------------------------------------------------------------------------------------------------------

### verze 1.1.0

* #### Přidán obecný datový slovník SYSNET do balíku models.general

Datový slovník je vytvořen pomocí pydantic a je plně kompatibilní s FastAPI. 
Obsahuje základní datové typy, které se používají ve všech aplikacích SYSNET. 

--------------------------------------------------------------------------------------------------------------------------------

### verze 1.1.3

Třída **PersonBaseType** rozšířena o atribut **identifier** (hlavní identifikátor) a metodu **make_identifier()**, 
která naplní atribut **identifier** z unid, pid nebo uuid. 


## Systémové proměnné

* **TZ**: Časová zóna. Implicitně 'Europe/Prague'
* **DEBUG**: Debug mode. Implicitně `True`
* **LOG_FORMAT**: Formát logování. Implicitně `'%(asctime)s - %(levelname)s in %(module)s: %(message)s'`
* **LOG_DATE_FORMAT**: Formát data pro logování. Implicitně `'%d.%m.%Y %H:%M:%S'`
* **PID_PREFIX**: PID prefix. Implicitně `'SNT'`

### verze 1.2.0

1. Místo typu `UUID` se v modelu používá pouze `str`. Je tomu tak kvůli ukládání do **MongoDb**.
2. Doplněn abstraktní typ `BaseEnum`, který obsahuje metodu `has_value`. 


### verze 1.2.4

Z modelu CITES přenesena třída **PersonTypeEnum**
Typ osoby (zdroj CRŽP):  
- legalEntity: tuzemská právnická osoba 
- legalEntityWithoutIco: tuzemská právnická osoba bez IČO 
- foreignLegalEntity: zahraniční právnická osoba 
- businessNaturalPerson: tuzemská fyzická osoba podnikající 
- naturalPerson: tuzemská fyzická osoba nepodnikající 
- foreignNaturalPerson: zahraniční fyzická osoba podnikající


### Verze 1.3.0

Přidána třida **Context**, která se používá při ověřování API-KEY

### Verze 1.3.1

Přidán modul s konstantami **constants.py**. Zatím obsahuje několik konstant pro parametry používané 
v konfiguračních souborech yaml.

### Verze 1.3.5

Do **PersonBaseType** doplněn atribut **person_printable** (Název osoby pro tisk)


### Verze 1.3.10

Do **MetadataTypeBase** doplněn atribut **comment** (Poznámka nebo komentář k metadatům)

### Verze 1.4.0

Do **PersonBaseType** doplněna strukturovaná adresa atribut **location (LocationType)**. 
Dosud používaný zápis adresa orientovaný na papírový permit neodpovídá požadavkům EU-CITES a Toolkitu CITES  
