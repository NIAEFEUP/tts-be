--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.3

-- Started on 2024-08-13 22:21:25 UTC

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
-- TOC entry 224 (class 1259 OID 16798)
-- Name: class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."class" (
    "id" bigint NOT NULL,
    "name" character varying(31) NOT NULL,
    "course_unit_id" integer NOT NULL,
    "last_updated" timestamp with time zone NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 16797)
-- Name: class_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."class_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3474 (class 0 OID 0)
-- Dependencies: 223
-- Name: class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."class_id_seq" OWNED BY "public"."class"."id";


--
-- TOC entry 217 (class 1259 OID 16756)
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
    "last_updated" timestamp with time zone NOT NULL
);


--
-- TOC entry 227 (class 1259 OID 16816)
-- Name: course_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."course_metadata" (
    "course_id" integer NOT NULL,
    "course_unit_id" integer NOT NULL,
    "course_unit_year" integer NOT NULL,
    "ects" double precision NOT NULL
);


--
-- TOC entry 222 (class 1259 OID 16785)
-- Name: course_unit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."course_unit" (
    "id" integer NOT NULL,
    "course_id" integer NOT NULL,
    "name" character varying(200) NOT NULL,
    "acronym" character varying(16) NOT NULL,
    "url" character varying(2000) NOT NULL,
    "semester" integer NOT NULL,
    "year" smallint NOT NULL,
    "schedule_url" character varying(2000),
    "last_updated" timestamp with time zone NOT NULL,
    "hash" character varying(64)
);


--
-- TOC entry 218 (class 1259 OID 16763)
-- Name: faculty; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."faculty" (
    "acronym" character varying(10) NOT NULL,
    "name" "text",
    "last_updated" timestamp with time zone NOT NULL
);


--
-- TOC entry 219 (class 1259 OID 16770)
-- Name: info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."info" (
    "date" timestamp with time zone NOT NULL
);


--
-- TOC entry 220 (class 1259 OID 16775)
-- Name: professor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."professor" (
    "id" integer NOT NULL,
    "professor_acronym" character varying(32),
    "professor_name" character varying(100)
);


--
-- TOC entry 221 (class 1259 OID 16780)
-- Name: slot; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."slot" (
    "id" integer NOT NULL,
    "lesson_type" character varying(3) NOT NULL,
    "day" integer NOT NULL,
    "start_time" numeric(3,1) NOT NULL,
    "duration" numeric(3,1) NOT NULL,
    "location" character varying(31) NOT NULL,
    "is_composed" integer NOT NULL,
    "professor_id" integer,
    "last_updated" timestamp with time zone NOT NULL
);


--
-- TOC entry 226 (class 1259 OID 16811)
-- Name: slot_class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."slot_class" (
    "slot_id" integer NOT NULL,
    "class_id" bigint NOT NULL
);


--
-- TOC entry 225 (class 1259 OID 16806)
-- Name: slot_professor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."slot_professor" (
    "slot_id" integer NOT NULL,
    "professor_id" integer NOT NULL
);

CREATE TABLE "public"."marketplace_exchange" (
  "id" SERIAL PRIMARY KEY, 
  "issuer" varchar(32) NOT NULL,
  "accepted" boolean NOT NULL,
  "date" TIMESTAMP DEFAULT now()
);

CREATE TABLE "public"."direct_exchange" (
  "id" SERIAL PRIMARY KEY,
  "issuer" varchar(32) NOT NULL,
  "accepted" boolean NOT NULL,
  "date" TIMESTAMP DEFAULT now(),
  "marketplace_exchange_id" INTEGER DEFAULT NULL REFERENCES "public"."marketplace_exchange"("id")
);

CREATE TABLE "public"."direct_exchange_participants" (
  "id" SERIAL PRIMARY KEY,
  "participant" varchar(32) NOT NULL,
  "old_class" varchar(16) NOT NULL,
  "new_class" varchar(16) NOT NULL,
  "course_unit" varchar(64) NOT NULL,
  "course_unit_id" varchar(16) NOT NULL,
  "direct_exchange" INTEGER NOT NULL REFERENCES "public"."direct_exchange"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  "accepted" boolean NOT NULL,
  "date" TIMESTAMP DEFAULT now()
);

CREATE TABLE "public"."marketplace_exchange_class" (
    "id" SERIAL PRIMARY KEY, 
    "marketplace_exchange" INTEGER NOT NULL REFERENCES "public"."marketplace_exchange"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "course_unit_name" varchar(256) NOT NULL,
    "course_unit_acronym" varchar(256) NOT NULL,
    "course_unit_id" varchar(256) NOT NULL,
    "old_class" varchar(16) NOT NULL,
    "new_class" varchar(16) NOT NULL
); 

