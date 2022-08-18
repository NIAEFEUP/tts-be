SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Delete every repeated course with no subjects
--
DELETE FROM `course`
WHERE `id` IN (
  SELECT cid FROM (
    SELECT `id` AS cid
    FROM `course`
    WHERE `id` IN (
      -- Select every repeated course
      SELECT DISTINCT C1.`id`
      FROM `course` C1, `course` C2
      WHERE C1.`course_id` = C2.`course_id` AND C1.`id` <> C2.`id`
    )
    AND `id` NOT IN (
      -- Select every course with subjects
      SELECT DISTINCT `course`.`id`
      FROM `course`, `course_unit`
      WHERE `course`.`id` = `course_unit`.`course_id`
    )
  ) AS C
);

--
-- Delete repeated theoretical classes: same day, duration, start_time, composed class name and course unit id
--
-- DELETE FROM `schedule`
-- WHERE `lesson_type` = 'T'
-- AND `id` NOT IN (
--	SELECT cid FROM (
--		SELECT min(`id`) AS cid
--		FROM `schedule` 
--		WHERE `lesson_type` = 'T' 
--		GROUP BY `day`, `duration`, `start_time`, `composed_class_name`, `course_unit_id`
--	) AS C
-- );



-- 
-- Delete repeated classes: all fields are equal. 
-- 

create view `schedule2` as 
  select min(id) 
  from `schedule` 
  group by `day`, `duration`, `start_time`, `location`, `lesson_type`, `teacher_acronym`, `course_unit_id`, `class_name`, `composed_class_name`;

delete from `schedule` 
where id not in (select * from schedule2);

drop view schedule2;

COMMIT; 
