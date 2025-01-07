import axios from "axios";

export const session_seed = Math.round(Math.random() * 10000000)

let server_url = ' https://analytics-trustyfox.pythonanywhere.com'

const get_geo = async () => {

    // console.log('getting ip')

    let url = 'https://api.ipify.org?format=json';
    let geo_url = `${server_url}/event/geo_locate`

    let ip = await axios.get(url)
        .then(resp => resp.data['ip'])
        .catch(err => null)

    if (!ip) {
        console.log("IP retrieval failed, skipping geolocation.");
        return null;
    }

    // console.log('getting geo')

    let geolocation = axios.get(geo_url, {params: {'ip': ip}})
        .then(geo => geo.data)
        .catch(err => null)

    return geolocation
}

export const geo_location = get_geo()
