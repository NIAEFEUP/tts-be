-- Delete old data

DELETE FROM exchange_admin_courses;
DELETE FROM exchange_admin;

DELETE FROM exchange_expirations;
DELETE FROM direct_exchange_participants;
DELETE FROM direct_exchange;
DELETE FROM marketplace_exchange_class;
DELETE FROM marketplace_exchange;
DELETE FROM course_unit_enrollment_options;
DELETE FROM course_unit_enrollments;
DELETE FROM exchange_urgent_request_options;
DELETE FROM exchange_urgent_requests;
DELETE FROM exchange_admin_course_units;
DELETE FROM exchange_admin_courses;
DELETE FROM exchange_admin;

-- Students
-- 202307365 -> Alice Oliveira (3LEIC01)
-- 202303872 -> Bruno Silva (3LEIC02)
-- 202204914 -> Carla Mendes (3LEIC03)
-- 202304064 -> Daniel Costa (3LEIC05)
-- 202305033 -> Eva Ferreira (3LEIC06)
-- 202307295 -> Filipe Rocha (3LEIC10)
-- 202306618 -> Gabriela Lima (3LEIC11)
-- 202306498 -> Hugo Fernandes (3LEIC12)
-- 202307321 -> Inês Gomes (3LEIC13)
-- 202304594 -> João Marques (3LEIC14)

-- Available course units (third year)
-- 560106 - Fundamentos de Segurança Informática (FSI)
-- 560107 - Interação Pessoa Computador (IPC)
-- 560108 - Laboratório de Bases de Dados e Aplicações Web (LBAW)
-- 560109 - Programação Funcional e em Lógica (PFL)
-- 560110 - Redes de Computadores (RC)

-- Mock data for marketplace_exchange
INSERT INTO marketplace_exchange(id, issuer_name, issuer_nmec, accepted, hash, admin_state) VALUES
    (1, 'Carla Mendes', '202204914', false, '71776572747975696f706173646667686a6b6c7a786376626e6d313233343536', 'untreated'),
    (2, 'Daniel Costa', '202304064', false, '3383583123884d91e241645651425d13a481203882984e31d7b27fc23b46294c', 'untreated'),
    (3, 'Gabriela Lima', '202306618', false, 'ab259b33a5d2545f7b4785a5434c23a13a802315b1391fb70a5a3089529f520f', 'untreated'),
    (4, 'Bruno Silva', '202303872', false, 'b4429334f952e88a2b9d0572b5a65a335173313819f4a4a6b8923035f2b852a2', 'untreated'),
    (5, 'Hugo Fernandes', '202306498', false, 'a481865f644b4de8301353a8314347b323f3343a8868b675381593b6950b2641', 'untreated'),
    (6, 'Filipe Rocha', '202307295', false, '3450417143458a529435e36551c94b633e9944fb682848114567759191a3c71a', 'untreated'),
    (7, 'Carla Mendes', '202204914', false, '55de52326e37038307766219b9f7963321b7c5f442456f098e4b5284012f393a', 'untreated'),
    (8, 'João Marques', '202304594', false, 'e35113c34053113c149456a6333315a41f5893027a3553301235527033340138', 'untreated'),
    (9, 'Daniel Costa', '202304064', false, '771b43151c2b3b4479da43377928a13e33d016b4b34433f37553581018113463', 'untreated'),
    (10, 'João Marques', '202304594', false, 'a18a1c363779ab0d39a19b1c2d35f3b03f434de331541135181411191111413c', 'untreated'),
    (11, 'Bruno Silva', '202303872', false, '072b834c4515414e4515414d4515414e4515414e4515414e4515414e4515414e', 'untreated'),
    (12, 'Inês Gomes', '202307321', false, 'd44c3a3d3a3b3c3e3f404142434445464748494a4b4c4d4e4f50515253545556', 'untreated'),
    (13, 'Alice Oliveira', '202307365', false, '3132333435363738393031323334353637383930313233343536373839303132', 'untreated'),
    (14, 'Eva Ferreira', '202305033', false, '6162636465666768696a6b6c6d6e6f707172737475767778797a313233343536', 'untreated'),
    (15, 'Filipe Rocha', '202307295', false, '313233343536373839306162636465666768696a6b6c6d6e6f70717273747576', 'untreated'),
    (16, 'Daniel Costa', '202304064', false, 'f33883613aabc7420183017e4370b1340286a652804453876c13a289037393de', 'untreated'),
    (17, 'Gabriela Lima', '202306618', false, '393837363534333231307a797877767574737271706f6e6d6c6b6a6968676665', 'untreated'),
    (18, 'Hugo Fernandes', '202306498', false, '6664736161736466666473616173646666647361617364666664736161736466', 'untreated'),
    (19, 'Inês Gomes', '202307321', false, '6c6b6a6867666473616c6b6a6867666473616c6b6a6867666473616c6b6a6867', 'untreated'),
    (20, 'João Marques', '202304594', false, '3131323233333434353536363737383839393030313132323333343435353636', 'untreated');

