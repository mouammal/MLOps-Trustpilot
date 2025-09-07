-- users.sql compatible Docker / PostgreSQL

-- Création de la table
CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);

ALTER TABLE public.users OWNER TO airflow;

-- Création de la séquence pour l'ID
CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);

-- Contrainte de clé primaire et unique
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);

-- Insertion des données
INSERT INTO public.users (id, username, password, role, created_at) VALUES
(1,'admin','$2b$12$nMwUWkrqA6TP.nn8wIkqZ.SkevVEez9adxm/6gkyQVuoHVJrlk0aG','admin','2025-09-03 17:44:51'),
(2,'client','$2b$12$vmMsgDUISoKy/qzXylv3puvEQqW.ESo1YsAq8OXVwBqRkMwkJOYV.','client','2025-09-03 17:44:51'),
(3,'rami','$2b$12$/yOoaaPw/YC0zeGpn/puL.xyrCyCkaQqIc.9bnzZ6shPaL7Jj2VpW','admin','2025-09-03 17:44:51'),
(4,'maxi','$2b$12$Do6gqybq71LBsCGv.msOQ./p5lvJXU7b4TxqRx.oYdAxYp//WcjAu','admin','2025-09-03 17:44:51'),
(5,'mo','$2b$12$nVdGis9B1TzMJVOpMbw5WeYWDRf9t.9Nw4r26IeOSlI20I3.ezI1C','admin','2025-09-03 17:44:51'),
(6,'test','$2b$12$tuFVds6iqJN.LENfA9EpSubdrDJ.7DlS9STyPTVRVsIEdGpJbh6e6','client','2025-09-03 17:44:51'),
(7,'pogba','$2b$12$F.XHlmMBO971uoHgtPpUp.glb9I3WdXR.HVCi2sLvC8UsZxzPUX2i','client','2025-09-03 17:44:51'),
(8,'isak','$2b$12$ATpwUOX.XzQX6ihnGDBVLuqHgCkyj4Yrx7oEVAWNcf8.Z1dauW6NK','client','2025-09-03 20:42:54'),
(9,'wirtz','$2b$12$pUeu90y1HS5AcWpqgcZe9SUSP1pd2f8T0k.1zoRczq8zd3ZZbnb2','client','2025-09-03 20:42:54'),
(10,'ekitike','$2b$12$pOsgHFbf.700YXuP7oMP2OjFjfvfB1oswNHt/qmPrcaHNjDFPJuQS','client','2025-09-03 20:42:54'),
(11,'sesko','$2b$12$vbZ9keNAfBCymjCAbF6Yz.2tuYVBM2TBy5AkP0Jugk6ODfar4k2Qq','client','2025-09-03 20:42:55'),
(12,'mbeumo','$2b$12$sLqDTbrbcG8fWPQ7kNDYnertJey3hCNHuycxcuUJQxUJZP0DT39vi','client','2025-09-04 00:55:43'),
(13,'osimhen','$2b$12$tRbfKFmcKemCDPkbYQ3VGu0JIb6pZY8bxaXvRCzcUB5cIGo5An5Y','client','2025-09-04 00:55:43'),
(14,'cunha','$2b$12$KVj1Zez4PMfYYqh1AsnOnO8vnnWzmJHwsLuq2M.I6ML9lBA1OKjmK','client','2025-09-04 00:55:44'),
(15,'diaz','$2b$12$1cctPiHyvBxjYQDcErmS.OMZk3F68P23I8LVVAY6ApZEfZNyThXu2','client','2025-09-05 02:20:57'),
(16,'eze','$2b$12$nb9MFMRKdYqplYfn82XkL.nOsbYhRGWfISv9j1dXpAVQ/2pUVhAiq','client','2025-09-05 02:20:58'),
(17,'zabarnyi','$2b$12$BJ9tRIefSLJ1sDP9WoJfXOW7XpAaaRrSDXsB.p7jjMOhxUlxL4Ugm','client','2025-09-05 02:20:58'),
(18,'chevalier','$2b$12$z/b8EyfBfjeWgGbUjIqWse9ZIvpd8zxOsd9jjRk0OqCiFLEBGEsWe','client','2025-09-05 02:20:58'),
(19,'marin','$2b$12$RPsIHPkpR7UcPnXPSaFO2OkVL7O24Z6brUi5dHJaCVhJbFk2eRAAa','client','2025-09-05 02:20:59'),
(20,'donnaruma','$2b$12$J4gt9KuOZFvLIY0Sac/lCuPSrarjTrC5LdaptvdvUze3SN57Kt9QS','client','2025-09-05 12:33:27'),
(21,'gyokeres','$2b$12$.8ZTfw8v7GABix5F7ZRXNO/.IWanowRk.JBlKSi6.f6xpRfp1C/NO','client','2025-09-05 12:33:28');

-- Mise à jour de la séquence pour correspondre à l'id max
SELECT pg_catalog.setval('public.users_id_seq', 21, true);
