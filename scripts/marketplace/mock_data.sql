-- ===================================
-- 1️⃣ Limpeza de dados (filhos primeiro)
-- ===================================

DELETE FROM direct_exchange_participants;
DELETE FROM direct_exchange;

DELETE FROM marketplace_exchange_class;
DELETE FROM marketplace_exchange;

DELETE FROM exchange_admin_courses;
DELETE FROM exchange_admin;

DELETE FROM exchange_expirations;

-- ===================================
-- 2️⃣ Inserção de dados no Marketplace Exchange
-- ===================================

INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted, admin_state) VALUES
(1, 'Armindo Santos', '202108881', false, 'untreated'),
(2, 'Tomás Palma', '202108880', false, 'untreated'),
(4, 'João Horácio', '202108883', false, 'untreated'),
(5, 'Óscar Cardoso', '202108884', false, 'untreated'),
(6, 'Ana Oliveira', '202108885', false, 'untreated'),
(7, 'António Oliveira', '202108886', false, 'untreated'),
(8, 'Armindo Armindo', '202108887', false, 'untreated'),
(9, 'João Andrade', '202108888', false, 'untreated');

INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES
(1, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC01', '1MEIC05'),
(1, 'Sistemas Gráficos e Interativos', 'SGI', 540680, '1MEIC05', '1MEIC02'),
(2, 'Aprendizagem Computacional', 'AC', 540676 , '1MEIC04', '1MEIC01'),
(4, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC06', '1MEIC05'),
(4, 'Desenvolvimento de Software de Larga Escala', 'DS', 540677, '1MEIC06', '1MEIC05'),
(5, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC01', '1MEIC07'),
(6, 'Aprendizagem Computacional', 'AC',540676 , '1MEIC01', '1MEIC02'),
(7, 'Sistemas Distribuídos de Larga Escala', 'SDLE', 540679 , '1MEIC01', '1MEIC07'),
(8, 'Processamento e Recuperação de Informação', 'PRI', 540678, '1MEIC03', '1MEIC05'),
(9, 'Sistemas Distribuídos de Larga Escala', 'SDLE', 540679 , '1MEIC03', '1MEIC04');

-- ===================================
-- 3️⃣ Inserção de dados no Direct Exchange
-- ===================================

INSERT INTO direct_exchange (id, issuer_name, issuer_nmec, accepted, admin_state, last_validated) VALUES
(1, 'Armindo Santos', '202108881', true, 'untreated', null),
(3, 'Ana Santos', '202208881', true, 'untreated', null),
(4, 'A', '20230000', true, 'untreated', null),
(6, 'Armindo Osóriosssssssssss', '202108880', true, 'untreated', null);

INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, class_participant_goes_from, class_participant_goes_to, course_unit, course_unit_id, direct_exchange, accepted) VALUES
(1, 'Armindo Santos', 202108881, '1MEIC06', '1MEIC05', 'AC', 540676, 1, false),
(2, 'Participante 2', 202108880, '1MEIC05', '1MEIC06', 'AC', 540676, 1, false),
(3, 'Ana Santos', 202208881, '1MEIC06', '1MEIC05', 'AC', 540676, 3, false),
(5, 'blabla', 202308880, '1MEIC05', '1MEIC06', 'AC', 540676, 3, false),
(9, 'A', 202300000, '1MEIC06', '1MEIC05', 'AC', 540676, 4, false),
(10, 'B', 202300001, '1MEIC05', '1MEIC06', 'AC', 540676, 4, false),
(11, 'Armindo Osóriosssssssssss', 202108880, '1MEIC01', '1MEIC06', 'DS', 540677, 6, true),
(12, 'José Santossdjcsubvfewusdbjbewudsjibdewss', 202109260, '1MEIC06', '1MEIC01', 'DS', 540677, 6, true);

-- ===================================
-- 4️⃣ Inserção de admins e cursos
-- ===================================

INSERT INTO exchange_admin (id, username) VALUES
(1, '202109260'),
(2, '202405731');

INSERT INTO exchange_admin_courses (exchange_admin_id, course_id) VALUES
(2, 22841),
(2, 22862);

-- ===================================
-- 5️⃣ Inserção de Exchange Expirations (datas corrigidas para setembro de 2025)
-- ===================================

INSERT INTO exchange_expirations(course_unit_id, active_date, end_date) VALUES
(540679, '2023-11-18 15:00:00', '2025-09-30 23:59:59'),
(541872, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541873, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541871, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541875, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541874, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541883, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541881, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541882, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541884, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541893, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541891, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541892, '2025-02-07 08:00:00', '2025-09-30 23:59:59'),
(541894, '2025-02-07 08:00:00', '2025-09-30 23:59:59');