CREATE TABLE "public"."exchange_admin" (
  "id" SERIAL PRIMARY KEY,
  "username" varchar(32) NOT NULL UNIQUE
); 

--
-- TOC entry 3276 (class 2604 OID 16801)
-- Name: class id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."class" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."class_id_seq"'::"regclass");


--
-- TOC entry 3299 (class 2606 OID 16833)
-- Name: class class_name_course_unit_id_b5fc7353_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."class"
    ADD CONSTRAINT "class_name_course_unit_id_b5fc7353_uniq" UNIQUE ("name", "course_unit_id");


--
-- TOC entry 3301 (class 2606 OID 16803)
-- Name: class class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."class"
    ADD CONSTRAINT "class_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3280 (class 2606 OID 16805)
-- Name: course course_id_faculty_id_year_a0a480cc_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course"
    ADD CONSTRAINT "course_id_faculty_id_year_a0a480cc_uniq" UNIQUE ("id", "faculty_id", "year");


--
-- TOC entry 3313 (class 2606 OID 16867)
-- Name: course_metadata course_metadata_course_id_course_unit_id_a53bd8fd_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_metadata"
    ADD CONSTRAINT "course_metadata_course_id_course_unit_id_a53bd8fd_uniq" UNIQUE ("course_id", "course_unit_id", "course_unit_year");


--
-- TOC entry 3316 (class 2606 OID 16820)
-- Name: course_metadata course_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_metadata"
    ADD CONSTRAINT "course_metadata_pkey" PRIMARY KEY ("course_id", "course_unit_id", "course_unit_year");


--
-- TOC entry 3282 (class 2606 OID 16762)
-- Name: course course_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course"
    ADD CONSTRAINT "course_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3294 (class 2606 OID 16823)
-- Name: course_unit course_unit_id_course_id_year_semester_5b83b50d_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_unit"
    ADD CONSTRAINT "course_unit_id_course_id_year_semester_5b83b50d_uniq" UNIQUE ("id", "course_id", "year", "semester");


--
-- TOC entry 3296 (class 2606 OID 16791)
-- Name: course_unit course_unit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_unit"
    ADD CONSTRAINT "course_unit_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3285 (class 2606 OID 16769)
-- Name: faculty faculty_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."faculty"
    ADD CONSTRAINT "faculty_pkey" PRIMARY KEY ("acronym");


--
-- TOC entry 3287 (class 2606 OID 16774)
-- Name: info info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."info"
    ADD CONSTRAINT "info_pkey" PRIMARY KEY ("date");


--
-- TOC entry 3289 (class 2606 OID 16779)
-- Name: professor professor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."professor"
    ADD CONSTRAINT "professor_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3309 (class 2606 OID 16815)
-- Name: slot_class slot_class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_class"
    ADD CONSTRAINT "slot_class_pkey" PRIMARY KEY ("slot_id", "class_id");


--
-- TOC entry 3311 (class 2606 OID 16854)
-- Name: slot_class slot_class_slot_id_class_id_618e5482_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_class"
    ADD CONSTRAINT "slot_class_slot_id_class_id_618e5482_uniq" UNIQUE ("slot_id", "class_id");


--
-- TOC entry 3291 (class 2606 OID 16784)
-- Name: slot slot_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot"
    ADD CONSTRAINT "slot_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3303 (class 2606 OID 16810)
-- Name: slot_professor slot_professor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_professor"
    ADD CONSTRAINT "slot_professor_pkey" PRIMARY KEY ("slot_id", "professor_id");


--
-- TOC entry 3306 (class 2606 OID 16841)
-- Name: slot_professor slot_professor_slot_id_professor_id_0a3129c4_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_professor"
    ADD CONSTRAINT "slot_professor_slot_id_professor_id_0a3129c4_uniq" UNIQUE ("slot_id", "professor_id");


--
-- TOC entry 3297 (class 1259 OID 16839)
-- Name: class_course_unit_id_964f4d1d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "class_course_unit_id_964f4d1d" ON "public"."class" USING "btree" ("course_unit_id");


--
-- TOC entry 3277 (class 1259 OID 16830)
-- Name: course_faculty_id_ef24d5b8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "course_faculty_id_ef24d5b8" ON "public"."course" USING "btree" ("faculty_id");


