const router = require("express").Router();
const faculties = require("./check-faculties");
const example = require("./example");

router.use("/faculties", faculties);
router.use("/", example);


module.exports = router;
