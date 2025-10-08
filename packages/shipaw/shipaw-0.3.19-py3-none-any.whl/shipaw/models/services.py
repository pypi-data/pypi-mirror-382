from dataclasses import dataclass
from typing import Literal


@dataclass
class Services:
    NEXT_DAY: str
    NEXT_DAY_12: str
    NEXT_DAY_9: str

    def reverse_lookup(self, provider_code: str) -> str | None:
        res = next((name for name, code in self.__dict__.items() if code == provider_code), None)
        if not res:
            raise ValueError(f'Invalid service code: {provider_code}')
        return res

    def lookup(self, agnostic_name: str) -> str:
        res = self.__dict__.get(agnostic_name)
        if not res:
            raise ValueError(f'Invalid service name: {agnostic_name}')
        return res


ServiceType = Literal['NEXT_DAY', 'NEXT_DAY_12', 'NEXT_DAY_9', 'SATURDAY']

SERVICE_ATTRS = tuple(Services.__annotations__.keys())
# type ServiceDict = dict[ServiceType, str]


# def get_agnostic_service_name(service_code: str, services: Services) -> ServiceType | None:
#     service_map: ServiceDict = {
#         'NEXT_DAY': services.NEXT_DAY,
#         'NEXT_DAY_12': services.NEXT_DAY_12,
#         'NEXT_DAY_9': services.NEXT_DAY_9,
#         'SATURDAY': 'Saturday Delivery',
#     }
#     for service_name, code in service_map.items():
#         if code == service_code:
#             return service_name
#     return None