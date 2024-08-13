--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.3

-- Started on 2024-08-13 20:42:51 UTC

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 219 (class 1259 OID 16432)
-- Name: class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."class" (
    "id" integer NOT NULL,
    "name" character varying(31) NOT NULL,
    "course_unit_id" integer NOT NULL,
    "last_updated" timestamp without time zone NOT NULL
);


--
-- TOC entry 216 (class 1259 OID 16392)
-- Name: course; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."course" (
    "id" integer NOT NULL,
    "faculty_id" character varying(10) NOT NULL,
    "name" character varying(200) NOT NULL,
    "acronym" character varying(10) NOT NULL,
    "course_type" character varying(2) NOT NULL,
    "year" integer NOT NULL,
    "url" character varying(2000) NOT NULL,
    "plan_url" character varying(2000) NOT NULL,
    "last_updated" timestamp without time zone NOT NULL
);


--
-- TOC entry 218 (class 1259 OID 16417)
-- Name: course_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."course_metadata" (
    "course_id" integer NOT NULL,
    "course_unit_id" integer NOT NULL,
    "course_unit_year" smallint NOT NULL,
    "ects" numeric(4,0) NOT NULL
);


--
-- TOC entry 217 (class 1259 OID 16404)
-- Name: course_unit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."course_unit" (
    "id" integer NOT NULL,
    "course_id" integer NOT NULL,
    "name" character varying(200) NOT NULL,
    "acronym" character varying(16) NOT NULL,
    "url" character varying(2000) NOT NULL,
    "semester" smallint NOT NULL,
    "year" smallint NOT NULL,
    "schedule_url" character varying(2000) DEFAULT NULL::character varying,
    "last_updated" timestamp without time zone NOT NULL
);


--
-- TOC entry 215 (class 1259 OID 16385)
-- Name: faculty; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."faculty" (
    "acronym" character varying(10) NOT NULL,
    "name" "text",
    "last_updated" timestamp without time zone NOT NULL
);


--
-- TOC entry 224 (class 1259 OID 16482)
-- Name: info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."info" (
    "date" timestamp without time zone NOT NULL
);


--
-- TOC entry 222 (class 1259 OID 16462)
-- Name: professor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."professor" (
    "id" integer NOT NULL,
    "professor_acronym" character varying(32),
    "professor_name" character varying(100)
);


--
-- TOC entry 220 (class 1259 OID 16442)
-- Name: slot; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."slot" (
    "id" integer NOT NULL,
    "lesson_type" character varying(3) NOT NULL,
    "day" smallint NOT NULL,
    "start_time" numeric(3,1) NOT NULL,
    "duration" numeric(3,1) NOT NULL,
    "location" character varying(31) NOT NULL,
    "is_composed" boolean NOT NULL,
    "professor_id" integer,
    "last_updated" timestamp without time zone NOT NULL
);


--
-- TOC entry 221 (class 1259 OID 16447)
-- Name: slot_class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."slot_class" (
    "slot_id" integer NOT NULL,
    "class_id" integer NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 16467)
-- Name: slot_professor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."slot_professor" (
    "slot_id" integer NOT NULL,
    "professor_id" integer NOT NULL
);


--
-- TOC entry 3291 (class 2606 OID 16436)
-- Name: class class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."class"
    ADD CONSTRAINT "class_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3288 (class 2606 OID 16421)
-- Name: course_metadata course_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_metadata"
    ADD CONSTRAINT "course_metadata_pkey" PRIMARY KEY ("course_id", "course_unit_id", "course_unit_year");


--
-- TOC entry 3281 (class 2606 OID 16398)
-- Name: course course_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course"
    ADD CONSTRAINT "course_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3284 (class 2606 OID 16411)
-- Name: course_unit course_unit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_unit"
    ADD CONSTRAINT "course_unit_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3277 (class 2606 OID 16391)
-- Name: faculty faculty_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."faculty"
    ADD CONSTRAINT "faculty_pkey" PRIMARY KEY ("acronym");


--
-- TOC entry 3302 (class 2606 OID 16486)
-- Name: info info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."info"
    ADD CONSTRAINT "info_pkey" PRIMARY KEY ("date");


