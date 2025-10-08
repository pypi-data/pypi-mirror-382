# Setup

## Index env file

set environment variable 'ENV_INDEX' to an index of environment files:

- SHIPAW_ENV = Shipaw settings env file
- APC_ENV = APC settings env file
- PARCELFORCE_ENV = Parcelforce settings env file

## Shipaw env file
### switches 
- SHIPPER_LIVE - set to 'true' for live mode, 'false' for test mode
- LOG_LEVEL - set to 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'

### paths
- LABEL_DIR - absolute path to label download root directory
- LOG_DIR - absolute path to log file directory
- UI_DIR - absolute path to UI root directory (templates and static)

### derived paths to overwrite if necessary
- [STATIC_DIR] = UI_DIR / 'static'
- [TEMPLATE_DIR] = UI_DIR / 'templates'

### sender details
- ADDRESS_LINE1
- [ADDRESS_LINE2]
- [ADDRESS_LINE3]
- TOWN
- POSTCODE
- [COUNTRY] = 'GB'
- BUSINESS_NAME
- CONTACT_NAME
- EMAIL
- [PHONE] = MOBILE_PHONE
- MOBILE_PHONE

## APC env file

- APC_EMAIL
- APC_PASSWORD
- BASE_URL

## Parcelforce env file
- PF_AC_NUM_1
- PF_CONTRACT_NUM_1
- DEPARTMENT_ID=1
- PF_EXPR_USR=EL
- PF_EXPR_PWD

- [PF_ENDPOINT]=https://expresslink-test.parcelforce.net/ws/
- [PF_BINDING]={http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding
- [TRACKING_URL_STEM]='https://www.royalmail.com/track-your-item#/tracking-results/'
