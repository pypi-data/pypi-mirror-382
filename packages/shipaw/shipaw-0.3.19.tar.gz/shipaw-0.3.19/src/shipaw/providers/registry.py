from shipaw.providers.parcelforce.provider import ParcelforceShippingProvider
from shipaw.providers.provider_abc import ShippingProvider
from shipaw.providers.apc.provider import APCShippingProvider

PROVIDER_TYPE_REGISTER: dict[str, type[ShippingProvider]] = {
    'APC': APCShippingProvider,
    'PARCELFORCE': ParcelforceShippingProvider,
}
#
# PROVIDER_REGISTER: dict[str, ShippingProvider] = {
#     'APC': APCShippingProvider.from_env_settings(),
#     'PARCELFORCE': ParcelforceShippingProvider.from_env_settings(),
# }