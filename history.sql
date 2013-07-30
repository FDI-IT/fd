CREATE USER "www-data";
CREATE DATABASE fd_test with owner="www-data";
ALTER USER postgres WITH PASSWORD='flavor640';
ALTER USER postgres WITH PASSWORD="flavor640";
ALTER USER postgres WITH PASSWORD "flavor640";
ALTER USER postgres WITH PASSWORD 'flavor640';
\q
ALTER USER "www-data" WITH PASSWORD 'flavor640';
\q
alter user dev createdb;
alter user www-data createdb;
alter user 'www-data' createdb;
alter user "www-data" createdb;
\q
\i models.sql 
\q
ALTER TABLE 'Raw Materials' MODIFY 'PRODNUM' integer;
ALTER TABLE "Raw Materials" MODIFY "PRODNUM" integer;
ALTER TABLE "Raw Materials" ALTER "PRODNUM" integer;
ALTER TABLE "Raw Materials" ALTER "PRODNUM" TYPE integer;
ALTER TABLE "Raw Materials" ALTER COLUMN "PRODNUM" TYPE integer USING CASE "PRODNUM"::int end;
ALTER TABLE "Raw Materials" ALTER COLUMN "PRODNUM" TYPE integer USING CASE "PRODNUM"::int END;
ALTER TABLE "Raw Materials" ALTER COLUMN "PRODNUM" TYPE integer USING CASE "PRODNUM"::int;
ALTER TABLE "Raw Materials" ALTER COLUMN "PRODNUM" TYPE integer USING "PRODNUM"::int;
\q
show databases;
select * from pg_database;
select * from pg_database;
\q
use database fd_testselect * from Ingredients;
;
exit;
ALTER TABLE "Suppliers" ALTER COLUMN "SupplierID" DROP CONSTRAINT unique;
\d "Suppliers"
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_Key";
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_Key"
\d "Suppliers"
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_Key"
\d "Suppliers"
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_key"
\d "Suppliers"
\q
\d "Suppliers"
\d "Suppliers"
ALTER TABLE Suppliers DROP CONSTRAINT "Suppliers_SupplierID_key"
\d "Suppliers"
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_check"
\d "Suppliers"
flu;
DROP TABLE flavor_usage_application;
DROP TABLE flavor_usage_applicationtype ;
exit;
exit;
\q
DROP TABLE flavor_usage_application;
\q
DROP TABLE flavor_usage_application;
DROP TABLE flavor_usage_applicationtype ;
\q
CREATE DATABASE mayan_test;
DROP DATABASE mayan_test;
CREATE DATABASE mayan_test OWNER www-data;
CREATE DATABASE mayan_test OWNER "www-data";
select tablename from pg_tables where tableowner='www-data';
BEGIN;DROP TABLE "fdileague_teamstats";
DROP TABLE "fdileague_scoring";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "away_team_id_refs_id_a6d59172";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "home_team_id_refs_id_a6d59172";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";COMMIT;
\q
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";
DROP TABLE "fdileague_player" CASCADE;
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore" CASCASDE;
DROP TABLE "fdileague_yearscore" CASCADE;
DROP TABLE "fdileague_game" CASCADE;
DROP TABLE "fdileague_team" CASCADE;
DROP TABLE "fdileague_teamstats";
DROP TABLE "fdileague_scoring";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";
\q
DROP TABLE fdileague_* CASCADE;
DROP TABLE fdileague_game CASCADE;
DROP TABLE fdileague_player CASCADE;
DROP TABLE fdileague_scoring CASCADE;
DROP TABLE fdileague_team CASCADE;
DROP TABLE fdileague_teamstats CASCADE;
DROP TABLE fdileague_yearscore CASCADE;
DROP TABLE fdileague_game CASCADE;
DROP TABLE fdileague_player CASCADE;
DROP TABLE fdileague_scoring CASCADE;
DROP TABLE fdileague_team CASCADE;
DROP TABLE fdileague_teamstats CASCADE;
DROP TABLE fdileague_yearscore CASCADE;
DROP TABLE fdileague_game CASCADE;
BEGIN;DROP TABLE "fdileague_teamstats";
DROP TABLE "fdileague_scoring";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "away_team_id_refs_id_a6d59172";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "home_team_id_refs_id_a6d59172";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";COMMIT;
\q
BEGIN;DROP TABLE "fdileague_teamstats";
DROP TABLE "fdileague_scoring";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "away_team_id_refs_id_a6d59172";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "home_team_id_refs_id_a6d59172";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";COMMIT;
\q
\d "Products"
\d "Products - Special Information"
\d "Products - Special Information"
select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
ALTER TABLE "Products - Special Information" DROP COLUMN "ProductID";
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
\d "Products - Special Information"
 ALTER TABLE "Products - Special Information" DROP CONSTRAINT PRIMARY KEY ("FlavorNumber");
 ALTER TABLE "Products - Special Information" DROP CONSTRAINT PRIMARY KEY ("FlavorNumber");
 ALTER TABLE "Products - Special Information" DROP CONSTRAINT "Products - Special Information_pkey";
