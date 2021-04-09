const { Router } = require("express");

const router = Router();

router.get("/", function(req, res) {
    res.send("hello world!");
});

module.exports = router;
