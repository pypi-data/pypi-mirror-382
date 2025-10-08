import DidengAPI
apis = DidengAPI.client.DidengAPI()
api = (str(str((apis.get_info())["CA-Library-IDE"]["best_version"])).split("v")[1])