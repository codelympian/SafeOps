-- Runs once, when the Postgres volume is first created.
-- A separate database for pytest, so tests never touch dev data.
CREATE DATABASE safeops_test;
\connect safeops_test
CREATE EXTENSION IF NOT EXISTS vector;
