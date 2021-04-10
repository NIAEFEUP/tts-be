const router = require("express").Router();
const faculties = require("./faculties");
const example = require("./health-check");

router.use("/faculties", faculties);
router.use("/health-check", example);


module.exports = router;
