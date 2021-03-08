# SIGARRA API Documentation for Schedule getting

Attempt to document everything in the same place.

Useful references:
* [Core base for this document](https://github.com/NIAEFEUP/tts-fe/blob/docs/api-spec/api-spec.md)
* [The holy grail of "SIGARRA docs"](https://web.archive.org/web/20200715100657/https://github.com/angelaigreja/sifeup-mobile/blob/master/SiFEUPMobile/src/pt/up/beta/mobile/sifeup/SifeupAPI.java)
* [A repo with some python scripts with utilities that use SIGARRA's API](https://github.com/miguelpduarte/FEUP-Tools/tree/master/python)
* [UPCC Source code](https://github.com/miguelpduarte/FEUP-Tools/tree/master/up-course-collision) - React app that can check if course units have students in common using a SIGARRA login. It's live [here](https://upcc.miguelpduarte.me/) - The requests are being proxied by Netlify, but you can still use them as an example since Netlify is not adding any logic.

## Table of Contents

* [Faculty Acronyms](#Faculty-Acronyms)
* [Faculty IDs](#Faculty-IDs)
* [Faculty Courses](#Faculty-Courses)
* [Course Course Units (Course UCs aka "Cadeiras")](#Course-UCs)
* [UC Schedule](#UC-Schedule)
* [Authentication](#Authentication)


## Faculty Acronyms

The faculty acronyms can be scraped from `https://sigarra.up.pt/up/pt/web_base.gera_pagina?p_pagina=escolas`.

However, since they are unlikely to change, this can be hard-coded. (Especially since we will probably know of new faculties and can easily include them)

```
[
  "faup",
  "fbaup",
  "fcup",
  "fcnaup",
  "fadeup",
  "fdup",
  "fep",
  "feup",
  "ffup",
  "flup",
  "fmup",
  "fmdup",
  "fpceup",
  "icbas",
  "pbs"
]
```

## Faculty IDs

For the next requests, we need `inst_id`. This can be scraped from `https://sigarra.up.pt/{faculty_acronym}/pt/UCURR_GERAL.PESQUISA_UCS`.

Using the `input[name="pv_search_inst_id"]` selector, the `value` attribute of the input represents the `inst_id`. This input element is inside a `<script>`, so depending on the DOM parser being used, the selector may have to be run within the scope of the `<script>`. This can be achieved using the `script[data-lov-template-zone="search"]` selector and using the element's `innerHTML`.

Once again, these can be hard-coded. They can be found [here, for example](https://github.com/miguelpduarte/FEUP-Tools/blob/master/python/faculty_ids.json) and are listed below:

```
{
  fadeup: '18383',
  faup: '18380',
  fbaup: '18395',
  fcnaup: '18379',
  fcup: '18493',
  fdup: '18487',
  fep: '18491',
  feup: '18490',
  ffup: '18381',
  flup: '18492',
  fmdup: '18384',
  fmup: '18494',
  fpceup: '18489',
  icbas: '18382'
}
```

## Faculty Courses

To fetch a faculty's courses we can use the following endpoint, which returns JSON:

```
https://sigarra.up.pt/{faculty_acronym}/pt/cur_lov_geral.get_json_cursos_ga?
pv_search_inst_adm=
&pv_search_alect={schoolYear}
&pv_search_inst_id={inst_id}
&pv_search_cod=
&pv_search_nome=
&pv_search_sigla=
```

Parameters:
* `faculty_acronym` - self-explanatory
* `pv_search_alect`-  Current school year (`alect` = `"ano letivo"` probably). 2019 represents 2019/2020, 2020 represents 2020/2021, etc.
* `pv_search_inst_id` - Use the faculty's `inst_id` from the previous step
* `pv_search_cod` - Search using a course's code
* `pv_search_nome` - Search using a course's name
* `pv_search_sigla` - Search using a course's "sigla"

The search parameters filter the response. To fetch all the Courses the parameters may be left blank.

All of the parameters are always required, otherwise the response will be `"A página que pediu não se encontra disponível."`.

**Example:**

[FEUP's courses for 2019/2020](https://sigarra.up.pt/feup/pt/cur_lov_geral.get_json_cursos_ga?pv_search_inst_adm=&pv_search_alect=2019&pv_search_inst_id=18490&pv_search_cod=&pv_search_nome=&pv_search_sigla=)

```
GET https://sigarra.up.pt/feup/pt/cur_lov_geral.get_json_cursos_ga?
pv_search_inst_adm=
&pv_search_alect=2019
&pv_search_inst_id=18490
&pv_search_cod=
&pv_search_nome=
&pv_search_sigla=
```

**Result snippet:**

```
{
  "completeSetCount": 137,
  "data": [
    {
      "tipo": "Mestrado Integrado",
      "codigo": "9459",
      "sigla": "MIEIC",
      "nome": "Mestrado Integrado em Engenharia Informática e Computação",
      "id": "742"
    },
    ...
  ]
}
```

By the way, **important detail**: The output of the endpoint is JSON, but the response header is `Content-Type: text/html;charset=ISO-8859-15` so some parsers may complain unless the correct charset is used or the data is converted to UTF-8.

[Example python script that does this](https://github.com/miguelpduarte/FEUP-Tools/blob/master/python/get_up_faculty_courses.py)

## Course UCs

Similar to the previous request. We can use this endpoint which returns JSON:

```
https://sigarra.up.pt/{faculty_acronym}/pt/mob_ucurr_geral.pesquisa?
pv_ano_lectivo={school_year}
&pv_curso_id={course_id}
&pv_pag={page_number}
```

Parameters:
* `faculty_acronym` - self-explanatory
* `pv_ano_lectivo` -  Current school year, just like before. 2019 represents 2019/2020, 2020 represents 2020/2021, etc.
* `pv_curso_id` - Course ID, get this from the previous step. (e.g., for MIEIC this is 742)
* `pv_page` - Page number. This endpoint uses pagination. The index is 1-based and this parameter can be left blank to fetch the first page.

**Example:**

[MIEIC's UCs for 2019/2020](https://sigarra.up.pt/feup/pt/mob_ucurr_geral.pesquisa?pv_ano_lectivo=2019&pv_curso_id=742)

```
GET https://sigarra.up.pt/feup/pt/mob_ucurr_geral.pesquisa?
pv_ano_lectivo=2019
&pv_curso_id=742
```

**Result snippet:**

```
{
  "total":73,
  "pagina":"1",
  "tam_pagina":20,
  "resultados":[
    {
      "ocorr_id":436459,
      "codigo":"EIC0048",
      "nome":"Arquitectura de Sistemas de Software",
      "name":"Software Systems Architecture",
      "ano_lectivo":2019,
      "periodo":"2S",
      "data_inicio":"",
      "data_fim":""
    },
    ...
  ]
}
```

It is possible to calculate the number of pages necessary by taking `total` (total number of UCs) and dividing it by `tam_pagina` (page size), rounding up.

Example scripts:
* [Example python script that uses `pv_uc_sigla` to use this endpoint but filters by a UC's "sigla" instead of fetching everything](https://github.com/miguelpduarte/FEUP-Tools/blob/master/python/sobreposicoes_v2.py#L14)
* [UPCC Source code method that fetches a course's course units - check `fetchCourseUnits`](https://github.com/miguelpduarte/FEUP-Tools/blob/032b6a9a7208eceaa693eeb399f303fc603008a4/up-course-collision/src/App.js#L63) - This one does the aforementioned math and can be used as a good example for that as well.

## UC Schedule

**This endpoint requires [authentication](#Authentication)**. It returns JSON:

```
https://sigarra.up.pt/{faculty_acronym}/pt/mob_hor_geral.ucurr?
pv_ocorrencia_id=436459
&pv_semana_ini=
&pv_semana_fim=
```

Parameters:
* `faculty_acronym` - self-explanatory
* `pv_ocorrencia_id` -  Course Unit ID, get from the previous step.
* `pv_semana_ini` - Start week for the schedule range, YYYYMMDD format
* `pv_semana_fim` - End week for the schedule range, YYYYMMDD format

All of the above parameters are mandatory, otherwise the request fails with error.
It may be possible to have the weeks hardcoded for each semester and try to parse out the response somehow, as it seems like it will have a lot of extra information.

**Example:**

[LGP's Schedule for 2020/2021](https://sigarra.up.pt/feup/pt/mob_hor_geral.ucurr?pv_ocorrencia_id=459511&pv_semana_ini=20200920&pv_semana_fim=20201010)

```
GET https://sigarra.up.pt/feup/pt/mob_hor_geral.ucurr
?pv_ocorrencia_id=459511
&pv_semana_ini=20200920
&pv_semana_fim=20201010
```

**Result snippet:**

(NOTE: This is currently "bad data" but is all I can get ATM. More testing necessary)

```
{
  "blocos": [
    {
      "semana_ini": "2021-02-07",
      "semana_fim": "2021-02-20",
      "bloco_codigo": null,
      "c_turma_id": null,
      "turmas_bloco": "",
      "turma_real": "",
      "periodo": ""
    },
    {
      "semana_ini": "2021-02-21",
      "semana_fim": "2021-04-03",
      "bloco_codigo": null,
      "c_turma_id": null,
      "turmas_bloco": "",
      "turma_real": "",
      "periodo": ""
    },
    {
      "semana_ini": "2021-04-04",
      "semana_fim": "2021-05-29",
      "bloco_codigo": null,
      "c_turma_id": null,
      "turmas_bloco": "",
      "turma_real": "",
      "periodo": ""
    }
  ],
  "horario": []
}
```

**"Good" example:**

(Since SIGARRA API is currently broken for 2021 - 2nd semester 2020/2021 - we can use examples of earlier dates)

[ASSO's schedule for 2019/2020](https://sigarra.up.pt/feup/pt/mob_hor_geral.ucurr?pv_ocorrencia_id=436459&pv_semana_ini=20200105&pv_semana_fim=20200312)

```
GET https://sigarra.up.pt/feup/pt/mob_hor_geral.ucurr
?pv_ocorrencia_id=436459
&pv_semana_ini=20200105
&pv_semana_fim=20200312
```

**Response snippet:**

```
{
  "horario": [
    {
      "dia": 2,
      "hora_inicio": 61200,
      "ucurr_sigla": "ASSO",
      "ocorrencia_id": 436459,
      "tipo": "TP",
      "aula_id": 5293588,
      "aula_duracao": 3,
      "sala_sigla": "B310+B011",
      "salas": [
        {
          "espaco_id": 73394,
          "espaco_nome": "B310"
        },
        {
          "espaco_id": 73441,
          "espaco_nome": "B011"
        }
      ],
      "doc_sigla": "AMA",
      "docentes": [
        {
          "doc_codigo": "231081",
          "doc_nome": "Ademar Manuel Teixeira de Aguiar"
        }
      ],
      "turma_sigla": "4MIEIC01",
      "turmas": [
        {
          "turma_id": 209578,
          "turma_sigla": "4MIEIC01"
        }
      ],
      "periodo": 3
    },
    ...
  ]
}
```

There are no code examples available for this yet.

## Authentication

In order to authenticate to SIGARRA's mobile API, you can use the following endpoint:

```
https://sigarra.up.pt/{faculty_acronym}/pt/mob_val_geral.autentica?
pv_login={username}
&pv_password={password}
```

Parameters:
* `faculty_acronym` - self-explanatory. I don't think this has any impact on the login request itself, though. (i.e. the session cookie should be valid for all of the faculties)
* `pv_login` - The account username, e.g. `up201606298`. Do not use the email or it will not work.
* `pv_password` - The account's password. Be careful to store / get this safely!

The session cookie is shared between the API and SIGARRA's website, so if you login in SIGARRA's webpage, the API requests will also work, which can be used for testing the other endpoints initially.

**Example request:**

```
GET https://sigarra.up.pt/feup/pt/mob_val_geral.autentica?
pv_login=up1234567890
&pv_password=bmljZV90cnlfcGl6emFfZ3V5
```

**Example response (error):**

```
{
    "authenticated": false,
    "erro": "Autentica\u00E7\u00E3o",
    "erro_msg": "O nome de utilizador ou a palavra-passe foram incorrectamente introduzidos."
}
```

Example response (success):
```
{
    "authenticated": true,
    "codigo": "201606298",
    "tipo": "A"
}
```

Example scripts:
* [Example in sobreposicoes python script](https://github.com/miguelpduarte/FEUP-Tools/blob/master/python/sobreposicoes_v2.py#L35)
* [Example in UPCC, checking for a valid response](https://github.com/miguelpduarte/FEUP-Tools/blob/032b6a9a7208eceaa693eeb399f303fc603008a4/up-course-collision/src/App.js#L90)

