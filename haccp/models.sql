BEGIN;
CREATE TABLE "haccp_qualitytest" (
    "id" serial NOT NULL PRIMARY KEY,
    "test_date" date NOT NULL,
    "zone" smallint CHECK ("zone" >= 0) NOT NULL,
    "test_result" numeric(2, 1) NOT NULL
)
;
CREATE TABLE "haccp_watertest" (
    "qualitytest_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "haccp_qualitytest" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "haccp_tobaccobeetletest" (
    "qualitytest_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "haccp_qualitytest" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "haccp_thermometertest" (
    "qualitytest_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "haccp_qualitytest" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
COMMIT;
