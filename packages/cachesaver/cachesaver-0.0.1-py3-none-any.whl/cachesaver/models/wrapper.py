from ..pipelines import OnlineAPI
from diskcache import Cache
from copy import deepcopy
from ..typedefs import BatchRequestModel, Batch, Request, Metadata, SingleRequestModel, Response

class Create:
    def __init__(self, api, namespace):
        self.api = api
        self.global_request_counter = 0
        self.namespace = namespace

    async def __call__(self, *args, **kwargs):
        self.global_request_counter += 1
        if "n" in kwargs:
            n = kwargs.pop("n")
        else:
            n = 1
        flattened_responses = await self.api.request(Request(
            args=args,
            kwargs=kwargs,
            n=n,
            namespace=self.namespace,
            request_id=str(self.global_request_counter)
        ))
        choices = [resp.choices[0] for resp in flattened_responses.data]
        one_response = deepcopy(flattened_responses.data[0])
        one_response.choices = choices
        return one_response


class Completions:
    def __init__(self, api, namespace):
        self.create = Create(api, namespace)


class Chat:
    def __init__(self,  api, namespace):
        self.completions = Completions( api, namespace)


class AsyncWrapper:
    def __init__(self,
                 model:SingleRequestModel,
                 namespace="default",
                 cachedir="./cache",
                 batch_size=1):
        self.namespace = namespace
        self.cachedir = cachedir
        self.batch_size = batch_size
        self.cache = Cache("./cache", timeout=-1)
        self.model = model
        self.api = OnlineAPI(model=self.model,
                             cache=self.cache, batch_size=self.batch_size)
        self.chat = Chat(self.api, self.namespace)