ALTER TABLE "Products - Special Information" ADD COLUMN id integer not null;
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
ALTER TABLE "Products - Special Information" DROP COLUMN "FlavorNumber";
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
\d psitest 
\d "Products - Special Information"
ALTER TABLE "Products - Special Information" DROP COLUMN flavor_id;
ALTER TABLE psitest DROP COLUMN flavor_id;
\d psitest 
\d "Products - Special Information"
\d psitest 
ALTER TABLE psitest OWNER TO www-data;
ALTER TABLE psitest OWNER TO "www-data";
\q
\d "Products"
\d "Products
\d "Products"
ALTER TABLE "Products" DROP COLUMN formulagraph;
ALTER TABLE psitest DROP COLUMN formulagraph ;
select * from "ExperimentalLog" FULL OUTER JOIN "Products" on "ExperimentalLog"."ProductNumber" = "Products"."FlavorNumber";
select COUNT(*) from "ExperimentalLog" FULL OUTER JOIN "Products" on "ExperimentalLog"."ProductNumber" = "Products"."FlavorNumber";
select COUNT(*) from "Products";
select COUNT(*) from "ExperimentalLog";
select * from "ExperimentalLog" FULL OUTER JOIN "Products" on "ExperimentalLog"."ProductNumber" = "Products"."FlavorNumber";
select * from "ExperimentalLog" FULL OUTER JOIN "Products" on "ExperimentalLog"."ProductNumber" = "Products"."FlavorNumber";
ALTER TABLE "ExperimentalLog" RENAME COLUMN "id" TO experimental_id;
\d ExperimentalLog
\d "ExperimentalLog"
ALTER TABLE "ExperimentalLog" RENAME COLUMN experimental_id TO "id";
ALTER TABLE "ExperimentalLog" RENAME COLUMN "ProductName" TO "ExperimentalProductName";
ALTER TABLE "ExperimentalLog" DROP COLUMN "Organic";
ALTER TABLE "ExperimentalLog" DROP COLUMN "SpG";
DROP DATABASE fd_test;
DROP DATABASE fd_test;
DROP DATABASE fd_test;

ALTER TABLE "Products" ALTER COLUMN "CategoryID" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "UnitPrice" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "QuantityPerUnit" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "SupplierID" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "UnitsInStock" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "UnitsOnOrder" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "ReorderLevel" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "LastPrice" DROP NOT NULL;
ALTER TABLE "Products" ADD COLUMN no_pg NOT NULL DEFAULT FALSE;
ALTER TABLE "Products" ADD COLUMN no_pg;
ALTER TABLE "Products" ADD COLUMN no_pg boolean NO NULL DEFAULT FALSE;
ALTER TABLE "Products" ADD COLUMN no_pg boolean NOT NULL DEFAULT FALSE;
ALTER TABLE "newqc_testcard" RENAME COLUMN "jbg_hash" TO "image_hash";


