from __future__ import annotations

import base64
import json

from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import requests

students = [
    "202307365",
    "202303872",
    "202204914",
    "202304064",
    "202305033",
    "202307295",
    "202306618",
    "202306498",
    "202307321",
    "202304594",
]

course_units = [
    "560106",
    "560107",
    "560108",
    "560109",
    "560110",
    "560096"
]


sigarra_requests = {
    "login": {
        "method": "POST",
        "url": "https://sigarra.up.pt/feup/pt/vld_validacao.validacao"
    },
    "student_photo": {
        "method": "GET",
        "url": lambda nmec: f"https://sigarra.up.pt/feup/pt/fotografias_service.foto?pct_cod={nmec}"
    },
    "student_profile": {
        "method": "GET",
        "url": lambda nmec: f"https://sigarra.up.pt/feup/pt/mob_fest_geral.perfil?pv_codigo={nmec}"
    },
    "student_schedule": {
        "method": "GET",
        "url": lambda nmec, semana_ini="20251001", semana_fim="20260131": (
            f"https://sigarra.up.pt/feup/pt/mob_hor_geral.estudante?pv_codigo={nmec}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}"
        )
    },
    "course_unit_schedule": {
        "method": "GET",
        "url": lambda ocorrencia_id, semana_ini="20251001", semana_fim="20260131", faculty="feup": (
            f"https://sigarra.up.pt/{faculty}/pt/mob_hor_geral.ucurr?pv_ocorrencia_id={ocorrencia_id}&pv_semana_ini={semana_ini}&pv_semana_fim={semana_fim}"
        )
    },
    "course_unit_schedule_new": {
        "method": "GET",
        "url": lambda faculty="feup", course_unit_id=None, year="2025", period="2": ( # period 2 means semester 1, it is really weird but it is that way
            f"https://sigarra.up.pt/calendarios-api/api/v1/events/{faculty}/uc/{course_unit_id}/?academic_year={year}&period={period}"
        )
    },
    "course_unit_classes": {
        "method": "GET",
        "url": lambda course_unit_id: f"https://sigarra.up.pt/feup/pt/mob_ucurr_geral.uc_inscritos?pv_ocorrencia_id={course_unit_id}"
    }
}

REPO_ROOT = Path(__file__).resolve().parents[2]
MOCK_DATA_PATH = REPO_ROOT / "django" / "mock-data.json"




def load_mock_store() -> dict:
    if MOCK_DATA_PATH.exists():
        with MOCK_DATA_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"get": {}, "post": {}}


def data_uri(content_type: str, payload: bytes) -> str:
    encoded = base64.b64encode(payload).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


def serialize_response(method: str, url: str, response: requests.Response, store: dict, cookie_snapshot: dict | None = None) -> None:
    bucket = store.setdefault(method.lower(), {})
    entry: dict = {"status_code": response.status_code}

    if method.upper() == "POST":
        entry["cookies"] = {} # Not gonna store actual credentials
    else:
        content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("image/"):
            entry["data"] = data_uri(content_type.split(";")[0], response.content)
        else:
            entry["data"] = response.text

    bucket[url] = entry


def ensure_session() -> tuple[requests.Session, requests.Response]:
    username = input("SIGARRA username: ")
    password = input("SIGARRA password: ")

    session = requests.Session()
    login_url = sigarra_requests["login"]["url"]
    response = session.post(login_url, data={"p_user": username, "p_pass": password})
    response.raise_for_status()
    return session, response


def fetch_all(session: requests.Session, store: dict, login_response: requests.Response) -> None:
    serialize_response(
        "POST",
        sigarra_requests["login"]["url"],
        login_response,
        store,
    )

    for nmec in students:
        photo_url = sigarra_requests["student_photo"]["url"](nmec)
        photo_resp = session.get(photo_url)
        photo_resp.raise_for_status()
        serialize_response("GET", photo_url, photo_resp, store)

        profile_url = sigarra_requests["student_profile"]["url"](nmec)
        profile_resp = session.get(profile_url)
        profile_resp.raise_for_status()
        serialize_response("GET", profile_url, profile_resp, store)

        schedule_url = sigarra_requests["student_schedule"]["url"](nmec)
        schedule_resp = session.get(schedule_url)
        schedule_resp.raise_for_status()
        serialize_response("GET", schedule_url, schedule_resp, store)

    for course_unit in course_units:
        classes_url = sigarra_requests["course_unit_classes"]["url"](course_unit)
        classes_resp = session.get(classes_url)
        classes_resp.raise_for_status()
        serialize_response("GET", classes_url, classes_resp, store)

        schedule_url = sigarra_requests["course_unit_schedule"]["url"](course_unit)
        schedule_resp = session.get(schedule_url)
        schedule_resp.raise_for_status()
        serialize_response("GET", schedule_url, schedule_resp, store)

        new_schedule_url = sigarra_requests["course_unit_schedule_new"]["url"](course_unit_id=course_unit)
        new_schedule_resp = session.get(new_schedule_url)
        new_schedule_resp.raise_for_status()
        serialize_response("GET", new_schedule_url, new_schedule_resp, store)


def main() -> None:
    store = load_mock_store()
    session, login_response = ensure_session()
    fetch_all(session, store, login_response)

    with MOCK_DATA_PATH.open("w", encoding="utf-8") as handle:
        json.dump(store, handle, indent=4, sort_keys=True, ensure_ascii=False)

    print(f"Stored {sum(len(v) for v in store.values())} mock responses in {MOCK_DATA_PATH}")


if __name__ == "__main__":
    main()