--
-- TOC entry 3298 (class 2606 OID 16466)
-- Name: professor professor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."professor"
    ADD CONSTRAINT "professor_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3296 (class 2606 OID 16451)
-- Name: slot_class slot_class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_class"
    ADD CONSTRAINT "slot_class_pkey" PRIMARY KEY ("slot_id", "class_id");


--
-- TOC entry 3294 (class 2606 OID 16446)
-- Name: slot slot_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot"
    ADD CONSTRAINT "slot_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3300 (class 2606 OID 16471)
-- Name: slot_professor slot_professor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_professor"
    ADD CONSTRAINT "slot_professor_pkey" PRIMARY KEY ("slot_id", "professor_id");


--
-- TOC entry 3289 (class 1259 OID 16493)
-- Name: class_course_unit_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "class_course_unit_id" ON "public"."class" USING "btree" ("course_unit_id");


--
-- TOC entry 3292 (class 1259 OID 16492)
-- Name: class_uniqueness; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "class_uniqueness" ON "public"."class" USING "btree" ("name", "course_unit_id");


--
-- TOC entry 3278 (class 1259 OID 16487)
-- Name: course_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "course_course_id" ON "public"."course" USING "btree" ("id", "faculty_id", "year");


--
-- TOC entry 3279 (class 1259 OID 16488)
-- Name: course_faculty_acronym; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "course_faculty_acronym" ON "public"."course" USING "btree" ("faculty_id");


--
-- TOC entry 3286 (class 1259 OID 16491)
-- Name: course_metadata_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "course_metadata_index" ON "public"."course_metadata" USING "btree" ("course_id", "course_unit_id", "course_unit_year");


--
-- TOC entry 3282 (class 1259 OID 16490)
-- Name: course_unit_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "course_unit_course_id" ON "public"."course_unit" USING "btree" ("course_id");


--
-- TOC entry 3285 (class 1259 OID 16489)
-- Name: course_unit_uniqueness; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "course_unit_uniqueness" ON "public"."course_unit" USING "btree" ("id", "course_id", "year", "semester");


--
-- TOC entry 3307 (class 2606 OID 16437)
-- Name: class class_course_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."class"
    ADD CONSTRAINT "class_course_unit_id_fkey" FOREIGN KEY ("course_unit_id") REFERENCES "public"."course_unit"("id") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3303 (class 2606 OID 16399)
-- Name: course course_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course"
    ADD CONSTRAINT "course_faculty_id_fkey" FOREIGN KEY ("faculty_id") REFERENCES "public"."faculty"("acronym") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3305 (class 2606 OID 16427)
-- Name: course_metadata course_metadata_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_metadata"
    ADD CONSTRAINT "course_metadata_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."course"("id") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3306 (class 2606 OID 16422)
-- Name: course_metadata course_metadata_course_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_metadata"
    ADD CONSTRAINT "course_metadata_course_unit_id_fkey" FOREIGN KEY ("course_unit_id") REFERENCES "public"."course_unit"("id") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3304 (class 2606 OID 16412)
-- Name: course_unit course_unit_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_unit"
    ADD CONSTRAINT "course_unit_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."course"("id") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3308 (class 2606 OID 16452)
-- Name: slot_class slot_class_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_class"
    ADD CONSTRAINT "slot_class_class_id_fkey" FOREIGN KEY ("class_id") REFERENCES "public"."class"("id") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3309 (class 2606 OID 16457)
-- Name: slot_class slot_class_slot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_class"
    ADD CONSTRAINT "slot_class_slot_id_fkey" FOREIGN KEY ("slot_id") REFERENCES "public"."slot"("id") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3310 (class 2606 OID 16477)
-- Name: slot_professor slot_professor_professor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_professor"
    ADD CONSTRAINT "slot_professor_professor_id_fkey" FOREIGN KEY ("professor_id") REFERENCES "public"."professor"("id") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3311 (class 2606 OID 16472)
-- Name: slot_professor slot_professor_slot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_professor"
    ADD CONSTRAINT "slot_professor_slot_id_fkey" FOREIGN KEY ("slot_id") REFERENCES "public"."slot"("id") ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2024-08-13 20:42:51 UTC

--
-- PostgreSQL database dump complete
--
