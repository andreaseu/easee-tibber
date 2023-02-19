#!/usr/bin python3
import requests
import json
from datetime import datetime, timedelta
import os
import sys

############################################################################
## Functions
############################################################################
### Read the user settings from json file
def read_evn_json():
    config_path = os.path.abspath(sys.argv[0])
    config_filename = os.path.join(os.path.dirname(config_path), "config.json")
    # Checks if the json file is present
    if os.path.isfile(config_filename):
        print("Load the file:", config_filename)
        # Read the json file
        with open(config_filename, "r") as f:
            env_data = json.load(f)

        # Load easee values
        env_data_easee = env_data["easee"]
        easee_userName = env_data_easee["userName"]
        easee_password = env_data_easee["password"]
        easee_AccessToken = env_data_easee["AccessToken"]
        easee_currency = env_data_easee["currency"]
        easee_InvalidateRefreshToken = env_data_easee["InvalidateRefreshToken"]

        # Load tibber values
        env_data_tibber = env_data["tibber"]
        tibber_token = env_data_tibber["token"]

        return (
            easee_userName,
            easee_password,
            easee_AccessToken,
            easee_currency,
            easee_InvalidateRefreshToken,
            tibber_token,
        )
    else:
        print("The file doesnt exist:", config_filename)
        print("Exit")
        sys.exit()


############################################################################
### log the last runtime
def log_last_runtime():
    session_path = os.path.abspath(sys.argv[0])
    session_filename = os.path.join(os.path.dirname(session_path), "session.json")

    # Checks if the json file is present
    if os.path.isfile(session_filename):
        # Read the session json file
        with open(session_filename, "r") as f:
            log_last_runtime_session_data = json.load(f)

        now = datetime.now()

        log_last_runtime_session_data["general"] = {"lastRuntime": now.isoformat()}

        with open(session_filename, "w") as f:
            json.dump(log_last_runtime_session_data, f, indent=4)
    else:
        print("The session file doesnt exist.")
        print("Continue with the first login.")
        easee_AccessToken = easee_authentication()
        print("Please start the script again.")
        sys.exit()


############################################################################
### Easee Authentication
def easee_authentication():
    global easee_userName, easee_password, easee_AccessToken
    easee_authentication_url = "https://api.easee.cloud/api/accounts/login"
    easee_authentication_payload = (
        f'{{"userName":"{easee_userName}","password":"{easee_password}"}}'
    )
    easee_authentication_headers = {
        "accept": "application/json",
        "content-type": "application/*+json",
        "Authorization": f"Bearer {easee_AccessToken}",
    }
    easee_authentication_response = requests.post(
        easee_authentication_url,
        data=easee_authentication_payload,
        headers=easee_authentication_headers,
    )
    if easee_authentication_response.status_code == 200:
        easee_authentication_data = easee_authentication_response.json()

        # Calculate the expiration date
        now = datetime.now()
        easee_authentication_expiredate = now + timedelta(
            seconds=easee_authentication_data["expiresIn"]
        )

        # Write the response output in session.json
        easee_authentication_session_data = json.loads("{}")
        easee_authentication_session_data["easee_session"] = {
            "createtime": now.isoformat(),
            "accesstoken": easee_authentication_data["accessToken"],
            "expiresin": easee_authentication_data["expiresIn"],
            "refreshtoken": easee_authentication_data["refreshToken"],
            "expiredate": easee_authentication_expiredate.isoformat(),
        }

        session_path = os.path.abspath(sys.argv[0])
        session_filename = os.path.join(os.path.dirname(session_path), "session.json")

        with open(session_filename, "w") as f:
            json.dump(easee_authentication_session_data, f, indent=4)

        easee_AccessToken = easee_authentication_data["refreshToken"]

        return easee_AccessToken

        print("Login successfully.")
    else:
        print("Error:", easee_authentication_response.status_code)
        print("Exit")
        sys.exit()