--
-- TOC entry 3278 (class 1259 OID 16831)
-- Name: course_faculty_id_ef24d5b8_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "course_faculty_id_ef24d5b8_like" ON "public"."course" USING "btree" ("faculty_id" "varchar_pattern_ops");


--
-- TOC entry 3314 (class 1259 OID 16878)
-- Name: course_metadata_course_unit_id_8acf031c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "course_metadata_course_unit_id_8acf031c" ON "public"."course_metadata" USING "btree" ("course_unit_id");


--
-- TOC entry 3292 (class 1259 OID 16829)
-- Name: course_unit_course_id_b0c453a5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "course_unit_course_id_b0c453a5" ON "public"."course_unit" USING "btree" ("course_id");


--
-- TOC entry 3283 (class 1259 OID 16821)
-- Name: faculty_acronym_fd9686a8_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "faculty_acronym_fd9686a8_like" ON "public"."faculty" USING "btree" ("acronym" "varchar_pattern_ops");


--
-- TOC entry 3307 (class 1259 OID 16865)
-- Name: slot_class_class_id_050cb01e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "slot_class_class_id_050cb01e" ON "public"."slot_class" USING "btree" ("class_id");


--
-- TOC entry 3304 (class 1259 OID 16852)
-- Name: slot_professor_professor_id_7f0a06e1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "slot_professor_professor_id_7f0a06e1" ON "public"."slot_professor" USING "btree" ("professor_id");


--
-- TOC entry 3319 (class 2606 OID 16834)
-- Name: class class_course_unit_id_964f4d1d_fk_course_unit_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."class"
    ADD CONSTRAINT "class_course_unit_id_964f4d1d_fk_course_unit_id" FOREIGN KEY ("course_unit_id") REFERENCES "public"."course_unit"("id") DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3317 (class 2606 OID 16792)
-- Name: course course_faculty_id_ef24d5b8_fk_faculty_acronym; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course"
    ADD CONSTRAINT "course_faculty_id_ef24d5b8_fk_faculty_acronym" FOREIGN KEY ("faculty_id") REFERENCES "public"."faculty"("acronym") DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3324 (class 2606 OID 16868)
-- Name: course_metadata course_metadata_course_id_d10b5aca_fk_course_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_metadata"
    ADD CONSTRAINT "course_metadata_course_id_d10b5aca_fk_course_id" FOREIGN KEY ("course_id") REFERENCES "public"."course"("id") DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3325 (class 2606 OID 16873)
-- Name: course_metadata course_metadata_course_unit_id_8acf031c_fk_course_unit_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_metadata"
    ADD CONSTRAINT "course_metadata_course_unit_id_8acf031c_fk_course_unit_id" FOREIGN KEY ("course_unit_id") REFERENCES "public"."course_unit"("id") DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3318 (class 2606 OID 16824)
-- Name: course_unit course_unit_course_id_b0c453a5_fk_course_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."course_unit"
    ADD CONSTRAINT "course_unit_course_id_b0c453a5_fk_course_id" FOREIGN KEY ("course_id") REFERENCES "public"."course"("id") DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3322 (class 2606 OID 16860)
-- Name: slot_class slot_class_class_id_050cb01e_fk_class_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_class"
    ADD CONSTRAINT "slot_class_class_id_050cb01e_fk_class_id" FOREIGN KEY ("class_id") REFERENCES "public"."class"("id") DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3323 (class 2606 OID 16855)
-- Name: slot_class slot_class_slot_id_8ac0e819_fk_slot_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_class"
    ADD CONSTRAINT "slot_class_slot_id_8ac0e819_fk_slot_id" FOREIGN KEY ("slot_id") REFERENCES "public"."slot"("id") DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3320 (class 2606 OID 16847)
-- Name: slot_professor slot_professor_professor_id_7f0a06e1_fk_professor_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_professor"
    ADD CONSTRAINT "slot_professor_professor_id_7f0a06e1_fk_professor_id" FOREIGN KEY ("professor_id") REFERENCES "public"."professor"("id") DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3321 (class 2606 OID 16842)
-- Name: slot_professor slot_professor_slot_id_ddc4b9c2_fk_slot_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."slot_professor"
    ADD CONSTRAINT "slot_professor_slot_id_ddc4b9c2_fk_slot_id" FOREIGN KEY ("slot_id") REFERENCES "public"."slot"("id") DEFERRABLE INITIALLY DEFERRED;


-- Completed on 2024-08-13 22:21:25 UTC

--
-- PostgreSQL database dump complete
--