INSERT INTO marketplace_exchange_class(marketplace_exchange, course_unit_name, course_unit_acronym, course_unit_id, class_issuer_goes_from, class_issuer_goes_to) VALUES
    (1, 'Laboratório de Bases de Dados e Aplicações Web', 'LBAW', 560108, '3LEIC03', '3LEIC08'),
    (1, 'Programação Funcional e em Lógica', 'PFL', 560109, '3LEIC03', '3LEIC09'),
    (2, 'Programação Funcional e em Lógica', 'PFL', 560109, '3LEIC05', '3LEIC06'),
    (3, 'Redes de Computadores', 'RC', 560110, '3LEIC11', '3LEIC13'),
    (4, 'Fundamentos de Segurança Informática', 'FSI', 560106, '3LEIC02', '3LEIC04'),
    (4, 'Interação Pessoa Computador', 'IPC', 560107, '3LEIC02', '3LEIC01'),
    (5, 'Redes de Computadores', 'RC', 560110, '3LEIC12', '3LEIC13'),
    (6, 'Fundamentos de Segurança Informática', 'FSI', 560106, '3LEIC10', '3LEIC13'),
    (7, 'Redes de Computadores', 'RC', 560110, '3LEIC03', '3LEIC06'),
    (7, 'Programação Funcional e em Lógica', 'PFL', 560109, '3LEIC03', '3LEIC06'),
    (8, 'Laboratório de Bases de Dados e Aplicações Web', 'LBAW', 560108, '3LEIC14', '3LEIC11'),
    (9, 'Fundamentos de Segurança Informática', 'FSI', 560106, '3LEIC05', '3LEIC01'),
    (9, 'Redes de Computadores', 'RC', 560110, '3LEIC05', '3LEIC02'),
    (10, 'Fundamentos de Segurança Informática', 'FSI', 560106, '3LEIC14', '3LEIC11'),
    (10, 'Programação Funcional e em Lógica', 'PFL', 560109, '3LEIC14', '3LEIC12'),
    (11, 'Redes de Computadores', 'RC', 560110, '3LEIC02', '3LEIC07'),
    (11, 'Laboratório de Bases de Dados e Aplicações Web', 'LBAW', 560108, '3LEIC02', '3LEIC07'),
    (12, 'Fundamentos de Segurança Informática', 'FSI', 560106, '3LEIC13', '3LEIC10'),
    (13, 'Programação Funcional e em Lógica', 'PFL', 560109, '3LEIC01', '3LEIC02'),
    (13, 'Redes de Computadores', 'RC', 560110, '3LEIC01', '3LEIC02'),
    (14, 'Fundamentos de Segurança Informática', 'FSI', 560106, '3LEIC06', '3LEIC03'),
    (15, 'Interação Pessoa Computador', 'IPC', 560107, '3LEIC10', '3LEIC11'),
    (15, 'Laboratório de Bases de Dados e Aplicações Web', 'LBAW', 560108, '3LEIC10', '3LEIC12'),
    (16, 'Redes de Computadores', 'RC', 560110, '3LEIC05', '3LEIC07'),
    (17, 'Fundamentos de Segurança Informática', 'FSI', 560106, '3LEIC11', '3LEIC12'),
    (18, 'Interação Pessoa Computador', 'IPC', 560107, '3LEIC12', '3LEIC17'),
    (18, 'Redes de Computadores', 'RC', 560110, '3LEIC12', '3LEIC10'),
    (19, 'Laboratório de Bases de Dados e Aplicações Web', 'LBAW', 560108, '3LEIC13', '3LEIC10'),
    (20, 'Interação Pessoa Computador', 'IPC', 560107, '3LEIC13', '3LEIC11'),
    (20, 'Fundamentos de Segurança Informática', 'FSI', 560106, '3LEIC14', '3LEIC12');