############################################################################
### Easee refresh token
def easee_refreshtoken():
    session_path = os.path.abspath(sys.argv[0])
    session_filename = os.path.join(os.path.dirname(session_path), "session.json")

    # Checks if the json file is present
    if os.path.isfile(session_filename):
        # Read the session json file
        with open(session_filename, "r") as f:
            easee_refreshtoken_session_data = json.load(f)

        easee_refreshtoken_session_data_easee = easee_refreshtoken_session_data[
            "easee_session"
        ]
        easee_refreshtoken_accesstoken = easee_refreshtoken_session_data_easee[
            "accesstoken"
        ]
        easee_refreshtoken_refreshtoken = easee_refreshtoken_session_data_easee[
            "refreshtoken"
        ]
        easee_refreshtoken_expiredate = easee_refreshtoken_session_data_easee[
            "expiredate"
        ]

        now = datetime.now()
        easee_refreshtoken_currenttime = now.isoformat()

        # Checks if the token has already expired
        if easee_refreshtoken_expiredate <= easee_refreshtoken_currenttime:
            print(
                "Token has already expired.",
                easee_refreshtoken_expiredate,
            )
            print("Continue with the first login.")
            easee_AccessToken = easee_authentication()
        else:
            print("Token is still valid.", easee_refreshtoken_expiredate)
            # Since token is valid this is refresh
            easee_refreshtoken_url = (
                "https://api.easee.cloud/api/accounts/refresh_token"
            )
            easee_refreshtoken_payload = f'{{"accessToken":"{easee_refreshtoken_accesstoken}","refreshToken":"{easee_refreshtoken_refreshtoken}"}}'
            easee_refreshtoken_headers = {
                "accept": "application/json",
                "content-type": "application/*+json",
                "Authorization": f"Bearer {easee_refreshtoken_accesstoken}",
            }

            easee_refreshtoken_response = requests.post(
                easee_refreshtoken_url,
                data=easee_refreshtoken_payload,
                headers=easee_refreshtoken_headers,
            )

            if easee_refreshtoken_response.status_code == 200:
                easee_refreshtoken_data = easee_refreshtoken_response.json()

                # Calculate the expiration date
                now = datetime.now()
                easee_refreshtoken_expiredate = now + timedelta(
                    seconds=easee_refreshtoken_data["expiresIn"]
                )

                # Write the response output in session.json
                easee_refreshtoken_session_data = json.loads("{}")
                easee_refreshtoken_session_data["easee_session"] = {
                    "createtime": now.isoformat(),
                    "accesstoken": easee_refreshtoken_data["accessToken"],
                    "expiresin": easee_refreshtoken_data["expiresIn"],
                    "refreshtoken": easee_refreshtoken_data["refreshToken"],
                    "expiredate": easee_refreshtoken_expiredate.isoformat(),
                }

                session_path = os.path.abspath(sys.argv[0])
                session_filename = os.path.join(
                    os.path.dirname(session_path), "session.json"
                )

                with open(session_filename, "w") as f:
                    json.dump(easee_refreshtoken_session_data, f, indent=4)
                print("Token Refresh successfully.")

                # Return the new accesstoken
                return easee_refreshtoken_accesstoken
            else:
                print("Token Refresh does not successfully.")
                print("Continue with the first login.")
                easee_AccessToken = easee_authentication()
    else:
        print("The session file doesnt exist.")
        print("Continue with the first login.")
        easee_AccessToken = easee_authentication()
        print("Please start the script again.")
        sys.exit()


############################################################################
### Easee load profile infos
def easee_profile():
    global easee_AccessToken

    easee_profile_url = "https://api.easee.cloud/api/accounts/profile"
    easee_profile_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {easee_AccessToken}",
    }

    easee_profile_response = requests.get(
        easee_profile_url, headers=easee_profile_headers
    )

    if easee_profile_response.status_code == 200:
        easee_profile_data = easee_profile_response.json()
        ####
        # Write the response output in session.json2
        session_path = os.path.abspath(sys.argv[0])
        session_filename = os.path.join(os.path.dirname(session_path), "session.json")

        with open(session_filename, "r") as f:
            easee_profile_session_data = json.load(f)

        easee_profile_session_data["easee_profile"] = {
            "userId": easee_profile_data["userId"],
            "firstName": easee_profile_data["firstName"],
            "lastName": easee_profile_data["lastName"],
        }

        with open(session_filename, "w") as f:
            json.dump(easee_profile_session_data, f, indent=4)

        print(
            "Profile load successfully, ",
            easee_profile_data["lastName"],
            easee_profile_data["firstName"],
        )
    else:
        print("Profile load does not successfully.")
        print("Exit")
        sys.exit()


