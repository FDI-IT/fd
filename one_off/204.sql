ALTER TABLE access_integratedformula ALTER COLUMN acc_flavor DROP NOT NULL;
ALTER TABLE access_integratedformula ALTER COLUMN acc_ingredient DROP NOT NULL;

ALTER TABLE hazard_calculator_ghsingredient ADD COLUMN reach varchar(50) DEFAULT '' NOT NULL;
ALTER TABLE hazard_calculator_ghsingredient ADD COLUMN name text DEFAULT '' NOT NULL;
ALTER TABLE hazard_calculator_ghsingredient ADD COLUMN ghs_hazard_category text DEFAULT '' NOT NULL;
ALTER TABLE hazard_calculator_ghsingredient ADD COLUMN ghs_change_indicators text DEFAULT '' NOT NULL;
ALTER TABLE hazard_calculator_ghsingredient ADD COLUMN ghs_signal_words text DEFAULT '' NOT NULL;
ALTER TABLE hazard_calculator_ghsingredient ADD COLUMN ghs_codes text DEFAULT '' NOT NULL;
ALTER TABLE hazard_calculator_ghsingredient ADD COLUMN ghs_pictogram_codes text DEFAULT '' NOT NULL;
ALTER TABLE hazard_calculator_ghsingredient ADD COLUMN synonyms text DEFAULT '' NOT NULL;