ALTER TABLE "Products" ALTER COLUMN "CategoryID" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "UnitPrice" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "QuantityPerUnit" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "SupplierID" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "UnitsInStock" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "UnitsOnOrder" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "ReorderLevel" DROP NOT NULL;
ALTER TABLE "Products" ALTER COLUMN "LastPrice" DROP NOT NULL;
ALTER TABLE "Products" ADD COLUMN no_pg NOT NULL DEFAULT FALSE;
ALTER TABLE "Products" ADD COLUMN no_pg;
ALTER TABLE "Products" ADD COLUMN no_pg boolean NO NULL DEFAULT FALSE;
ALTER TABLE "Products" ADD COLUMN no_pg boolean NOT NULL DEFAULT FALSE;
ALTER TABLE "newqc_testcard" RENAME COLUMN "jbg_hash" TO "image_hash";
select distinct natart from products;
select distinct natart from Products;
select distinct natart from "Products";
select distinct "Products".natart from "Products";
select distinct "Products"."FlavorNatArt" from "Products";
CREATE USER "www-data";
CREATE DATABASE fd_test with owner="www-data";
ALTER USER postgres WITH PASSWORD='flavor640';
ALTER USER postgres WITH PASSWORD="flavor640";
ALTER USER postgres WITH PASSWORD "flavor640";
ALTER USER postgres WITH PASSWORD 'flavor640';
\q
ALTER USER "www-data" WITH PASSWORD 'flavor640';
\q
alter user dev createdb;
alter user www-data createdb;
alter user 'www-data' createdb;
alter user "www-data" createdb;
\q
\i models.sql 
\q
ALTER TABLE 'Raw Materials' MODIFY 'PRODNUM' integer;
ALTER TABLE "Raw Materials" MODIFY "PRODNUM" integer;
ALTER TABLE "Raw Materials" ALTER "PRODNUM" integer;
ALTER TABLE "Raw Materials" ALTER "PRODNUM" TYPE integer;
ALTER TABLE "Raw Materials" ALTER COLUMN "PRODNUM" TYPE integer USING CASE "PRODNUM"::int end;
ALTER TABLE "Raw Materials" ALTER COLUMN "PRODNUM" TYPE integer USING CASE "PRODNUM"::int END;
ALTER TABLE "Raw Materials" ALTER COLUMN "PRODNUM" TYPE integer USING CASE "PRODNUM"::int;
ALTER TABLE "Raw Materials" ALTER COLUMN "PRODNUM" TYPE integer USING "PRODNUM"::int;
\q
show databases;
select * from pg_database;
select * from pg_database;
\q
use database fd_testselect * from Ingredients;
;
exit;
ALTER TABLE "Suppliers" ALTER COLUMN "SupplierID" DROP CONSTRAINT unique;
\d "Suppliers"
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_Key";
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_Key"
\d "Suppliers"
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_Key"
\d "Suppliers"
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_key"
\d "Suppliers"
\q
\d "Suppliers"
\d "Suppliers"
ALTER TABLE Suppliers DROP CONSTRAINT "Suppliers_SupplierID_key"
\d "Suppliers"
ALTER TABLE "Suppliers" DROP CONSTRAINT "Suppliers_SupplierID_check"
\d "Suppliers"
flu;
DROP TABLE flavor_usage_application;
DROP TABLE flavor_usage_applicationtype ;
exit;
exit;
\q
DROP TABLE flavor_usage_application;
\q
DROP TABLE flavor_usage_application;
DROP TABLE flavor_usage_applicationtype ;
\q
CREATE DATABASE mayan_test;
DROP DATABASE mayan_test;
CREATE DATABASE mayan_test OWNER www-data;
CREATE DATABASE mayan_test OWNER "www-data";
select tablename from pg_tables where tableowner='www-data';
BEGIN;DROP TABLE "fdileague_teamstats";
DROP TABLE "fdileague_scoring";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "away_team_id_refs_id_a6d59172";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "home_team_id_refs_id_a6d59172";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";COMMIT;
\q
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";
DROP TABLE "fdileague_player" CASCADE;
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore" CASCASDE;
DROP TABLE "fdileague_yearscore" CASCADE;
DROP TABLE "fdileague_game" CASCADE;
DROP TABLE "fdileague_team" CASCADE;
DROP TABLE "fdileague_teamstats";
DROP TABLE "fdileague_scoring";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";
\q
DROP TABLE fdileague_* CASCADE;
DROP TABLE fdileague_game CASCADE;
DROP TABLE fdileague_player CASCADE;
DROP TABLE fdileague_scoring CASCADE;
DROP TABLE fdileague_team CASCADE;
DROP TABLE fdileague_teamstats CASCADE;
DROP TABLE fdileague_yearscore CASCADE;
DROP TABLE fdileague_game CASCADE;
DROP TABLE fdileague_player CASCADE;
DROP TABLE fdileague_scoring CASCADE;
DROP TABLE fdileague_team CASCADE;
DROP TABLE fdileague_teamstats CASCADE;
DROP TABLE fdileague_yearscore CASCADE;
DROP TABLE fdileague_game CASCADE;
BEGIN;DROP TABLE "fdileague_teamstats";
DROP TABLE "fdileague_scoring";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "away_team_id_refs_id_a6d59172";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "home_team_id_refs_id_a6d59172";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";COMMIT;
\q
BEGIN;DROP TABLE "fdileague_teamstats";
DROP TABLE "fdileague_scoring";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "away_team_id_refs_id_a6d59172";
ALTER TABLE "fdileague_game" DROP CONSTRAINT "home_team_id_refs_id_a6d59172";
DROP TABLE "fdileague_team";
DROP TABLE "fdileague_game";
DROP TABLE "fdileague_yearscore";
DROP TABLE "fdileague_player";COMMIT;
\q
\d "Products"
\d "Products - Special Information"
\d "Products - Special Information"
select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
ALTER TABLE "Products - Special Information" DROP COLUMN "ProductID";
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
\d "Products - Special Information"
 ALTER TABLE "Products - Special Information" DROP CONSTRAINT PRIMARY KEY ("FlavorNumber");
 ALTER TABLE "Products - Special Information" DROP CONSTRAINT PRIMARY KEY ("FlavorNumber");
 ALTER TABLE "Products - Special Information" DROP CONSTRAINT "Products - Special Information_pkey";
