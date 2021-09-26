import axios from "axios";

const baseURL = "http://127.0.0.1:8000/api/v1/";

let axiosInstance = axios.create({
  baseURL: baseURL,
  timeout: 5000,
  headers: {
    Authorization:
      localStorage.getItem("access_token") !== null
        ? "Token " + localStorage.getItem("access_token")
        : null,
    "content-type": "application/json",
    accept: "application/json",
  },
});

let axiosMultipartInstance = axios.create({
  baseURL: baseURL,
  timeout: 5000,
  headers: {
    Authorization:
      localStorage.getItem("access_token") !== null
        ? "Token " + localStorage.getItem("access_token")
        : null,
    "content-type": "multipart/form-data",
    accept: "application/json",
  },
});

window.onstorage = (event) => {
  console.log("-----LOG------");
  console.log(event.storageArea);
  console.log(event.key);
  console.log(event.oldValue);
  console.log(event.newValue);
  console.log("----ENDLOG----");

  if (
    event.storageArea === window.localStorage &&
    (event.key === "access_token" || event.key === null)
  ) {
    console.log("WORKED!!!");

    axiosInstance = axios.create({
      baseURL: baseURL,
      timeout: 5000,
      headers: {
        Authorization:
          event.newValue !== null ? "Token " + event.newValue : null,
        "content-type": "application/json",
        accept: "application/json",
      },
    });

    axiosMultipartInstance = axios.create({
      baseURL: baseURL,
      timeout: 5000,
      headers: {
        Authorization:
          event.newValue !== null ? "Token " + event.newValue : null,
        "content-type": "multipart/form-data",
        accept: "application/json",
      },
    });
  }
};

export { axiosInstance, axiosMultipartInstance };
