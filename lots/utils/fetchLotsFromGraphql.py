import requests
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from django.utils import  timezone
from django.core.cache import cache
from lots.models import Article, Unit, Cities, Regions
from lots.insert_region_location import read_xls
#this query will use for fetching lots from grapql server
query = """
    query getLots($limit: Int, $after: Int) {
        Lots(limit: $limit, after: $after) {
            lotNumber
            TrdBuy {
                id
                RefSubjectType {
                    nameRu
                }
                startDate
                endDate
            }
            Files {
                filePath
            }
            Plans {
                subjectBiin
                subjectNameRu
                nameRu
                descRu
                amount
                count
                Customer {
                    Address {
                        katoCode
                        address
                    }
                }
                RefUnits {
                    nameRu 
                }
                RefTradeMethods {
                    nameRu
                }

                PlansKato {
                    refKatoCode
                    fullDeliveryPlaceNameRu
                }
            }
        }
    }
"""


def get_aware_datetime(date_str):
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret


def fetchLotsFromGraphql():
   
    headers = {
        'Authorization': 'Bearer bb28b5ade7629ef512a8b7b9931d04ad',
        'Content-Type': 'application/json'
    }

    endpoint = "https://ows.goszakup.gov.kz/v3/graphql"


    variables = {
        'limit': 200
    }
    

    try:
        if cache.get('lastId'):
            variables['after'] = cache.get('lastId')
        
        response = requests.post(endpoint, json={'query': query, 'variables': variables}, headers=headers, verify=False)
        data = response.json()['data']
        meta = response.json()['extensions']

        if(meta['pageInfo']['hasNextPage']):
            #setting lastid article id it will save that id for 12 hours
            cache.set('lastId', meta['pageInfo']['lastId'], timeout=43200)


        for lot in data['Lots']:
            unit, created = Unit.objects.get_or_create(name=lot['Plans'][0]['RefUnits']['nameRu'])

            lotObj = {
                'xml_id': lot['lotNumber'],
                'itemZakup': lot['TrdBuy']['RefSubjectType']['nameRu'],
                'date_open': get_aware_datetime(lot['TrdBuy']['startDate']),
                'date': get_aware_datetime(lot['TrdBuy']['endDate']),
                'customer_bin': lot['Plans'][0]['subjectBiin'],
                'customer': lot['Plans'][0]['subjectNameRu'],
                'title': lot['Plans'][0]['nameRu'],
                'lotFullName': lot['Plans'][0]['descRu'],
                'price': lot['Plans'][0]['amount'],
                'count': lot['Plans'][0]['count'],
                'statzakup': lot['Plans'][0]['RefTradeMethods']['nameRu'],
                'unit_id': unit.id,
                'yst': f"https://goszakup.gov.kz/ru/announce/index/{lot['TrdBuy']['id']}?tab=documents"
            }

            try:
                article, created = Article.objects.get_or_create(**lotObj);
             
             
                fetch_region_location_from_goszak({
                    'kato_code': lot['Plans'][0]['Customer']['Address'][0]['katoCode'],
                    'address': lot['Plans'][0]['Customer']['Address'][0]['address']
                }, article.xml_id)

            except Exception as e:
                print(f"an exception occured when creating new article {e}")

    except Exception as e:
        print(f'something went wrong exception: {e}')





def fetch_region_location_from_goszak(item, lot_number):
    kato_list = read_xls()

    try:
        kato_code = item["kato_code"]
        region_code = kato_code[0:2] + "0000000"
        location_code = kato_code[0:4] + "00000"

        location_found = False
        location  = None
        try:
            location = Cities.objects.get(code=location_code)
        except Exception as e:
            print(f"exception in finding cities with location_code: {location_code} exception: {e} ", location_code)
        #checking is location none
        if location:
            location_found = True
            try:
                a=Article.objects.get(xml_id=lot_number)
                a.city=location
                a.save()
            except Exception as e:
                print(f"exception updating location found in db with lot number: {lot_number} with {e} ", lot_number)


        region_found = False
        region = None
        try:
            region = Regions.objects.get(code=region_code)
        except Exception as e:
            print("exception in fetching region with region_code: ", region_code)
            print(e)

        code_map = {'710000000': ' г. Нур-Султан', '750000000': 'г. Алматы', '790000000': 'г. Шымкент'}
        if region:
            region_found = True
            try:
                a=Article.objects.get(xml_id=lot_number)
                a.region=region
                a.save()
            except Exception as e:
                print("exception in updating lot with region found in db with lot number: ", lot_number)
                print(e)



        if not location_found:
            code_map = {'710000000': ' г. Нур-Султан', '750000000': 'г. Алматы', '790000000': 'г. Шымкент'}
            cc = None
            if kato_code in ["710000000", "750000000", "790000000"]:
                print("kato_code in (71, 75,m 79)")
                try:
                    cc = Cities()
                    cc.code = kato_code
                    cc.name = code_map[kato_code]
                    cc.save()
                except Exception as e:
                    print("exception creating city (code in 71, 75, 79) with kato_code: ", kato_code)
                    print(e)
            else:
                print("kato_code not in (71, 75, 79)")
                try:
                    cc = Cities()
                    cc.code = location_code
                    cc.name = location_code
                    cc.save()
                except Exception as e:
                    print("exception creating city, when kato not in (71-79) with location_code: ", location_code)
                    print(e)
            if cc:
                try:
                    a = Article.objects.get(xml_id=lot_number)
                    a.city = cc
                    a.save()
                except Exception as e:
                    print("exception updating lot after create city with lot number: ", lot_number)
                    print("with city: ", cc)
                    print(e)

        if region_found:
            print("region found")
        else:
            print("region not found")
            code_map = {'710000000': ' г. Нур-Султан', '750000000': 'г. Алматы', '790000000': 'г. Шымкент'}
            rr = None
            if kato_code in ["710000000", "750000000", "790000000"]:
                try:
                    rr = Regions()
                    rr.code = kato_code
                    rr.name = code_map[kato_code]
                    rr.save()
                except Exception as e:
                    print("exception creating region when code in (71-79): ", kato_code)
                    print(e)
            else:
                try:
                    rr = Regions()
                    rr.code = region_code
                    rr.name = region_code
                    rr.save()
                except Exception as e:
                    print(e)             
            if rr:
                try:
                    a = Article.objects.get(xml_id=lot_number)
                    a.region = rr
                    a.save()
                except Exception as e:
                    print("exception updating lot with lot number: ", lot_number)
                    print(e)

        address = item["address"]
        if address:
            address_split = item["address"].split(",")
            if '0' in address_split[0]:
                address_split = address_split[1:]
                print("address without city: ", address_split)
                if location:
                    address = location.name + ", " + ", ".join(address_split)
            try:
                a=Article.objects.get(xml_id=lot_number)
                a.addressFull=address
                a.save()
            except Exception as e:
                print("exception in updating address with lot number: ", lot_number)
                print(e)

    except Exception as e:
        print("exeption in updating region/location")
        print(e)




