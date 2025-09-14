DELETE FROM direct_exchange;
DELETE FROM direct_exchange_participants;
DELETE FROM marketplace_exchange;
DELETE FROM exchange_admin;
DELETE FROM marketplace_exchange_class;
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (1, 'Armindo Santos', '202108881', false, 'untreated');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (1, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC01', '1MEIC05');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (1, 'Sistemas Gráficos e Interativos', 'SGI', 540680, '1MEIC05', '1MEIC02');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (2, 'Tomás Palma', '202108880', false, 'untreated');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (2, 'Aprendizagem Computacional', 'AC', 540676 , '1MEIC04', '1MEIC01');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (4, 'João Horácio', '202108883', false, 'untreated');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (4, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC06', '1MEIC05');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (4, 'Desenvolvimento de Software de Larga Escala', 'DS', 540677, '1MEIC06', '1MEIC05');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (5, 'Óscar Cardoso', '202108884', false, 'untreated');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (5, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC01', '1MEIC07');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (6, 'Ana Oliveira', '202108885', false, 'untreated');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (6, 'Aprendizagem Computacional', 'AC',540676 , '1MEIC01', '1MEIC02');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (7, 'António Oliveira', '202108886', false, 'untreated');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (7, 'Sistemas Distribuídos de Larga Escala ', 'SDLE', 540679 , '1MEIC01', '1MEIC07');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (8, 'Armindo Armindo', '202108887', false, 'untreated');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (8, 'Processamento e Recuperação de Informação', 'PRI', 540678, '1MEIC03', '1MEIC05');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (9, 'João Andrade', '202108888', false, 'untreated');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (9, 'Sistemas Distribuídos de Larga Escala ', 'SDLE', 540679 , '1MEIC03', '1MEIC04');

INSERT INTO direct_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (1, 'Armindo Santos', '202108881', false, 'untreated');
INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, class_participant_goes_from, class_participant_goes_to, course_unit, course_unit_id, direct_exchange, accepted) VALUES (1, 'Participante 1', 202108881, '1MEIC06', '1MEIC05', 'AC', 540676, 1, false);
INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, class_participant_goes_from, class_participant_goes_to, course_unit, course_unit_id, direct_exchange, accepted) VALUES (2, 'Participante 2', 202108880, '1MEIC05', '1MEIC06', 'AC', 540676, 1, false);

INSERT INTO direct_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES (2, 'José Santos', '202109260', true, 'untreated');
INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, class_participant_goes_from, class_participant_goes_to, course_unit, course_unit_id, direct_exchange, accepted) VALUES (3, 'José Santos', 202109260, '1MEIC06', '1MEIC05', 'AC', 540676, 2, true);
INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, class_participant_goes_from, class_participant_goes_to, course_unit, course_unit_id, direct_exchange, accepted) VALUES (4, 'Armindo Osório', 202108880, '1MEIC05', '1MEIC06', 'AC', 540676, 2, true);
INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, class_participant_goes_from, class_participant_goes_to, course_unit, course_unit_id, direct_exchange, accepted) VALUES (5, 'Armindo Osório', 202108880, '1MEIC01', '1MEIC06', 'DS', 540677, 2, true);
INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, class_participant_goes_from, class_participant_goes_to, course_unit, course_unit_id, direct_exchange, accepted) VALUES (6, 'José Santos', 202109260, '1MEIC06', '1MEIC01', 'DS', 540677, 2, true);

INSERT INTO exchange_admin(id, username) VALUES (1, '202109260');

--INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted) VALUES (1, 'Armindo Santos', '202108881', false);
--INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (1, 'Álgebra Linear e Geometria Analítica', 'ALGA', 541865, '1LEIC01', '1LEIC05');
--INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (1, 'Matemática Discreta', 'MDIS', 541869, '1LEIC01', '1LEIC05');

--INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (54186, '2023-11-18 15:00:00', '2025-10-25 15:00:00');
--INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541869, '2023-11-18 15:00:00', '2025-10-25 15:00:00');
--INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541868, '2023-11-18 15:00:00', '2025-10-25 15:00:00');
--INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541867, '2023-11-18 15:00:00', '2025-10-25 15:00:00');

INSERT INTO exchange_admin (id, username) VALUES (2, '202108880');
INSERT INTO exchange_admin_courses (exchange_admin_id, course_id) VALUES (2, 22841);
INSERT INTO exchange_admin_courses (exchange_admin_id, course_id) VALUES (2, 22862);
INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (540679, '2023-11-18 15:00:00', '2025-10-25 15:00:00');

DELETE FROM exchange_expirations;

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541872, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541873, '2025-02-07 8:00:00', '2025-02-15 24:00:00');


INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541871, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541875, '2025-02-07 8:00:00', '2025-02-15 24:00:00');


INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541874, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541883, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541881, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541882, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541884, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541893, '2025-02-07 8:00:00', '2025-02-15 24:00:00');


INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541891, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541892, '2025-02-07 8:00:00', '2025-02-15 24:00:00');

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES (541894, '2025-02-07 8:00:00', '2025-02-15 24:00:00');