############################################################################
### Easee load sites infos
def easee_getsites():
    global easee_AccessToken

    easee_getsites_url = "https://api.easee.cloud/api/sites"
    easee_getsites_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {easee_AccessToken}",
    }

    easee_getsites_response = requests.get(
        easee_getsites_url, headers=easee_getsites_headers
    )

    n = 0
    if easee_getsites_response.status_code == 200:
        easee_getsites_data = easee_getsites_response.json()

        n = n + 1

        for easee_site_key in easee_getsites_data:
            ####
            # Write the response output in session.json2
            session_path = os.path.abspath(sys.argv[0])
            session_filename = os.path.join(
                os.path.dirname(session_path), "session.json"
            )

            with open(session_filename, "r") as f:
                easee_getsites_session_data = json.load(f)

            easee_site_name = "easee_site_" + str(n)

            easee_getsites_session_data["easee_sites"] = {
                easee_site_name: {
                    "Id": easee_site_key["id"],
                    "siteKey": easee_site_key["siteKey"],
                    "name": easee_site_key["name"],
                }
            }

        with open(session_filename, "w") as f:
            json.dump(easee_getsites_session_data, f, indent=4)

        print(n, "sites load successfully.")
    else:
        print("Sites load does not successfully.")
        print("Exit")
        sys.exit()


############################################################################
### Easee load site infos / get the price
def easee_getsiteinfos():
    global easee_AccessToken

    session_path = os.path.abspath(sys.argv[0])
    session_filename = os.path.join(os.path.dirname(session_path), "session.json")

    # Checks if the json file is present
    if os.path.isfile(session_filename):
        # Read the session json file
        with open(session_filename, "r") as f:
            easee_getsiteinfos_session_data = json.load(f)

        easee_getsiteinfos_session_data_easee = easee_getsiteinfos_session_data.get(
            "easee_sites", {}
        )
        for easee_site_key in easee_getsiteinfos_session_data_easee:
            easee_site_info = easee_getsiteinfos_session_data_easee[easee_site_key]
            easee_site_id = easee_site_info["Id"]
            easee_site_name = easee_site_info["name"]

            print("Id:", easee_site_id)
            print("name:", easee_site_name)

            easee_getsiteinfos_url = (
                "https://api.easee.cloud/api/sites/{}?detailed=false"
            )
            easee_getsiteinfos_headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {easee_AccessToken}",
            }

            easee_getsiteinfos_response = requests.get(
                easee_getsiteinfos_url.format(easee_site_id),
                headers=easee_getsiteinfos_headers,
            )

            if easee_getsiteinfos_response.status_code == 200:
                easee_getsiteinfos_data = easee_getsiteinfos_response.json()
                easee_getsiteinfos_session_data["easee_sites"][easee_site_key] = {
                    "Id": easee_site_info["Id"],
                    "siteKey": easee_site_info["siteKey"],
                    "name": easee_site_info["name"],
                    "costPerKWh": easee_getsiteinfos_data["costPerKWh"],
                    "costPerKwhExcludeVat": easee_getsiteinfos_data[
                        "costPerKwhExcludeVat"
                    ],
                    "currencyId": easee_getsiteinfos_data["currencyId"],
                    "vat": easee_getsiteinfos_data["vat"],
                    "updatedOn": easee_getsiteinfos_data["updatedOn"],
                }

                with open(session_filename, "w") as f:
                    json.dump(easee_getsiteinfos_session_data, f, indent=4)
                print("Price information read successfully.")
                ###
            else:
                print("Sitesinfos load does not successfully.")
                print("Exit")
                sys.exit()
    else:
        print("The session file doesnt exist.")
        print("Exit")
        sys.exit()


