
ALTER TABLE newqc_scanneddoc RENAME TO newqc_oldscanneddoc;
ALTER TABLE newqc_testcard RENAME TO newqc_oldtestcard;
ALTER TABLE newqc_rmtestcard RENAME TO newqc_oldrmtestcard;
ALTER TABLE newqc_batchsheet RENAME TO newqc_oldbatchsheet;
ALTER TABLE newqc_generictestcard RENAME TO newqc_oldgenerictestcard;

UPDATE django_content_type SET model='oldscanneddoc' WHERE model='scanneddoc';
UPDATE django_content_type SET model='oldtestcard' WHERE model='testcard';
UPDATE django_content_type SET model='oldgenerictestcard' WHERE model='generictestcard';
UPDATE django_content_type SET model='oldrmtestcard' WHERE model='rmtestcard';

ALTER TABLE newqc_oldgenerictestcard DROP COLUMN status;

# let's the main db user create databases, for example to run tests
ALTER USER "www-data" CREATEDB;

# fixes a defect where django content type names can get too long
ALTER TABLE auth_permission ALTER COLUMN name TYPE varchar(255);


# delete some of these
ALTER TABLE newqc_batchsheet ADD COLUMN status varchar(25) DEFAULT '' NOT NULL;
ALTER TABLE newqc_batchsheet ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
ALTER TABLE newqc_batchsheet ADD COLUMN modified_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
ALTER TABLE newqc_testcard ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
ALTER TABLE newqc_testcard ADD COLUMN modified_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
ALTER TABLE newqc_rmtestcard ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
ALTER TABLE newqc_rmtestcard ADD COLUMN modified_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
ALTER TABLE newqc_generictestcard ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
ALTER TABLE newqc_generictestcard ADD COLUMN modified_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;


ALTER TABLE newqc_scanneddoc ADD COLUMN image_hash varchar(64);
ALTER TABLE newqc_scanneddoc ADD COLUMN large varchar(100);
ALTER TABLE newqc_scanneddoc ADD COLUMN thumbnail varchar(100);
ALTER TABLE newqc_scanneddoc ADD COLUMN notes text;
ALTER TABLE newqc_scanneddoc ADD COLUMN scan_time timestamp with time zone;

