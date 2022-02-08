import requests
import asyncio
import aiohttp
import time

#GET - /api/datasetId [Creates new dataset and returns its ID]
def get_dataset_id():
    res = requests.get(url = "http://api.coxauto-interview.com/api/datasetId")
    data = res.json()
    datasetId = data['datasetId']
    return datasetId

#GET - /api/{datasetId}/vehicles [Get a list of all vehicleids in dataset]
def get_vehicles_list(datasetId):
    res = requests.get(url = f'http://api.coxauto-interview.com/api/{datasetId}/vehicles')
    data = res.json()
    vehicles_List = data['vehicleIds']
    return vehicles_List


async def get_info(data, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json = await response.json()
            data.append(json)

#GET - /api/{datasetId}/vehicles/{vehicleid} [Get information about a vehicle]
async def get_vehicles_info(datasetId, vehicles_list):
    vehicles_info = []
    url = f'http://api.coxauto-interview.com/api/{datasetId}/vehicles/'
    base_url = url + '{vehicleId}'
    futures = [asyncio.ensure_future(get_info(vehicles_info, 
    base_url.format(vehicleId=vehicleId))) for vehicleId in vehicles_list]
    await asyncio.gather(*futures)
    return vehicles_info


async def get_name(data, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json = await response.json()
            data.append(json)


def get_dealers_id(vehicles_info):
    lst = []
    for vehicle_info in vehicles_info:
        lst.append(vehicle_info['dealerId'])
    dealersId = list(set(lst))
    return dealersId

#GET - /api/{datasetId}/dealers/{dealerid} [Get information about a dealer]
async def get_dearers_name(datasetId, dealersId):
    dealers_info = []
    url = f'http://api.coxauto-interview.com/api/{datasetId}/dealers/'
    base_url = url + '{dealer_id}'
    futures = [asyncio.ensure_future(get_name(dealers_info, 
    base_url.format(dealer_id=dealer_id))) for dealer_id in dealersId]
    await asyncio.gather(*futures)
    return dealers_info


def manage_data(vehicles_info, dealers_info):
    for dealer in dealers_info:
        dealer['vehicles'] = []
    for vehicle_info in vehicles_info:
        vehicle = {}
        vehicle['vehicleId'] = vehicle_info['vehicleId']
        vehicle['make'] = vehicle_info['make']
        vehicle['model'] = vehicle_info['model']
        vehicle['year'] = vehicle_info['year']
        for dealer in dealers_info:
            if vehicle_info['dealerId'] == dealer['dealerId']:
                dealer['vehicles'].append(vehicle)
    answer = {'dealers': dealers_info}
    return answer

#POST - /api/{datasetId}/answer [Submit answer for dataset]
def passing_answer(datasetId, answer):
    res = requests.post(f'http://api.coxauto-interview.com/api/{datasetId}/answer', json = answer)
    print(res)
    print(res.json())


async def main():
    dataset_id = get_dataset_id()
    vehicles_list = get_vehicles_list(dataset_id)
    vehicles_info = await get_vehicles_info(dataset_id, vehicles_list)
    dealers_id = get_dealers_id(vehicles_info)
    dealers_info = await get_dearers_name(dataset_id, dealers_id)
    answer = manage_data(vehicles_info, dealers_info)
    passing_answer(dataset_id, answer)


start = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
end = time.time()
print(f'>>> async time: {end - start}')
