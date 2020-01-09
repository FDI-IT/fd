INSERT INTO access_productcategory VALUES (nextval('access_productcategory_id_seq'::regclass), 'Flavor');
INSERT INTO access_productcategory VALUES (nextval('access_productcategory_id_seq'::regclass), 'Base');
INSERT INTO access_productcategory VALUES (nextval('access_productcategory_id_seq'::regclass), 'Syrup');
INSERT INTO access_productcategory VALUES (nextval('access_productcategory_id_seq'::regclass), 'Flavored Syrup');
INSERT INTO access_productcategory VALUES (nextval('access_productcategory_id_seq'::regclass), 'Syrup Base');
INSERT INTO access_productcategory VALUES (nextval('access_productcategory_id_seq'::regclass), 'Rub');
INSERT INTO access_productcategory VALUES (nextval('access_productcategory_id_seq'::regclass), 'Spice Blend');
INSERT INTO access_productcategory VALUES (nextval('access_productcategory_id_seq'::regclass), 'Gastrique');


ALTER TABLE "ExperimentalLog" ADD COLUMN product_category_id integer not null default 1;
ALTER TABLE "ExperimentalLog" ADD CONSTRAINT "ExperimentalLog_productcategory_id_fkey" FOREIGN KEY (product_category_id) references access_productcategory(id);

