    ALTER TABLE "access_integratedproduct" ADD COLUMN acute_hazard_not_specified varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN acute_hazard_oral varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN acute_hazard_dermal varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN acute_hazard_gases varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN acute_hazard_vapors varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN acute_hazard_dusts_mists varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN germ_cell_mutagenicity_hazard  varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  carcinogenicty_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  reproductive_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN TOST_single_hazard  varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  TOST_repeat_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  aspiration_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  asphyxiation_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  flammable_liquid_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  flamamble_solid_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  self_reactive_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  emit_flammable_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  oxidizing_liquid_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  oxidizing_solid_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  organic_peroxide_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  metal_corrosifve_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  skin_corrosion_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  eye_damage_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  respiratory_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  skin_sensitization_hazard varchar(50) DEFAULT '' NOT NULL;
    
    ALTER TABLE "access_integratedproduct" ADD COLUMN  acute_aquatic_toxicity_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "access_integratedproduct" ADD COLUMN  chronic_aquatic_toxicity_hazard varchar(50) DEFAULT '' NOT NULL;
    
    
    ALTER TABLE newqc_batchsheet ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    ALTER TABLE newqc_batchsheet ADD COLUMN status varchar(25) DEFAULT '' NOT NULL;
    ALTER TABLE newqc_batchsheet ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    ALTER TABLE newqc_batchsheet ADD COLUMN modified_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    ALTER TABLE newqc_testcard ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    ALTER TABLE newqc_testcard ADD COLUMN modified_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    ALTER TABLE newqc_rmtestcard ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    ALTER TABLE newqc_rmtestcard ADD COLUMN modified_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    ALTER TABLE newqc_generictestcard ADD COLUMN create_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    ALTER TABLE newqc_generictestcard ADD COLUMN modified_time timestamp with time zone DEFAULT '2010-01-01' NOT NULL;
    
    
    ALTER TABLE "Raw Materials" ADD COLUMN skin_sensitization_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "Raw Materials" ADD COLUMN  acute_aquatic_toxicity_hazard varchar(50) DEFAULT '' NOT NULL;
    ALTER TABLE "Raw Materials" ADD COLUMN  chronic_aquatic_toxicity_hazard varchar(50) DEFAULT '' NOT NULL;    
    
    ALTER TABLE "access_integratedproduct" ADD COLUMN oral_ld50 numeric(10,3);
    ALTER TABLE "access_integratedproduct" ADD COLUMN dermal_ld50 numeric(10,3);
    ALTER TABLE "access_integratedproduct" ADD COLUMN gases_ld50 numeric(10,3);
    ALTER TABLE "access_integratedproduct" ADD COLUMN vapors_ld50 numeric(10,3);
    ALTER TABLE "access_integratedproduct" ADD COLUMN dusts_mists_ld50 numeric(10,3);
    
    ALTER TABLE "Raw Materials" ADD COLUMN oral_ld50 numeric(10,3);
    ALTER TABLE "Raw Materials" ADD COLUMN dermal_ld50 numeric(10,3);
    ALTER TABLE "Raw Materials" ADD COLUMN gases_ld50 numeric(10,3);
    ALTER TABLE "Raw Materials" ADD COLUMN vapors_ld50 numeric(10,3);
    ALTER TABLE "Raw Materials" ADD COLUMN dusts_mists_ld50 numeric(10,3);   
    
    ALTER TABLE "Raw Materials" RENAME COLUMN "CAS" to "cas";
    
    
    
# NEWQC SQL STATEMENTS

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