############################################################################
### Easee set price info
def easee_setprice():
    global easee_AccessToken, easee_currency

    session_path = os.path.abspath(sys.argv[0])
    session_filename = os.path.join(os.path.dirname(session_path), "session.json")

    # Checks if the json file is present
    if os.path.isfile(session_filename):
        # Read the session json file
        with open(session_filename, "r") as f:
            easee_setprice_session_data = json.load(f)

        tibber_price = easee_setprice_session_data["tibber_price"]
        tibber_total_price = tibber_price["total_price"]
        tibber_energy_price = tibber_price["energy_price"]
        tibber_tax_price = tibber_price["tax_price"]

        easee_setprice_session_data_easee = easee_setprice_session_data.get(
            "easee_sites", {}
        )
        for easee_site_key in easee_setprice_session_data_easee:
            easee_site_info = easee_setprice_session_data_easee[easee_site_key]
            easee_site_id = easee_site_info["Id"]

            easee_setprice_url = "https://api.easee.cloud/api/sites/{}/price"

            easee_setprice_payload = f'{{"currencyId":"{easee_currency}","costPerKWh":{tibber_total_price},"costPerKwhExcludeVat":{tibber_energy_price},"vat":{tibber_tax_price}}}'
            easee_setprice_headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {easee_AccessToken}",
            }

            easee_setprice_response = requests.post(
                easee_setprice_url.format(easee_site_id),
                data=easee_setprice_payload,
                headers=easee_setprice_headers,
            )

            if easee_setprice_response.status_code == 200:
                print("The price was successfully set.")
            else:
                print("The price was does not successfully set.")
                print("Exit")
                sys.exit()


############################################################################
### Get the tibber price
def tibber_getprice():
    global tibber_token

    tibber_getprice_url = "https://api.tibber.com/v1-beta/gql"
    tibber_getprice_headers = {
        "Authorization": tibber_token,
        "Content-Type": "application/json",
    }
    tibber_getprice_payload = {
        "query": "{viewer {homes {currentSubscription {priceInfo {current {total energy tax startsAt }}}}}}"
    }

    tibber_getprice_response = requests.post(
        tibber_getprice_url,
        headers=tibber_getprice_headers,
        json=tibber_getprice_payload,
    )

    if tibber_getprice_response.status_code == 200:
        tibber_getprice_data = tibber_getprice_response.json()

        # Write the response output in session.json
        session_path = os.path.abspath(sys.argv[0])
        session_filename = os.path.join(os.path.dirname(session_path), "session.json")

        with open(session_filename, "r") as f:
            tibber_getprice_session_data = json.load(f)

        price_info = tibber_getprice_data["data"]["viewer"]["homes"][0][
            "currentSubscription"
        ]["priceInfo"]

        tibber_getprice_session_data["tibber_price"] = {
            "total_price": price_info["current"]["total"],
            "energy_price": price_info["current"]["energy"],
            "tax_price": price_info["current"]["tax"],
            "starts_at": price_info["current"]["startsAt"],
        }

        with open(session_filename, "w") as f:
            json.dump(tibber_getprice_session_data, f, indent=4)

        print("Tibber price infos load successfully.")

    else:
        print("Failed to retrieve price info from tibber")
        print("Exit")
        sys.exit()


############################################################################
### Invalidate refresh token

###
def easee_InvalidateRefreshTokens():
    print("Still under development.")
    ### Still under development


#    session_path = os.path.abspath(sys.argv[0])
#    session_filename = os.path.join(os.path.dirname(session_path), 'session.json')

# Checks if the json file is present
#    if os.path.isfile(session_filename):
# Read the session json file
#        with open(session_filename, 'r') as f:
#            easee_InvalidateRefreshTokens_session_data = json.load(f)

#        easee_InvalidateRefreshTokens_session_data_easee_profile = easee_InvalidateRefreshTokens_session_data['easee_profile']
#        easee_InvalidateRefreshTokens_userId = easee_InvalidateRefreshTokens_session_data_easee_profile['userId']
#        print(easee_InvalidateRefreshTokens_userId)
#    else:
#        print("The file doesnt exist:",session_filename)
#        print("Exit")
#        sys.exit()

############################################################################
## Main Programm
############################################################################
# Check json file an read the values
(
    easee_userName,
    easee_password,
    easee_AccessToken,
    easee_currency,
    easee_InvalidateRefreshToken,
    tibber_token,
) = read_evn_json()

# Renewal of the token, if this fails a new login is executed
easee_AccessToken = easee_refreshtoken()

# Load easee profil infos
easee_profile()

# Load easee sites infos
easee_getsites()

easee_getsiteinfos()

tibber_getprice()

easee_setprice()

# Invalidate easee refresh token
if easee_InvalidateRefreshToken == "True":
    easee_InvalidateRefreshTokens()

# Log the runtime
log_last_runtime()