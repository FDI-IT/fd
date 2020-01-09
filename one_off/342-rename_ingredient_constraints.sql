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