ALTER TABLE "Products - Special Information" ADD COLUMN id integer not null;
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
ALTER TABLE "Products - Special Information" DROP COLUMN "FlavorNumber";
create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
\d psitest 
\d "Products - Special Information"
ALTER TABLE "Products - Special Information" DROP COLUMN flavor_id;
ALTER TABLE psitest DROP COLUMN flavor_id;
\d psitest 
\d "Products - Special Information"
\d psitest 
ALTER TABLE psitest OWNER TO www-data;
ALTER TABLE psitest OWNER TO "www-data";
\q
\d "Products"
\d "Products
\d "Products"
ALTER TABLE "Products" DROP COLUMN formulagraph;
ALTER TABLE psitest DROP COLUMN formulagraph ;
select * from "ExperimentalLog" FULL OUTER JOIN "Products" on "ExperimentalLog"."ProductNumber" = "Products"."FlavorNumber";
select COUNT(*) from "ExperimentalLog" FULL OUTER JOIN "Products" on "ExperimentalLog"."ProductNumber" = "Products"."FlavorNumber";
select COUNT(*) from "Products";
select COUNT(*) from "ExperimentalLog";
select * from "ExperimentalLog" FULL OUTER JOIN "Products" on "ExperimentalLog"."ProductNumber" = "Products"."FlavorNumber";
select * from "ExperimentalLog" FULL OUTER JOIN "Products" on "ExperimentalLog"."ProductNumber" = "Products"."FlavorNumber";
ALTER TABLE "ExperimentalLog" RENAME COLUMN "id" TO experimental_id;
\d ExperimentalLog
\d "ExperimentalLog"
ALTER TABLE "ExperimentalLog" RENAME COLUMN experimental_id TO "id";
ALTER TABLE "ExperimentalLog" RENAME COLUMN "ProductName" TO "ExperimentalProductName";
ALTER TABLE "ExperimentalLog" DROP COLUMN "Organic";
ALTER TABLE "ExperimentalLog" DROP COLUMN "SpG";
DROP DATABASE fd_test;
DROP DATABASE fd_test;
DROP DATABASE fd_test;
