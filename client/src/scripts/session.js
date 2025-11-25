import {axios} from "@bundled-es-modules/axios";

export const get_session_seed = () => {
  let sid = localStorage.getItem("session-seed");
  // let sid = false
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem("session-seed", sid);
  }
  return sid;
}
//
// let session_seed = null
//
// export const get_session_seed = () => {
//   if (!session_seed) session_seed = crypto.randomUUID()
//   return session_seed
// }
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