-- Mock data for course_unit_enrollments
INSERT INTO course_unit_enrollments(id, student_nmec, accepted, admin_state, created_at) VALUES
    (1, '202307321', 0, 'untreated', '2026-02-03 22:12:01.598239'),
    (2, '202304594', 0, 'untreated', '2026-02-03 22:12:54.939139'),
    (3, '202305033', 0, 'untreated', '2026-02-03 22:22:34.893334');

INSERT INTO course_unit_enrollment_options(id, created_at, course_unit_id, course_unit_enrollment_id, accepted) VALUES
    (1, '2026-02-03 22:12:01.598778', 560109, 1, 0),
    (2, '2026-02-03 22:12:54.939542', 560108, 2, 0),
    (3, '2026-02-03 22:22:34.893775', 560110, 3, 0);

-- Mock data for direct_exchange
INSERT INTO direct_exchange(id, issuer_name, issuer_nmec, accepted, admin_state, marketplace_exchange) VALUES
    (1, 'Daniel Costa', '202304064', false, 'untreated', 2),
    (2, 'Gabriela Lima', '202306618', false, 'untreated', 3),
    (3, 'Hugo Fernandes', '202306498', false, 'untreated', 5),
    (4, 'Carla Mendes', '202204914', false, 'untreated', 7),
    (5, 'João Marques', '202304594', false, 'untreated', 8);

INSERT INTO direct_exchange_participants(direct_exchange, participant_name, participant_nmec, class_participant_goes_from, class_participant_goes_to, course_unit, course_unit_id, accepted) VALUES
    (1, 'Daniel Costa', '202304064', '3LEIC05', '3LEIC07', 'PFL', 560109, false),
    (1, 'Eva Ferreira', '202305033', '3LEIC07', '3LEIC05', 'PFL', 560109, false),
    (2, 'Gabriela Lima', '202306618', '3LEIC11', '3LEIC13', 'RC', 560110, false),
    (2, 'Inês Gomes', '202307321', '3LEIC13', '3LEIC11', 'RC', 560110, false),
    (3, 'Hugo Fernandes', '202306498', '3LEIC12', '3LEIC13', 'RC', 560110, false),
    (3, 'Inês Gomes', '202307321', '3LEIC13', '3LEIC12', 'RC', 560110, false),
    (4, 'Carla Mendes', '202204914', '3LEIC03', '3LEIC06', 'RC', 560110, false),
    (4, 'Carla Mendes', '202204914', '3LEIC03', '3LEIC06', 'PFL', 560109, false),
    (4, 'Filipe Rocha', '202307295', '3LEIC06', '3LEIC03', 'RC', 560110, false),
    (4, 'Filipe Rocha', '202307295', '3LEIC06', '3LEIC03', 'PFL', 560109, false),
    (5, 'João Marques', '202304594', '3LEIC14', '3LEIC11', 'LBAW', 560108, false),
    (5, 'Gabriela Lima', '202306618', '3LEIC11', '3LEIC14', 'LBAW', 560108, false);

-- Mock data for exchange_urgent_requests
INSERT INTO exchange_urgent_requests(id, message, accepted, admin_state, created_at, issuer_nmec, issuer_name, hash) VALUES
    (1, 'Se não aceitarem o pedido a Doutora Brinquedos disse que não ia sobreviver', 0, 'untreated', '2026-02-03 22:00:17.072886', '202307365', 'Alice Oliveira', '173358602536def6c094a99f26c462ab72ee7fe03eb5aa0b6dd8dd24d6a02221'),
    (2, 'se recusares este pedido és cringe e ser cringe é mau, por isso n recuses porque se recusares és muito cringe e isso é bué cringado', 0, 'untreated', '2026-02-03 22:03:50.065315', '202303872', 'Bruno Silva', 'fd5d4df7b91953c4acb02bc257e46085b9679ab82efb258aba7a0bf6f5d56def'),
    (3, 'A minha irmã é medica e deu atestado por isso posso fazer o que quiser e tens de aceitar ', 0, 'untreated', '2026-02-03 22:08:56.235490', '202307321', 'Inês Gomes', 'e23e454f1bf57f3d2056408e8f09f46b62cb64997d86dbd92ad8a9da32fe87cf'),
    (4, 'eu posso porque o meu pai e diretor do curso e se n aceitarem ficam sem emprego', 0, 'untreated', '2026-02-03 22:20:10.437968', '202307295', 'Filipe Rocha', '3f0d3f97c8fd0f38e109e958151bf1e96134dabfc5dc2250d2818f61fe193675'),
    (5, 'Aceita pls pls pls pls pls pls pls pls', 0, 'untreated', '2026-02-03 22:22:27.575354', '202305033', 'Eva Ferreira', '62255b24f720b9a420ba876546f39411c5b126a1713e149e4966dfda0e5fa838');

