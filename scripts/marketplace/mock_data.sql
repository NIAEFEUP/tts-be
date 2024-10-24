DELETE FROM direct_exchange;
DELETE FROM direct_exchange_participants;
DELETE FROM marketplace_exchange;
DELETE FROM marketplace_exchange_class;
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted) VALUES (1, 'Armindo Santos', '202108881', false);
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (1, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC01', '1MEIC05');
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (1, 'Sistemas Gráficos e Interativos', 'SGI', 540680, '1MEIC05', '1MEIC02');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted) VALUES (2, 'Tomás Palma', '202108880', false);
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (2, 'Aprendizagem Computacional', 'AC', 540676 , '1MEIC04', '1MEIC01');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted) VALUES (4, 'João Horácio', '202108883', false);
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (4, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC06', '1MEIC05');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted) VALUES (5, 'Óscar Cardoso', '202108884', false);
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (5, 'Aprendizagem Computacional', 'AC', 540676, '1MEIC01', '1MEIC07');
INSERT INTO marketplace_exchange (id, issuer_name, issuer_nmec, accepted) VALUES (6, 'Ana Oliveira', '202108885', false);
INSERT INTO marketplace_exchange_class (marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES (6, 'Aprendizagem Computacional', 'AC',540676 , '1MEIC01', '1MEIC01');

INSERT INTO direct_exchange (id, issuer_name, issuer_nmec, accepted) VALUES (1, 'Armindo Santos', '202108881', false);
INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, old_class, new_class, course_unit, course_unit_id, direct_exchange, accepted) VALUES (1, 'Participante 1', 202108881, '1MEIC06', '1MEIC05', 'AC', 540676, 1, false);
INSERT INTO direct_exchange_participants (id, participant_name, participant_nmec, old_class, new_class, course_unit, course_unit_id, direct_exchange, accepted) VALUES (2, 'Participante 2', 202108880, '1MEIC05', '1MEIC06', 'AC', 540676, 1, false);
