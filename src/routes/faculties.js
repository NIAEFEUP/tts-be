const facultiesIds = require("../../assets/faculties.json");
const faculties = require("../../assets/faculties_acronyms.json");

const got = require("got");
const express = require("express");
const router = express.Router();
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

router.get("/", function(req, res) {
    res.send(facultiesIds);
});

router.get("/check", function(req, res) {
    try {
        faculties.forEach((faculty) => {
            const url = `https://sigarra.up.pt/${faculty}/pt/UCURR_GERAL.PESQUISA_UCS`;
            got(url)
                .then((response) => {
                    const dom = new JSDOM(response.body);
                    const scriptHtml = dom.window.document.querySelector(
                        'script[data-lov-template-zone="search"]'
                    ).innerHTML;
                    const dom2 = new JSDOM(scriptHtml.toString());
                    const facultyId = dom2.window.document.querySelector(
                        '.form input[name="pv_search_inst_id"]'
                    ).value;

                    // outdated id
                    if (facultyId !== facultiesIds[faculty]) {
                        throw new Error(
                            `Faculty id ´${faculty}' outdated in the backend storage`
                        );
                    }
                })
                .catch((error) => {
                    console.error(`URL: ${url}:${error}`);
                    return res.status(500).json({ success: false, error: error.message });
                });
        });
    } catch (e) {
        return res.status(409).json({ success: false, error: e.message });
    }

    return res.status(200).json({ success: true, ok: "Backend is updated" });
});

// https://sigarra.up.pt/up/pt/web_base.gera_pagina?p_pagina=escolas faculties_acronyms
module.exports = router;
