ALTER TABLE "Raw Materials" RENAME TO "access_ingredient";

ALTER TABLE access_ingredient ADD CONSTRAINT "access_ingredient_ProductID_check" CHECK ("ProductID" >= 0);
ALTER TABLE access_ingredient DROP CONSTRAINT "Raw Materials_ProductID_check";

ALTER TABLE access_ingredient ADD CONSTRAINT "access_ingredient_RawMaterialCode_check" CHECK ("RawMaterialCode" >= 0);
ALTER TABLE access_ingredient DROP CONSTRAINT "Raw Materials_RawMaterialCode_check";

ALTER TABLE access_ingredient ADD CONSTRAINT "access_ingredient_SupplierID_check" CHECK ("SupplierID" >= 0);
ALTER TABLE access_ingredient DROP CONSTRAINT "Raw Materials_SupplierID_check";

ALTER INDEX "Raw Materials_pkey" RENAME TO "access_ingredient_pkey";

ALTER TABLE access_ingredient ADD CONSTRAINT "access_ingredient_sub_flavor_id_fkey" FOREIGN KEY (sub_flavor_id) REFERENCES access_integratedproduct(id) DEFERRABLE;
ALTER TABLE access_ingredient DROP CONSTRAINT "Raw Materials_sub_flavor_id_fkey";


ALTER TABLE newqc_testcard ADD COLUMN qc_time timestamp with time zone;

DROP TABLE hazard_calculator_formulalineitem CASCADE;
DROP TABLE hazard_calculator_hazardcategory CASCADE;
DROP TABLE hazard_calculator_ingredientcategoryinfo CASCADE;
DROP TABLE hazard_calculator_ghsingredient CASCADE;
DROP TABLE hazard_calculator_hazardclass CASCADE;

DELETE FROM access_flavorcategoryinfo;


ALTER TABLE "newqc_rmretain" ADD COLUMN "po_id" integer NULL;
CREATE INDEX newqc_rmretain_c73ffa0a ON "newqc_rmretain" ("po_id");
ALTER TABLE "newqc_rmretain" ADD CONSTRAINT "newqc_rmretain_po_id_266f3ef18e28e50_fk_access_purchaseorder_id" FOREIGN KEY ("po_id") REFERENCES "access_purchaseorder" ("id") DEFERRABLE INITIALLY DEFERRED;


ALTER TABLE reversion_version DROP COLUMN IF EXISTS type ;