INSERT INTO exchange_urgent_request_options(id, class_issuer_goes_from, class_issuer_goes_to, course_unit_id, exchange_urgent_request_id, created_at) VALUES
    (1, '3LEIC01', '3LEIC12', 560107, 1, '2026-02-03 22:00:17.074477'),
    (2, '3LEIC02', '3LEIC07', 560108, 2, '2026-02-03 22:03:50.066350'),
    (3, '3LEIC13', '3LEIC17', 560109, 3, '2026-02-03 22:08:56.236400'),
    (4, '3LEIC10', '3LEIC03', 560108, 4, '2026-02-03 22:20:10.438934'),
    (5, '3LEIC10', '3LEIC13', 560110, 4, '2026-02-03 22:20:10.438953'),
    (6, '3LEIC06', '3LEIC04', 560108, 5, '2026-02-03 22:22:27.576261');

-- Auth users
-- Insert users only if they don't exist
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
SELECT '', NULL, 0, '210963', 'João', 'Cansssss', '210963@up.pt', 0, 1, '2026-02-03 22:00:00.000000'
WHERE NOT EXISTS (SELECT 1 FROM auth_user WHERE username = '210963');

INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
SELECT '', NULL, 0, '424415', 'Augusto', 'Gama', '424415@up.pt', 0, 1, '2026-02-03 22:01:00.000000'
WHERE NOT EXISTS (SELECT 1 FROM auth_user WHERE username = '424415');

-- Admin mock data
INSERT INTO exchange_admin (id, username) VALUES
    (2, '<username>'),
    (3, '210963'),
    (4, '424415');

INSERT INTO exchange_admin_courses (exchange_admin_id, course_id) VALUES
    (2, 22841),
    (2, 22862);


INSERT INTO exchange_admin_course_units (exchange_admin_id, course_unit_id) VALUES
    (4, 560109);

    
-- INSERT INTO exchange_expirations(course_unit_id, active_date, end_date, is_course_expiration) VALUES
--     -- First year
--     (541865, '2025-09-01', '2026-08-31', 1),
--     (541866, '2025-09-01', '2026-08-31', 1),
--     (541867, '2025-09-01', '2026-08-31', 1),
--     (541868, '2025-09-01', '2026-08-31', 1),
--     (541869, '2025-09-01', '2026-08-31', 1),
--     (541870, '2025-09-01', '2026-08-31', 1),
--     -- Second year
--     (541876, '2025-09-01', '2026-08-31', 1),
--     (541877, '2025-09-01', '2026-08-31', 1),
--     (541878, '2025-09-01', '2026-08-31', 1),
--     (541879, '2025-09-01', '2026-08-31', 1),
--     (541880, '2025-09-01', '2026-08-31', 1),
--     -- Third year
--     (541886, '2025-09-01', '2026-08-31', 1),
--     (541887, '2025-09-01', '2026-08-31', 1),
--     (541888, '2025-09-01', '2026-08-31', 1),
--     (541889, '2025-09-01', '2026-08-31', 1),
--     (541890, '2025-09-01', '2026-08-31', 1),
--     -- Fourth year
--     (560265, '2025-09-01', '2026-08-31', 1),
--     (560266, '2025-09-01', '2026-08-31', 1),
--     (560267, '2025-09-01', '2026-08-31', 1),
--     (560268, '2025-09-01', '2026-08-31', 1),
--     (560269, '2025-09-01', '2026-08-31', 1);



-- Exchange Admins
-- These are just regular exchange admins (mostly professors)



-- Admins (Super Users)
-- This is reserved for TTS administrators , they can manage exchange admins