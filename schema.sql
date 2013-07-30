--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: Customers; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Customers" (
    id integer NOT NULL,
    "RPS/UPSNumber" smallint,
    "CompanyName" character varying(40) NOT NULL,
    "BillingAddress" character varying(60),
    "BillingAddress2" character varying(20),
    "BillingCity" character varying(35),
    "BillingState" character varying(2),
    "BillingZip" character varying(10),
    "ShipAddress" character varying(60),
    "ShipAddress2" character varying(20),
    "ShipCity" character varying(35),
    "ShipState" character varying(2),
    "ShipZip" character varying(10),
    "BillingPhone" character varying(24),
    "ShipPhone" character varying(24),
    "BillingFax" character varying(24),
    "ShipFax" character varying(24),
    "CustomerNotes" text,
    "CustomerID" character varying(5),
    "Salesperson" character varying(15),
    "Prefix" character varying(10),
    "AccountingCode" character varying(10),
    "Terms" character varying(10),
    "Country" character varying(15),
    "CategoryID" integer,
    "Fedex" character varying(11),
    "Region" character varying(15),
    "Extension" integer,
    "ContactName" character varying(30) NOT NULL,
    "Gender" character varying(4),
    "ContactTitle" character varying(30),
    "Address" character varying(60),
    "City" character varying(25),
    "PostalCode" character varying(10),
    "Phone" character varying(24),
    "Fax" character varying(24),
    "HomePage" character varying(50),
    "EMail" character varying(50),
    "CustomerType" character varying(10),
    CONSTRAINT "Customers_CategoryID_check" CHECK (("CategoryID" >= 0)),
    CONSTRAINT "Customers_Extension_check" CHECK (("Extension" >= 0)),
    CONSTRAINT "Customers_RPS/UPSNumber_check" CHECK (("RPS/UPSNumber" >= 0))
);


ALTER TABLE public."Customers" OWNER TO "www-data";

--
-- Name: Customers_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE "Customers_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public."Customers_id_seq" OWNER TO "www-data";

--
-- Name: Customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE "Customers_id_seq" OWNED BY "Customers".id;


--
-- Name: Experimental Formulas; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Experimental Formulas" (
    id integer NOT NULL,
    "FlavorNumber" integer NOT NULL,
    "ProductID" integer NOT NULL,
    "FlavorAmount" numeric(7,3) NOT NULL,
    "TotalWeight" numeric(7,3) NOT NULL,
    "FlavorExtendedPrice" numeric(7,3) NOT NULL,
    "Price" numeric(7,3) NOT NULL,
    "Discontinued" boolean NOT NULL,
    "BatchAmount" integer NOT NULL,
    "MachineBatch" integer NOT NULL,
    "RawMaterialCode" integer NOT NULL,
    CONSTRAINT "Experimental Formulas_BatchAmount_check" CHECK (("BatchAmount" >= 0)),
    CONSTRAINT "Experimental Formulas_FlavorNumber_check" CHECK (("FlavorNumber" >= 0)),
    CONSTRAINT "Experimental Formulas_MachineBatch_check" CHECK (("MachineBatch" >= 0)),
    CONSTRAINT "Experimental Formulas_ProductID_check" CHECK (("ProductID" >= 0)),
    CONSTRAINT "Experimental Formulas_RawMaterialCode_check" CHECK (("RawMaterialCode" >= 0))
);


ALTER TABLE public."Experimental Formulas" OWNER TO "www-data";

--
-- Name: Experimental Formulas_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE "Experimental Formulas_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public."Experimental Formulas_id_seq" OWNER TO "www-data";

--
-- Name: Experimental Formulas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE "Experimental Formulas_id_seq" OWNED BY "Experimental Formulas".id;


--
-- Name: Experimental Products; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Experimental Products" (
    "ProductID" integer NOT NULL,
    "FlavorNumber" integer NOT NULL,
    "ProductName" character varying(40) NOT NULL,
    "ProductPrefix" character varying(2) NOT NULL,
    "FlavorCode" character varying(2) NOT NULL,
    "FlavorNatArt" character varying(3) NOT NULL,
    "FlavorType" character varying(25) NOT NULL,
    "CategoryID" integer NOT NULL,
    "UnitPrice" numeric(7,3) NOT NULL,
    "QuantityPerUnit" integer NOT NULL,
    "SupplierID" integer NOT NULL,
    "UnitsInStock" integer NOT NULL,
    "UnitsOnOrder" integer NOT NULL,
    "ReorderLevel" integer NOT NULL,
    "Discontinued" boolean NOT NULL,
    "Approved" boolean NOT NULL,
    "ProductMemo" text NOT NULL,
    "Sold" boolean NOT NULL,
    "SprayDried" boolean NOT NULL,
    "LastPrice" numeric(7,3) NOT NULL,
    "Experimental" character varying(50) NOT NULL,
    "LastSPDate" timestamp with time zone NOT NULL,
    CONSTRAINT "Experimental Products_CategoryID_check" CHECK (("CategoryID" >= 0)),
    CONSTRAINT "Experimental Products_FlavorNumber_check" CHECK (("FlavorNumber" >= 0)),
    CONSTRAINT "Experimental Products_ProductID_check" CHECK (("ProductID" >= 0)),
    CONSTRAINT "Experimental Products_QuantityPerUnit_check" CHECK (("QuantityPerUnit" >= 0)),
    CONSTRAINT "Experimental Products_ReorderLevel_check" CHECK (("ReorderLevel" >= 0)),
    CONSTRAINT "Experimental Products_SupplierID_check" CHECK (("SupplierID" >= 0)),
    CONSTRAINT "Experimental Products_UnitsInStock_check" CHECK (("UnitsInStock" >= 0)),
    CONSTRAINT "Experimental Products_UnitsOnOrder_check" CHECK (("UnitsOnOrder" >= 0))
);


ALTER TABLE public."Experimental Products" OWNER TO "www-data";

--
-- Name: ExperimentalLog; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "ExperimentalLog" (
    id integer NOT NULL,
    "ExperimentalNum" integer NOT NULL,
    "DateSent" timestamp with time zone NOT NULL,
    "Customer" character varying(50),
    "ProductName" character varying(50) NOT NULL,
    "Initials" character varying(2) NOT NULL,
    "Memo" text,
    "Liquid" boolean NOT NULL,
    "Dry" boolean NOT NULL,
    "OilSoluble" boolean NOT NULL,
    "Organic" boolean NOT NULL,
    "Duplication" boolean NOT NULL,
    "N/A" boolean NOT NULL,
    "Natural" boolean NOT NULL,
    "Experimental Number" integer NOT NULL,
    "SpG" numeric(4,3) NOT NULL,
    "Flash" integer NOT NULL,
    "UsageLevel" numeric(6,4) NOT NULL,
    "ProductNumber" integer,
    "Concentrate" boolean NOT NULL,
    "Spray Dried" boolean NOT NULL,
    "Promotable" boolean NOT NULL,
    "Holiday" boolean NOT NULL,
    "Coffee" boolean NOT NULL,
    "Tea" boolean NOT NULL,
    "Fruit" boolean NOT NULL,
    "Sweet" boolean NOT NULL,
    "Nutraceutical" boolean NOT NULL,
    "Personal Care" boolean NOT NULL,
    "Meat and Savory" boolean NOT NULL,
    "Beverage" boolean NOT NULL,
    "Chai" boolean NOT NULL,
    "Baked Goods" boolean NOT NULL,
    "Dairy" boolean NOT NULL,
    "Pet" boolean NOT NULL,
    "Snacks" boolean NOT NULL,
    "Tobacco" boolean NOT NULL,
    "Non-Food" boolean NOT NULL,
    "WONF" boolean NOT NULL,
    "Chef Assist" boolean NOT NULL,
    "Flavor Coat" boolean NOT NULL,
    "RetainNumber" integer,
    "RetainPresent" boolean NOT NULL,
    CONSTRAINT "ExperimentalLog_Experimental Number_check" CHECK (("Experimental Number" >= 0)),
    CONSTRAINT "ExperimentalLog_ExperimentalNum_check" CHECK (("ExperimentalNum" >= 0)),
    CONSTRAINT "ExperimentalLog_Flash_check" CHECK (("Flash" >= 0)),
    CONSTRAINT "ExperimentalLog_ProductNumber_check" CHECK (("ProductNumber" >= 0)),
    CONSTRAINT "ExperimentalLog_RetainNumber_check" CHECK (("RetainNumber" >= 0))
);


ALTER TABLE public."ExperimentalLog" OWNER TO "www-data";

--
-- Name: ExperimentalLog_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE "ExperimentalLog_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public."ExperimentalLog_id_seq" OWNER TO "www-data";

--
-- Name: ExperimentalLog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE "ExperimentalLog_id_seq" OWNED BY "ExperimentalLog".id;


--
-- Name: Flavors - Formulae; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Flavors - Formulae" (
    id integer NOT NULL,
    "FlavorNumber" integer NOT NULL,
    "ProductID" integer NOT NULL,
    flavor_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    "FlavorAmount" numeric(7,3) NOT NULL,
    "TotalWeight" numeric(7,3) NOT NULL,
    "FlavorExtendedPrice" numeric(7,3) NOT NULL,
    "Price" numeric(7,3) NOT NULL,
    "Discontinued" boolean NOT NULL,
    "BatchAmount" integer NOT NULL,
    "MachineBatch" integer NOT NULL,
    "RawMaterialCode" integer NOT NULL,
    CONSTRAINT "Flavors - Formulae_BatchAmount_check" CHECK (("BatchAmount" >= 0)),
    CONSTRAINT "Flavors - Formulae_FlavorNumber_check" CHECK (("FlavorNumber" >= 0)),
    CONSTRAINT "Flavors - Formulae_MachineBatch_check" CHECK (("MachineBatch" >= 0)),
    CONSTRAINT "Flavors - Formulae_ProductID_check" CHECK (("ProductID" >= 0)),
    CONSTRAINT "Flavors - Formulae_RawMaterialCode_check" CHECK (("RawMaterialCode" >= 0))
);


ALTER TABLE public."Flavors - Formulae" OWNER TO "www-data";

--
-- Name: Flavors - Formulae_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE "Flavors - Formulae_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public."Flavors - Formulae_id_seq" OWNER TO "www-data";

--
-- Name: Flavors - Formulae_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE "Flavors - Formulae_id_seq" OWNED BY "Flavors - Formulae".id;


--
-- Name: Incoming; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Incoming" (
    "IncomingID" integer NOT NULL,
    "IncDate" timestamp with time zone NOT NULL,
    "IncName" character varying(50) NOT NULL,
    "IncCompany" character varying(50) NOT NULL,
    "IncID" character varying(50) NOT NULL,
    "IncMemo" text NOT NULL,
    CONSTRAINT "Incoming_IncomingID_check" CHECK (("IncomingID" >= 0))
);


ALTER TABLE public."Incoming" OWNER TO "www-data";

--
-- Name: Products; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Products" (
    "ProductID" integer NOT NULL,
    "FlavorNumber" integer NOT NULL,
    "Solvent" character varying(50) NOT NULL,
    "ProductName" character varying(40) NOT NULL,
    "ProductPrefix" character varying(2) NOT NULL,
    "FlavorCode" character varying(3) NOT NULL,
    "FlavorNatArt" character varying(3) NOT NULL,
    "FlavorType" character varying(25) NOT NULL,
    "CategoryID" integer,
    "UnitPrice" numeric(7,3),
    "QuantityPerUnit" integer,
    "SupplierID" integer,
    "UnitsInStock" integer,
    "UnitsOnOrder" integer,
    "ReorderLevel" integer,
    "Discontinued" boolean NOT NULL,
    "Approved" boolean NOT NULL,
    "ProductMemo" text NOT NULL,
    "Sold" boolean NOT NULL,
    "SprayDried" boolean NOT NULL,
    "LastPrice" numeric(7,3),
    "Experimental" character varying(50) NOT NULL,
    "LastSPDate" timestamp with time zone NOT NULL,
    rawmaterialcost numeric(7,3),
    formulagraph text,
    valid boolean NOT NULL,
    no_pg boolean DEFAULT false NOT NULL,
    CONSTRAINT "Products_CategoryID_check" CHECK (("CategoryID" >= 0)),
    CONSTRAINT "Products_FlavorNumber_check" CHECK (("FlavorNumber" >= 0)),
    CONSTRAINT "Products_ProductID_check" CHECK (("ProductID" >= 0)),
    CONSTRAINT "Products_QuantityPerUnit_check" CHECK (("QuantityPerUnit" >= 0)),
    CONSTRAINT "Products_ReorderLevel_check" CHECK (("ReorderLevel" >= 0)),
    CONSTRAINT "Products_SupplierID_check" CHECK (("SupplierID" >= 0)),
    CONSTRAINT "Products_UnitsInStock_check" CHECK (("UnitsInStock" >= 0)),
    CONSTRAINT "Products_UnitsOnOrder_check" CHECK (("UnitsOnOrder" >= 0))
);


ALTER TABLE public."Products" OWNER TO "www-data";

--
-- Name: Products - Special Information; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Products - Special Information" (
    "FlavorNumber" integer NOT NULL,
    "ProductID" integer NOT NULL,
    flavor_id integer,
    "FlashPoint" integer NOT NULL,
    "Kosher" character varying(20) NOT NULL,
    "Solubility" character varying(25) NOT NULL,
    "Stability" character varying(25) NOT NULL,
    "Nutri on File" boolean NOT NULL,
    "Flammability" character varying(40) NOT NULL,
    "Allergen" character varying(50) NOT NULL,
    "Yield" integer NOT NULL,
    "PINNumber" integer,
    "Kosher_ID" character varying(15) NOT NULL,
    "Label_Check" boolean NOT NULL,
    "VaporPressure" numeric(4,2) NOT NULL,
    "ReactionExtraction" boolean NOT NULL,
    "PROP 65" character varying(50) NOT NULL,
    "GMO" character varying(50) NOT NULL,
    "CCP1" boolean NOT NULL,
    "CCP2" boolean NOT NULL,
    "CCP3" boolean NOT NULL,
    "CCP4" boolean NOT NULL,
    "CCP5" boolean NOT NULL,
    "CCP6" boolean NOT NULL,
    "HACCP" smallint,
    "BATFNo" character varying(50) NOT NULL,
    "MicroTest" character varying(4) NOT NULL,
    "Crustacean" boolean NOT NULL,
    "Eggs" boolean NOT NULL,
    "Fish" boolean NOT NULL,
    "Milk" boolean NOT NULL,
    "Peanuts" boolean NOT NULL,
    "Soybeans" boolean NOT NULL,
    "TreeNuts" boolean NOT NULL,
    "Wheat" boolean NOT NULL,
    "Sulfites" boolean NOT NULL,
    "Organic" boolean NOT NULL,
    "Diacetyl" boolean NOT NULL,
    "Entered" timestamp with time zone NOT NULL,
    sunflower boolean,
    sesame boolean,
    mollusks boolean,
    mustard boolean,
    celery boolean,
    lupines boolean,
    yellow_5 boolean,
    CONSTRAINT "Products - Special Information_FlashPoint_check" CHECK (("FlashPoint" >= 0)),
    CONSTRAINT "Products - Special Information_FlavorNumber_check" CHECK (("FlavorNumber" >= 0)),
    CONSTRAINT "Products - Special Information_HACCP_check" CHECK (("HACCP" >= 0)),
    CONSTRAINT "Products - Special Information_PINNumber_check" CHECK (("PINNumber" >= 0)),
    CONSTRAINT "Products - Special Information_ProductID_check" CHECK (("ProductID" >= 0)),
    CONSTRAINT "Products - Special Information_Yield_check" CHECK (("Yield" >= 0))
);


ALTER TABLE public."Products - Special Information" OWNER TO "www-data";

--
-- Name: Purchases; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Purchases" (
    "POEntry" integer NOT NULL,
    "ShipperID" integer,
    "ShipToID" integer,
    "SupplierCode" character varying(50),
    "OrderID" integer,
    "RawMaterialCode" integer,
    "DateOrdered" date,
    "DateReceived" date,
    "POMemo" text,
    "PONumber" integer,
    "POQuantity" numeric(7,2),
    "PODueDate" date,
    "PackageSize" numeric(7,3) NOT NULL,
    "POMEMO2" text,
    CONSTRAINT "Purchases_OrderID_check" CHECK (("OrderID" >= 0)),
    CONSTRAINT "Purchases_POEntry_check" CHECK (("POEntry" >= 0)),
    CONSTRAINT "Purchases_PONumber_check" CHECK (("PONumber" >= 0)),
    CONSTRAINT "Purchases_RawMaterialCode_check" CHECK (("RawMaterialCode" >= 0)),
    CONSTRAINT "Purchases_ShipToID_check" CHECK (("ShipToID" >= 0)),
    CONSTRAINT "Purchases_ShipperID_check" CHECK (("ShipperID" >= 0))
);


ALTER TABLE public."Purchases" OWNER TO "www-data";

--
-- Name: Raw Materials; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Raw Materials" (
    "ProductID" integer NOT NULL,
    "LSTPRICDAT" timestamp with time zone NOT NULL,
    "ProductName" character varying(60) NOT NULL,
    "PART_NAME2" character varying(60) NOT NULL,
    "DESCRIPT" character varying(60) NOT NULL,
    "Date_Ordered" timestamp with time zone NOT NULL,
    "LEAD_TIME" numeric(6,2) NOT NULL,
    "UnitsOnOrder" numeric(6,2) NOT NULL,
    "UnitsInStock" numeric(6,2) NOT NULL,
    "Discontinued" boolean NOT NULL,
    "UnitPrice" numeric(10,3) NOT NULL,
    "PREFIX" character varying(60) NOT NULL,
    "COMMENTS" text NOT NULL,
    "COMMITTED" numeric(6,2) NOT NULL,
    "CAS" character varying(15) NOT NULL,
    "FEMA" character varying(15) NOT NULL,
    "ART_NATI" character varying(3) NOT NULL,
    "KOSHER" character varying(15) NOT NULL,
    "ReorderLevel" numeric(6,2) NOT NULL,
    "LASTKOSHDT" timestamp with time zone NOT NULL,
    "PRODNUM" integer,
    sub_flavor_id integer,
    "SOLUTION" numeric(5,3) NOT NULL,
    "SOLVENT" character varying(10) NOT NULL,
    "SupplierCode" character varying(50) NOT NULL,
    "SupplierID" integer NOT NULL,
    "GMO" character varying(50) NOT NULL,
    "Natural_Document_On_File" boolean NOT NULL,
    "Allergen" character varying(50) NOT NULL,
    "Sprayed" boolean NOT NULL,
    "InventoryNG" boolean NOT NULL,
    "Kencheck" boolean NOT NULL,
    "Kosher Code" character varying(50) NOT NULL,
    "FLDR" character varying(50) NOT NULL,
    "Microsensitive" character varying(20) NOT NULL,
    "Prop65" boolean NOT NULL,
    "Nutri" boolean NOT NULL,
    "TransFat" boolean NOT NULL,
    "RawMaterialCode" integer NOT NULL,
    eggs boolean,
    fish boolean,
    milk boolean,
    peanuts boolean,
    soybeans boolean,
    treenuts boolean,
    wheat boolean,
    sulfites boolean,
    sunflower boolean,
    sesame boolean,
    mollusks boolean,
    mustard boolean,
    celery boolean,
    lupines boolean,
    yellow_5 boolean,
    crustacean boolean,
    has_allergen_text boolean,
    CONSTRAINT "Raw Materials_ProductID_check" CHECK (("ProductID" >= 0)),
    CONSTRAINT "Raw Materials_RawMaterialCode_check" CHECK (("RawMaterialCode" >= 0)),
    CONSTRAINT "Raw Materials_SupplierID_check" CHECK (("SupplierID" >= 0))
);


ALTER TABLE public."Raw Materials" OWNER TO "www-data";

--
-- Name: ShipTo; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "ShipTo" (
    "ShipToID" integer NOT NULL,
    "ShipToAddress" character varying(50) NOT NULL,
    "ShipToContact" character varying(50) NOT NULL,
    "ShipToCity" character varying(50) NOT NULL,
    "ShipToRegion" character varying(50) NOT NULL,
    "ShipToPostalCode" character varying(50) NOT NULL,
    "ShipToCountry" character varying(50) NOT NULL,
    "ShipToPhone" character varying(50) NOT NULL,
    "ShipToFax" character varying(50) NOT NULL,
    "ShipToContactTitle" character varying(50) NOT NULL,
    "ShipToName" character varying(50) NOT NULL,
    CONSTRAINT "ShipTo_ShipToID_check" CHECK (("ShipToID" >= 0))
);


ALTER TABLE public."ShipTo" OWNER TO "www-data";

--
-- Name: Shippers; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Shippers" (
    "ShipperID" integer NOT NULL,
    "Shipper Name" character varying(40) NOT NULL,
    "Phone" character varying(24) NOT NULL,
    CONSTRAINT "Shippers_ShipperID_check" CHECK (("ShipperID" >= 0))
);


ALTER TABLE public."Shippers" OWNER TO "www-data";

--
-- Name: Suppliers; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE "Suppliers" (
    "ID" integer NOT NULL,
    "SupplierCode" character varying(255) NOT NULL,
    "SupplierName" character varying(255) NOT NULL,
    "ContactName" character varying(255) NOT NULL,
    "ContactTitle" character varying(255) NOT NULL,
    "Address" character varying(255) NOT NULL,
    "City" character varying(255) NOT NULL,
    "Region" character varying(255) NOT NULL,
    "PostalCode" character varying(255) NOT NULL,
    "Country" character varying(255) NOT NULL,
    "Phone" character varying(255) NOT NULL,
    "Fax" character varying(255) NOT NULL,
    "SupplierID" integer,
    "RawMaterialCode" integer,
    "HomePage" character varying(255) NOT NULL,
    "EMail" character varying(255) NOT NULL,
    CONSTRAINT "Suppliers_ID_check" CHECK (("ID" >= 0)),
    CONSTRAINT "Suppliers_RawMaterialCode_check" CHECK (("RawMaterialCode" >= 0)),
    CONSTRAINT "Suppliers_SupplierID_check" CHECK (("SupplierID" >= 0))
);


ALTER TABLE public."Suppliers" OWNER TO "www-data";

--
-- Name: access_epsiformula; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE access_epsiformula (
    id integer NOT NULL,
    flavor_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    amount numeric(7,3) NOT NULL,
    totalweight numeric(7,3) NOT NULL,
    flavorextendedprice numeric(7,3) NOT NULL,
    price numeric(7,3) NOT NULL,
    discontinued boolean NOT NULL,
    batchamount integer NOT NULL,
    machinebatch integer NOT NULL,
    rawmaterialcode integer NOT NULL,
    CONSTRAINT access_epsiformula_batchamount_check CHECK ((batchamount >= 0)),
    CONSTRAINT access_epsiformula_machinebatch_check CHECK ((machinebatch >= 0)),
    CONSTRAINT access_epsiformula_rawmaterialcode_check CHECK ((rawmaterialcode >= 0))
);


ALTER TABLE public.access_epsiformula OWNER TO "www-data";

--
-- Name: access_epsiformula_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE access_epsiformula_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.access_epsiformula_id_seq OWNER TO "www-data";

--
-- Name: access_epsiformula_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE access_epsiformula_id_seq OWNED BY access_epsiformula.id;


--
-- Name: access_flavoriterorder; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE access_flavoriterorder (
    id integer NOT NULL,
    flavor_id integer NOT NULL
);


ALTER TABLE public.access_flavoriterorder OWNER TO "www-data";

--
-- Name: access_flavoriterorder_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE access_flavoriterorder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.access_flavoriterorder_id_seq OWNER TO "www-data";

--
-- Name: access_flavoriterorder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE access_flavoriterorder_id_seq OWNED BY access_flavoriterorder.id;


--
-- Name: access_formulatree; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE access_formulatree (
    id integer NOT NULL,
    root_flavor_id integer NOT NULL,
    lft smallint NOT NULL,
    rgt smallint NOT NULL,
    formula_row_id integer,
    node_ingredient_id integer,
    node_flavor_id integer,
    row_id smallint,
    parent_id smallint,
    weight numeric(7,3) NOT NULL,
    weight_factor numeric(16,15) NOT NULL,
    leaf boolean NOT NULL,
    CONSTRAINT access_formulatree_lft_check CHECK ((lft >= 0)),
    CONSTRAINT access_formulatree_parent_id_check CHECK ((parent_id >= 0)),
    CONSTRAINT access_formulatree_rgt_check CHECK ((rgt >= 0)),
    CONSTRAINT access_formulatree_row_id_check CHECK ((row_id >= 0))
);


ALTER TABLE public.access_formulatree OWNER TO "www-data";

--
-- Name: access_formulatree_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE access_formulatree_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.access_formulatree_id_seq OWNER TO "www-data";

--
-- Name: access_formulatree_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE access_formulatree_id_seq OWNED BY access_formulatree.id;


--
-- Name: access_leafweight; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE access_leafweight (
    id integer NOT NULL,
    root_flavor_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    weight numeric(7,3) NOT NULL
);


ALTER TABLE public.access_leafweight OWNER TO "www-data";

--
-- Name: access_leafweight_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE access_leafweight_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.access_leafweight_id_seq OWNER TO "www-data";

--
-- Name: access_leafweight_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE access_leafweight_id_seq OWNED BY access_leafweight.id;


--
-- Name: access_purchaseorder; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE access_purchaseorder (
    id integer NOT NULL,
    number integer NOT NULL,
    shipper_id integer NOT NULL,
    ship_to_id integer NOT NULL,
    supplier_id integer NOT NULL,
    date_ordered date NOT NULL,
    memo text NOT NULL,
    memo2 text NOT NULL,
    due_date date NOT NULL,
    CONSTRAINT access_purchaseorder_number_check CHECK ((number >= 0))
);


ALTER TABLE public.access_purchaseorder OWNER TO "www-data";

--
-- Name: access_purchaseorder_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE access_purchaseorder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.access_purchaseorder_id_seq OWNER TO "www-data";

--
-- Name: access_purchaseorder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE access_purchaseorder_id_seq OWNED BY access_purchaseorder.id;


--
-- Name: access_purchaseorderlineitem; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE access_purchaseorderlineitem (
    id integer NOT NULL,
    po_id integer NOT NULL,
    raw_material_id integer NOT NULL,
    date_received timestamp with time zone NOT NULL,
    memo text NOT NULL,
    memo2 text NOT NULL,
    quantity numeric(7,2) NOT NULL,
    due_date date NOT NULL,
    package_size numeric(7,3) NOT NULL,
    purchase_price numeric(10,3) NOT NULL,
    legacy_purchase_id integer NOT NULL
);


ALTER TABLE public.access_purchaseorderlineitem OWNER TO "www-data";

--
-- Name: access_purchaseorderlineitem_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE access_purchaseorderlineitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.access_purchaseorderlineitem_id_seq OWNER TO "www-data";

--
-- Name: access_purchaseorderlineitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE access_purchaseorderlineitem_id_seq OWNED BY access_purchaseorderlineitem.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO "www-data";

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO "www-data";

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO "www-data";

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO "www-data";

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_message; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE auth_message (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.auth_message OWNER TO "www-data";

--
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_message_id_seq OWNER TO "www-data";

--
-- Name: auth_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE auth_message_id_seq OWNED BY auth_message.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO "www-data";

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO "www-data";

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(75) NOT NULL,
    password character varying(128) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp with time zone NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO "www-data";

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO "www-data";

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO "www-data";

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO "www-data";

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO "www-data";

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO "www-data";

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO "www-data";

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO "www-data";

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_comment_flags; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE django_comment_flags (
    id integer NOT NULL,
    user_id integer NOT NULL,
    comment_id integer NOT NULL,
    flag character varying(30) NOT NULL,
    flag_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_comment_flags OWNER TO "www-data";

--
-- Name: django_comment_flags_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE django_comment_flags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_comment_flags_id_seq OWNER TO "www-data";

--
-- Name: django_comment_flags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE django_comment_flags_id_seq OWNED BY django_comment_flags.id;


--
-- Name: django_comments; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE django_comments (
    id integer NOT NULL,
    content_type_id integer NOT NULL,
    object_pk text NOT NULL,
    site_id integer NOT NULL,
    user_id integer,
    user_name character varying(50) NOT NULL,
    user_email character varying(75) NOT NULL,
    user_url character varying(200) NOT NULL,
    comment text NOT NULL,
    submit_date timestamp with time zone NOT NULL,
    ip_address inet,
    is_public boolean NOT NULL,
    is_removed boolean NOT NULL
);


ALTER TABLE public.django_comments OWNER TO "www-data";

--
-- Name: django_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE django_comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_comments_id_seq OWNER TO "www-data";

--
-- Name: django_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE django_comments_id_seq OWNED BY django_comments.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO "www-data";

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO "www-data";

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO "www-data";

--
-- Name: django_site; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.django_site OWNER TO "www-data";

--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_site_id_seq OWNER TO "www-data";

--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: djcelery_crontabschedule; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE djcelery_crontabschedule (
    id integer NOT NULL,
    minute character varying(64) NOT NULL,
    hour character varying(64) NOT NULL,
    day_of_week character varying(64) NOT NULL
);


ALTER TABLE public.djcelery_crontabschedule OWNER TO "www-data";

--
-- Name: djcelery_crontabschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE djcelery_crontabschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.djcelery_crontabschedule_id_seq OWNER TO "www-data";

--
-- Name: djcelery_crontabschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE djcelery_crontabschedule_id_seq OWNED BY djcelery_crontabschedule.id;


--
-- Name: djcelery_intervalschedule; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE djcelery_intervalschedule (
    id integer NOT NULL,
    every integer NOT NULL,
    period character varying(24) NOT NULL
);


ALTER TABLE public.djcelery_intervalschedule OWNER TO "www-data";

--
-- Name: djcelery_intervalschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE djcelery_intervalschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.djcelery_intervalschedule_id_seq OWNER TO "www-data";

--
-- Name: djcelery_intervalschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE djcelery_intervalschedule_id_seq OWNED BY djcelery_intervalschedule.id;


--
-- Name: djcelery_periodictask; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE djcelery_periodictask (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    task character varying(200) NOT NULL,
    interval_id integer,
    crontab_id integer,
    args text NOT NULL,
    kwargs text NOT NULL,
    queue character varying(200),
    exchange character varying(200),
    routing_key character varying(200),
    expires timestamp with time zone,
    enabled boolean NOT NULL,
    last_run_at timestamp with time zone,
    total_run_count integer NOT NULL,
    date_changed timestamp with time zone NOT NULL,
    CONSTRAINT djcelery_periodictask_total_run_count_check CHECK ((total_run_count >= 0))
);


ALTER TABLE public.djcelery_periodictask OWNER TO "www-data";

--
-- Name: djcelery_periodictask_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE djcelery_periodictask_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.djcelery_periodictask_id_seq OWNER TO "www-data";

--
-- Name: djcelery_periodictask_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE djcelery_periodictask_id_seq OWNED BY djcelery_periodictask.id;


--
-- Name: djcelery_periodictasks; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE djcelery_periodictasks (
    ident smallint NOT NULL,
    last_update timestamp with time zone NOT NULL
);


ALTER TABLE public.djcelery_periodictasks OWNER TO "www-data";

--
-- Name: djcelery_taskstate; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE djcelery_taskstate (
    id integer NOT NULL,
    state character varying(64) NOT NULL,
    task_id character varying(36) NOT NULL,
    name character varying(200),
    tstamp timestamp with time zone NOT NULL,
    args text,
    kwargs text,
    eta timestamp with time zone,
    expires timestamp with time zone,
    result text,
    traceback text,
    runtime double precision,
    retries integer NOT NULL,
    worker_id integer,
    hidden boolean NOT NULL
);


ALTER TABLE public.djcelery_taskstate OWNER TO "www-data";

--
-- Name: djcelery_taskstate_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE djcelery_taskstate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.djcelery_taskstate_id_seq OWNER TO "www-data";

--
-- Name: djcelery_taskstate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE djcelery_taskstate_id_seq OWNED BY djcelery_taskstate.id;


--
-- Name: djcelery_workerstate; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE djcelery_workerstate (
    id integer NOT NULL,
    hostname character varying(255) NOT NULL,
    last_heartbeat timestamp with time zone
);


ALTER TABLE public.djcelery_workerstate OWNER TO "www-data";

--
-- Name: djcelery_workerstate_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE djcelery_workerstate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.djcelery_workerstate_id_seq OWNER TO "www-data";

--
-- Name: djcelery_workerstate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE djcelery_workerstate_id_seq OWNED BY djcelery_workerstate.id;


--
-- Name: docvault_doc; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE docvault_doc (
    id integer NOT NULL,
    date timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    mailbox smallint NOT NULL,
    CONSTRAINT docvault_doc_mailbox_check CHECK ((mailbox >= 0))
);


ALTER TABLE public.docvault_doc OWNER TO "www-data";

--
-- Name: docvault_doc_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE docvault_doc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.docvault_doc_id_seq OWNER TO "www-data";

--
-- Name: docvault_doc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE docvault_doc_id_seq OWNED BY docvault_doc.id;


--
-- Name: docvault_page; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE docvault_page (
    id integer NOT NULL,
    doc_id integer NOT NULL,
    image character varying(100) NOT NULL,
    hash character varying(64) NOT NULL
);


ALTER TABLE public.docvault_page OWNER TO "www-data";

--
-- Name: docvault_page_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE docvault_page_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.docvault_page_id_seq OWNER TO "www-data";

--
-- Name: docvault_page_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE docvault_page_id_seq OWNED BY docvault_page.id;


--
-- Name: epsitest; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE epsitest (
    "ProductID" integer NOT NULL,
    "FlavorNumber" integer NOT NULL,
    "Solvent" character varying(50) NOT NULL,
    "ProductName" character varying(40) NOT NULL,
    "ProductPrefix" character varying(2) NOT NULL,
    "FlavorCode" character varying(3) NOT NULL,
    "FlavorNatArt" character varying(3) NOT NULL,
    "FlavorType" character varying(25) NOT NULL,
    "CategoryID" integer,
    "UnitPrice" numeric(7,3),
    "QuantityPerUnit" integer,
    "SupplierID" integer,
    "UnitsInStock" integer,
    "UnitsOnOrder" integer,
    "ReorderLevel" integer,
    "Discontinued" boolean NOT NULL,
    "Approved" boolean NOT NULL,
    no_pg boolean NOT NULL,
    "ProductMemo" text NOT NULL,
    "Sold" boolean NOT NULL,
    "SprayDried" boolean NOT NULL,
    "LastPrice" numeric(7,3),
    "Experimental" character varying(50) NOT NULL,
    "LastSPDate" timestamp with time zone NOT NULL,
    rawmaterialcost numeric(7,3),
    valid boolean NOT NULL,
    "FlashPoint" integer NOT NULL,
    "Kosher" character varying(20) NOT NULL,
    "Solubility" character varying(25) NOT NULL,
    "Stability" character varying(25) NOT NULL,
    "Nutri on File" boolean NOT NULL,
    "Flammability" character varying(40) NOT NULL,
    "Allergen" character varying(50) NOT NULL,
    "Yield" integer NOT NULL,
    "PINNumber" integer,
    "Kosher_ID" character varying(15) NOT NULL,
    "Label_Check" boolean NOT NULL,
    "VaporPressure" numeric(4,2) NOT NULL,
    "ReactionExtraction" boolean NOT NULL,
    "PROP 65" character varying(50) NOT NULL,
    "GMO" character varying(50) NOT NULL,
    "CCP1" boolean NOT NULL,
    "CCP2" boolean NOT NULL,
    "CCP3" boolean NOT NULL,
    "CCP4" boolean NOT NULL,
    "CCP5" boolean NOT NULL,
    "CCP6" boolean NOT NULL,
    "HACCP" smallint,
    "BATFNo" character varying(50) NOT NULL,
    "MicroTest" character varying(4) NOT NULL,
    "Crustacean" boolean NOT NULL,
    "Eggs" boolean NOT NULL,
    "Fish" boolean NOT NULL,
    "Milk" boolean NOT NULL,
    "Peanuts" boolean NOT NULL,
    "Soybeans" boolean NOT NULL,
    "TreeNuts" boolean NOT NULL,
    "Wheat" boolean NOT NULL,
    "Sulfites" boolean NOT NULL,
    "Organic" boolean NOT NULL,
    "Diacetyl" boolean NOT NULL,
    "Entered" timestamp with time zone NOT NULL,
    spg numeric(4,3),
    sunflower boolean NOT NULL,
    sesame boolean NOT NULL,
    mollusks boolean NOT NULL,
    mustard boolean NOT NULL,
    celery boolean NOT NULL,
    lupines boolean NOT NULL,
    yellow_5 boolean NOT NULL,
    "ExperimentalNum" integer NOT NULL,
    "DateSent" timestamp with time zone NOT NULL,
    "Customer" character varying(50),
    "ExperimentalProductName" character varying(50) NOT NULL,
    "Initials" character varying(2) NOT NULL,
    "Memo" text,
    "Liquid" boolean NOT NULL,
    "Dry" boolean NOT NULL,
    "OilSoluble" boolean NOT NULL,
    "Duplication" boolean NOT NULL,
    "N/A" boolean NOT NULL,
    "Natural" boolean NOT NULL,
    "Experimental Number" integer NOT NULL,
    "Flash" integer NOT NULL,
    "UsageLevel" numeric(6,4) NOT NULL,
    "ProductNumber" integer,
    "Concentrate" boolean NOT NULL,
    "Spray Dried" boolean NOT NULL,
    "Promotable" boolean NOT NULL,
    "Holiday" boolean NOT NULL,
    "Coffee" boolean NOT NULL,
    "Tea" boolean NOT NULL,
    "Fruit" boolean NOT NULL,
    "Sweet" boolean NOT NULL,
    "Nutraceutical" boolean NOT NULL,
    "Personal Care" boolean NOT NULL,
    "Meat and Savory" boolean NOT NULL,
    "Beverage" boolean NOT NULL,
    "Chai" boolean NOT NULL,
    "Baked Goods" boolean NOT NULL,
    "Dairy" boolean NOT NULL,
    "Pet" boolean NOT NULL,
    "Snacks" boolean NOT NULL,
    "Tobacco" boolean NOT NULL,
    "Non-Food" boolean NOT NULL,
    "WONF" boolean NOT NULL,
    "Chef Assist" boolean NOT NULL,
    "Flavor Coat" boolean NOT NULL,
    "RetainNumber" integer,
    "RetainPresent" boolean NOT NULL,
    CONSTRAINT "epsitest_CategoryID_check" CHECK (("CategoryID" >= 0)),
    CONSTRAINT "epsitest_Experimental Number_check" CHECK (("Experimental Number" >= 0)),
    CONSTRAINT "epsitest_ExperimentalNum_check" CHECK (("ExperimentalNum" >= 0)),
    CONSTRAINT "epsitest_FlashPoint_check" CHECK (("FlashPoint" >= 0)),
    CONSTRAINT "epsitest_Flash_check" CHECK (("Flash" >= 0)),
    CONSTRAINT "epsitest_FlavorNumber_check" CHECK (("FlavorNumber" >= 0)),
    CONSTRAINT "epsitest_HACCP_check" CHECK (("HACCP" >= 0)),
    CONSTRAINT "epsitest_PINNumber_check" CHECK (("PINNumber" >= 0)),
    CONSTRAINT "epsitest_ProductID_check" CHECK (("ProductID" >= 0)),
    CONSTRAINT "epsitest_ProductNumber_check" CHECK (("ProductNumber" >= 0)),
    CONSTRAINT "epsitest_QuantityPerUnit_check" CHECK (("QuantityPerUnit" >= 0)),
    CONSTRAINT "epsitest_ReorderLevel_check" CHECK (("ReorderLevel" >= 0)),
    CONSTRAINT "epsitest_RetainNumber_check" CHECK (("RetainNumber" >= 0)),
    CONSTRAINT "epsitest_SupplierID_check" CHECK (("SupplierID" >= 0)),
    CONSTRAINT "epsitest_UnitsInStock_check" CHECK (("UnitsInStock" >= 0)),
    CONSTRAINT "epsitest_UnitsOnOrder_check" CHECK (("UnitsOnOrder" >= 0)),
    CONSTRAINT "epsitest_Yield_check" CHECK (("Yield" >= 0))
);


ALTER TABLE public.epsitest OWNER TO "www-data";

--
-- Name: fdileague_game; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE fdileague_game (
    id integer NOT NULL,
    html_file character varying(100) NOT NULL,
    game_date date NOT NULL,
    week smallint NOT NULL,
    CONSTRAINT fdileague_game_week_check CHECK ((week >= 0))
);


ALTER TABLE public.fdileague_game OWNER TO "www-data";

--
-- Name: fdileague_game_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE fdileague_game_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.fdileague_game_id_seq OWNER TO "www-data";

--
-- Name: fdileague_game_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE fdileague_game_id_seq OWNED BY fdileague_game.id;


--
-- Name: fdileague_player; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE fdileague_player (
    id integer NOT NULL,
    lastname character varying(100) NOT NULL,
    firstname character varying(100) NOT NULL,
    "position" character varying(5) NOT NULL
);


ALTER TABLE public.fdileague_player OWNER TO "www-data";

--
-- Name: fdileague_player_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE fdileague_player_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.fdileague_player_id_seq OWNER TO "www-data";

--
-- Name: fdileague_player_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE fdileague_player_id_seq OWNED BY fdileague_player.id;


--
-- Name: fdileague_scoring; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE fdileague_scoring (
    id integer NOT NULL,
    game_id integer NOT NULL,
    quarter smallint NOT NULL,
    team_id integer NOT NULL,
    type character varying(20) NOT NULL,
    summary text NOT NULL,
    points smallint NOT NULL,
    scorer_id integer,
    yardage smallint,
    qb_id integer,
    extra_point_id integer,
    reason text NOT NULL,
    CONSTRAINT fdileague_scoring_points_check CHECK ((points >= 0)),
    CONSTRAINT fdileague_scoring_quarter_check CHECK ((quarter >= 0)),
    CONSTRAINT fdileague_scoring_yardage_check CHECK ((yardage >= 0))
);


ALTER TABLE public.fdileague_scoring OWNER TO "www-data";

--
-- Name: fdileague_scoring_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE fdileague_scoring_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.fdileague_scoring_id_seq OWNER TO "www-data";

--
-- Name: fdileague_scoring_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE fdileague_scoring_id_seq OWNED BY fdileague_scoring.id;


--
-- Name: fdileague_team; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE fdileague_team (
    id integer NOT NULL,
    year date NOT NULL,
    city character varying(50) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.fdileague_team OWNER TO "www-data";

--
-- Name: fdileague_team_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE fdileague_team_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.fdileague_team_id_seq OWNER TO "www-data";

--
-- Name: fdileague_team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE fdileague_team_id_seq OWNED BY fdileague_team.id;


--
-- Name: fdileague_teamstats; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE fdileague_teamstats (
    id integer NOT NULL,
    first_downs smallint NOT NULL,
    rushes smallint NOT NULL,
    rush_yards smallint NOT NULL,
    rush_tds smallint NOT NULL,
    pass_comp smallint NOT NULL,
    pass_att smallint NOT NULL,
    pass_yards smallint NOT NULL,
    pass_tds smallint NOT NULL,
    pass_int smallint NOT NULL,
    sacks smallint NOT NULL,
    sack_yards smallint NOT NULL,
    net_pass_yards smallint NOT NULL,
    total_yards smallint NOT NULL,
    fumbles smallint NOT NULL,
    fumbles_lots smallint NOT NULL,
    turnovers smallint NOT NULL,
    penlaties smallint NOT NULL,
    penalties_yards smallint NOT NULL,
    CONSTRAINT fdileague_teamstats_first_downs_check CHECK ((first_downs >= 0)),
    CONSTRAINT fdileague_teamstats_fumbles_check CHECK ((fumbles >= 0)),
    CONSTRAINT fdileague_teamstats_fumbles_lots_check CHECK ((fumbles_lots >= 0)),
    CONSTRAINT fdileague_teamstats_net_pass_yards_check CHECK ((net_pass_yards >= 0)),
    CONSTRAINT fdileague_teamstats_pass_att_check CHECK ((pass_att >= 0)),
    CONSTRAINT fdileague_teamstats_pass_comp_check CHECK ((pass_comp >= 0)),
    CONSTRAINT fdileague_teamstats_pass_int_check CHECK ((pass_int >= 0)),
    CONSTRAINT fdileague_teamstats_pass_tds_check CHECK ((pass_tds >= 0)),
    CONSTRAINT fdileague_teamstats_pass_yards_check CHECK ((pass_yards >= 0)),
    CONSTRAINT fdileague_teamstats_penalties_yards_check CHECK ((penalties_yards >= 0)),
    CONSTRAINT fdileague_teamstats_penlaties_check CHECK ((penlaties >= 0)),
    CONSTRAINT fdileague_teamstats_rush_tds_check CHECK ((rush_tds >= 0)),
    CONSTRAINT fdileague_teamstats_rush_yards_check CHECK ((rush_yards >= 0)),
    CONSTRAINT fdileague_teamstats_rushes_check CHECK ((rushes >= 0)),
    CONSTRAINT fdileague_teamstats_sack_yards_check CHECK ((sack_yards >= 0)),
    CONSTRAINT fdileague_teamstats_sacks_check CHECK ((sacks >= 0)),
    CONSTRAINT fdileague_teamstats_total_yards_check CHECK ((total_yards >= 0)),
    CONSTRAINT fdileague_teamstats_turnovers_check CHECK ((turnovers >= 0))
);


ALTER TABLE public.fdileague_teamstats OWNER TO "www-data";

--
-- Name: fdileague_teamstats_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE fdileague_teamstats_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.fdileague_teamstats_id_seq OWNER TO "www-data";

--
-- Name: fdileague_teamstats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE fdileague_teamstats_id_seq OWNED BY fdileague_teamstats.id;


--
-- Name: fdileague_yearscore; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE fdileague_yearscore (
    id integer NOT NULL,
    player_id integer NOT NULL,
    year smallint NOT NULL,
    score smallint NOT NULL,
    CONSTRAINT fdileague_yearscore_score_check CHECK ((score >= 0)),
    CONSTRAINT fdileague_yearscore_year_check CHECK ((year >= 0))
);


ALTER TABLE public.fdileague_yearscore OWNER TO "www-data";

--
-- Name: fdileague_yearscore_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE fdileague_yearscore_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.fdileague_yearscore_id_seq OWNER TO "www-data";

--
-- Name: fdileague_yearscore_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE fdileague_yearscore_id_seq OWNED BY fdileague_yearscore.id;


--
-- Name: flavor_usage_application; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE flavor_usage_application (
    id integer NOT NULL,
    flavor_id integer NOT NULL,
    application_type_id integer NOT NULL,
    usage_level numeric(5,3) NOT NULL,
    memo text NOT NULL,
    productinfo_id integer
);


ALTER TABLE public.flavor_usage_application OWNER TO "www-data";

--
-- Name: flavor_usage_application_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE flavor_usage_application_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.flavor_usage_application_id_seq OWNER TO "www-data";

--
-- Name: flavor_usage_application_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE flavor_usage_application_id_seq OWNED BY flavor_usage_application.id;


--
-- Name: flavor_usage_applicationtype; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE flavor_usage_applicationtype (
    id integer NOT NULL,
    name character varying(40) NOT NULL
);


ALTER TABLE public.flavor_usage_applicationtype OWNER TO "www-data";

--
-- Name: flavor_usage_applicationtype_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE flavor_usage_applicationtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.flavor_usage_applicationtype_id_seq OWNER TO "www-data";

--
-- Name: flavor_usage_applicationtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE flavor_usage_applicationtype_id_seq OWNED BY flavor_usage_applicationtype.id;


--
-- Name: haccp_koshergroup; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE haccp_koshergroup (
    id integer NOT NULL,
    name character varying(2) NOT NULL
);


ALTER TABLE public.haccp_koshergroup OWNER TO "www-data";

--
-- Name: haccp_koshergroup_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE haccp_koshergroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.haccp_koshergroup_id_seq OWNER TO "www-data";

--
-- Name: haccp_koshergroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE haccp_koshergroup_id_seq OWNED BY haccp_koshergroup.id;


--
-- Name: haccp_qualitytest; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE haccp_qualitytest (
    id integer NOT NULL,
    test_date date NOT NULL,
    zone smallint NOT NULL,
    CONSTRAINT haccp_qualitytest_zone_check CHECK ((zone >= 0))
);


ALTER TABLE public.haccp_qualitytest OWNER TO "www-data";

--
-- Name: haccp_qualitytest_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE haccp_qualitytest_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.haccp_qualitytest_id_seq OWNER TO "www-data";

--
-- Name: haccp_qualitytest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE haccp_qualitytest_id_seq OWNED BY haccp_qualitytest.id;


--
-- Name: haccp_receivinglog; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE haccp_receivinglog (
    id integer NOT NULL,
    entry_date timestamp with time zone NOT NULL,
    receiving_number integer NOT NULL,
    pin_number integer NOT NULL,
    supplier_id_id integer NOT NULL,
    description_of_goods character varying(50) NOT NULL,
    package_quantity integer NOT NULL,
    supplier_lot_number character varying(25) NOT NULL,
    po_number integer NOT NULL,
    truck character varying(25) NOT NULL,
    kosher_group_id integer,
    notes text NOT NULL,
    CONSTRAINT haccp_receivinglog_package_quantity_check CHECK ((package_quantity >= 0)),
    CONSTRAINT haccp_receivinglog_pin_number_check CHECK ((pin_number >= 0)),
    CONSTRAINT haccp_receivinglog_po_number_check CHECK ((po_number >= 0)),
    CONSTRAINT haccp_receivinglog_receiving_number_check CHECK ((receiving_number >= 0))
);


ALTER TABLE public.haccp_receivinglog OWNER TO "www-data";

--
-- Name: haccp_receivinglog_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE haccp_receivinglog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.haccp_receivinglog_id_seq OWNER TO "www-data";

--
-- Name: haccp_receivinglog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE haccp_receivinglog_id_seq OWNED BY haccp_receivinglog.id;


--
-- Name: haccp_thermometertest; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE haccp_thermometertest (
    qualitytest_ptr_id integer NOT NULL,
    test_result smallint NOT NULL,
    CONSTRAINT haccp_thermometertest_test_result_check CHECK ((test_result >= 0))
);


ALTER TABLE public.haccp_thermometertest OWNER TO "www-data";

--
-- Name: haccp_tobaccobeetletest; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE haccp_tobaccobeetletest (
    qualitytest_ptr_id integer NOT NULL,
    test_result smallint NOT NULL,
    CONSTRAINT haccp_tobaccobeetletest_test_result_check CHECK ((test_result >= 0))
);


ALTER TABLE public.haccp_tobaccobeetletest OWNER TO "www-data";

--
-- Name: haccp_watertest; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE haccp_watertest (
    id integer NOT NULL,
    test_date date NOT NULL,
    zone smallint NOT NULL,
    test_result numeric(2,1) NOT NULL,
    CONSTRAINT haccp_watertest_zone_check CHECK ((zone >= 0))
);


ALTER TABLE public.haccp_watertest OWNER TO "www-data";

--
-- Name: haccp_watertest_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE haccp_watertest_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.haccp_watertest_id_seq OWNER TO "www-data";

--
-- Name: haccp_watertest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE haccp_watertest_id_seq OWNED BY haccp_watertest.id;


--
-- Name: lot_lot; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE lot_lot (
    id integer NOT NULL,
    date date NOT NULL,
    number integer NOT NULL,
    sub_lot smallint,
    status character varying(25) NOT NULL,
    amount numeric(6,1),
    flavor_id integer NOT NULL,
    CONSTRAINT lot_lot_number_check CHECK ((number >= 0)),
    CONSTRAINT lot_lot_sub_lot_check CHECK ((sub_lot >= 0))
);


ALTER TABLE public.lot_lot OWNER TO "www-data";

--
-- Name: lot_lot_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE lot_lot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.lot_lot_id_seq OWNER TO "www-data";

--
-- Name: lot_lot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE lot_lot_id_seq OWNED BY lot_lot.id;


--
-- Name: newqc_experimentalretain; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_experimentalretain (
    id integer NOT NULL,
    retain smallint NOT NULL,
    date date NOT NULL,
    experimental_number smallint NOT NULL,
    CONSTRAINT newqc_experimentalretain_experimental_number_check CHECK ((experimental_number >= 0)),
    CONSTRAINT newqc_experimentalretain_retain_check CHECK ((retain >= 0))
);


ALTER TABLE public.newqc_experimentalretain OWNER TO "www-data";

--
-- Name: newqc_experimentalretain_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_experimentalretain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_experimentalretain_id_seq OWNER TO "www-data";

--
-- Name: newqc_experimentalretain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_experimentalretain_id_seq OWNED BY newqc_experimentalretain.id;


--
-- Name: newqc_importretain; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_importretain (
    id integer NOT NULL,
    number smallint,
    date date,
    name character varying(100),
    prefix character varying(10),
    flavor_number integer,
    lot_number integer,
    sub_lot_number smallint,
    status character varying(100),
    amount numeric(6,1),
    notes character varying(200),
    path character varying(200),
    CONSTRAINT newqc_importretain_flavor_number_check CHECK ((flavor_number >= 0)),
    CONSTRAINT newqc_importretain_lot_number_check CHECK ((lot_number >= 0)),
    CONSTRAINT newqc_importretain_number_check CHECK ((number >= 0)),
    CONSTRAINT newqc_importretain_sub_lot_number_check CHECK ((sub_lot_number >= 0))
);


ALTER TABLE public.newqc_importretain OWNER TO "www-data";

--
-- Name: newqc_importretain_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_importretain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_importretain_id_seq OWNER TO "www-data";

--
-- Name: newqc_importretain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_importretain_id_seq OWNED BY newqc_importretain.id;


--
-- Name: newqc_lot; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_lot (
    id integer NOT NULL,
    date date NOT NULL,
    number integer NOT NULL,
    sub_lot smallint,
    status character varying(25) NOT NULL,
    amount numeric(6,1),
    flavor_id integer NOT NULL,
    CONSTRAINT newqc_lot_number_check CHECK ((number >= 0)),
    CONSTRAINT newqc_lot_sub_lot_check CHECK ((sub_lot >= 0))
);


ALTER TABLE public.newqc_lot OWNER TO "www-data";

--
-- Name: newqc_lot_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_lot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_lot_id_seq OWNER TO "www-data";

--
-- Name: newqc_lot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_lot_id_seq OWNED BY newqc_lot.id;


--
-- Name: newqc_productinfo; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_productinfo (
    id integer NOT NULL,
    flavor_id integer NOT NULL,
    appearance character varying(100) NOT NULL,
    organoleptic_properties character varying(100) NOT NULL,
    testing_procedure text NOT NULL,
    flash_point double precision,
    specific_gravity numeric(3,2),
    notes text NOT NULL,
    retain_on_file boolean NOT NULL,
    original_card character varying(100) NOT NULL
);


ALTER TABLE public.newqc_productinfo OWNER TO "www-data";

--
-- Name: newqc_productinfo_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_productinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_productinfo_id_seq OWNER TO "www-data";

--
-- Name: newqc_productinfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_productinfo_id_seq OWNED BY newqc_productinfo.id;


--
-- Name: newqc_retain; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_retain (
    id integer NOT NULL,
    retain smallint NOT NULL,
    date date NOT NULL,
    lot_id integer NOT NULL,
    status character varying(25) NOT NULL,
    notes character varying(500) NOT NULL,
    ir_id integer,
    CONSTRAINT newqc_retain_retain_check CHECK ((retain >= 0))
);


ALTER TABLE public.newqc_retain OWNER TO "www-data";

--
-- Name: newqc_retain_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_retain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_retain_id_seq OWNER TO "www-data";

--
-- Name: newqc_retain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_retain_id_seq OWNED BY newqc_retain.id;


--
-- Name: newqc_rmimportretain; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_rmimportretain (
    id integer NOT NULL,
    date date,
    pin smallint,
    supplier character varying(40),
    name character varying(100),
    lot character varying(40),
    r_number smallint,
    status character varying(20),
    notes character varying(200),
    CONSTRAINT newqc_rmimportretain_pin_check CHECK ((pin >= 0)),
    CONSTRAINT newqc_rmimportretain_r_number_check CHECK ((r_number >= 0))
);


ALTER TABLE public.newqc_rmimportretain OWNER TO "www-data";

--
-- Name: newqc_rmimportretain_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_rmimportretain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_rmimportretain_id_seq OWNER TO "www-data";

--
-- Name: newqc_rmimportretain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_rmimportretain_id_seq OWNED BY newqc_rmimportretain.id;


--
-- Name: newqc_rminfo; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_rminfo (
    id integer NOT NULL,
    pin smallint NOT NULL,
    testing_procedure text NOT NULL,
    notes text NOT NULL,
    retain_on_file boolean NOT NULL,
    original_card character varying(100) NOT NULL,
    CONSTRAINT newqc_rminfo_pin_check CHECK ((pin >= 0))
);


ALTER TABLE public.newqc_rminfo OWNER TO "www-data";

--
-- Name: newqc_rminfo_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_rminfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_rminfo_id_seq OWNER TO "www-data";

--
-- Name: newqc_rminfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_rminfo_id_seq OWNED BY newqc_rminfo.id;


--
-- Name: newqc_rmretain; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_rmretain (
    id integer NOT NULL,
    date date NOT NULL,
    pin smallint NOT NULL,
    supplier character varying(40) NOT NULL,
    lot character varying(40) NOT NULL,
    r_number smallint NOT NULL,
    status character varying(25) NOT NULL,
    notes character varying(200) NOT NULL,
    ir_id integer,
    CONSTRAINT newqc_rmretain_pin_check CHECK ((pin >= 0)),
    CONSTRAINT newqc_rmretain_r_number_check CHECK ((r_number >= 0))
);


ALTER TABLE public.newqc_rmretain OWNER TO "www-data";

--
-- Name: newqc_rmretain_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_rmretain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_rmretain_id_seq OWNER TO "www-data";

--
-- Name: newqc_rmretain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_rmretain_id_seq OWNED BY newqc_rmretain.id;


--
-- Name: newqc_testcard; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE newqc_testcard (
    id integer NOT NULL,
    retain_id integer NOT NULL,
    image_hash character varying(64) NOT NULL,
    large character varying(100) NOT NULL,
    notes text NOT NULL,
    status character varying(25) NOT NULL
);


ALTER TABLE public.newqc_testcard OWNER TO "www-data";

--
-- Name: newqc_testcard_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE newqc_testcard_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.newqc_testcard_id_seq OWNER TO "www-data";

--
-- Name: newqc_testcard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE newqc_testcard_id_seq OWNED BY newqc_testcard.id;


--
-- Name: performance_appraisal_department; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE performance_appraisal_department (
    id integer NOT NULL,
    name character varying(40) NOT NULL
);


ALTER TABLE public.performance_appraisal_department OWNER TO "www-data";

--
-- Name: performance_appraisal_department_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE performance_appraisal_department_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.performance_appraisal_department_id_seq OWNER TO "www-data";

--
-- Name: performance_appraisal_department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE performance_appraisal_department_id_seq OWNED BY performance_appraisal_department.id;


--
-- Name: performance_appraisal_performanceappraisal; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE performance_appraisal_performanceappraisal (
    id integer NOT NULL,
    employee_name character varying(40) NOT NULL,
    department_id integer NOT NULL,
    title character varying(40) NOT NULL,
    reason_for_review character varying(40) NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    quality_rating smallint NOT NULL,
    quality_comments text NOT NULL,
    productivity_rating smallint NOT NULL,
    productivity_comments text NOT NULL,
    job_knowledge_rating smallint NOT NULL,
    job_knowledge_comments text NOT NULL,
    reliability_rating smallint NOT NULL,
    reliability_comments text NOT NULL,
    attendance_rating smallint NOT NULL,
    attendance_comments text NOT NULL,
    creativity_rating smallint NOT NULL,
    creativity_comments text NOT NULL,
    initiative_rating smallint NOT NULL,
    initiative_comments text NOT NULL,
    adherence_to_policy_rating smallint NOT NULL,
    adherence_to_policy_comments text NOT NULL,
    interpersonal_relationships_rating smallint NOT NULL,
    interpersonal_relationships_comments text NOT NULL,
    judgement_rating smallint NOT NULL,
    judgement_comments text NOT NULL,
    additional_comments text NOT NULL,
    CONSTRAINT performance_appraisal_perfor_interpersonal_relationships__check CHECK ((interpersonal_relationships_rating >= 0)),
    CONSTRAINT performance_appraisal_performa_adherence_to_policy_rating_check CHECK ((adherence_to_policy_rating >= 0)),
    CONSTRAINT performance_appraisal_performanceapp_job_knowledge_rating_check CHECK ((job_knowledge_rating >= 0)),
    CONSTRAINT performance_appraisal_performanceappr_productivity_rating_check CHECK ((productivity_rating >= 0)),
    CONSTRAINT performance_appraisal_performanceappra_reliability_rating_check CHECK ((reliability_rating >= 0)),
    CONSTRAINT performance_appraisal_performanceapprai_attendance_rating_check CHECK ((attendance_rating >= 0)),
    CONSTRAINT performance_appraisal_performanceapprai_creativity_rating_check CHECK ((creativity_rating >= 0)),
    CONSTRAINT performance_appraisal_performanceapprai_initiative_rating_check CHECK ((initiative_rating >= 0)),
    CONSTRAINT performance_appraisal_performanceapprais_judgement_rating_check CHECK ((judgement_rating >= 0)),
    CONSTRAINT performance_appraisal_performanceappraisal_quality_rating_check CHECK ((quality_rating >= 0))
);


ALTER TABLE public.performance_appraisal_performanceappraisal OWNER TO "www-data";

--
-- Name: performance_appraisal_performanceappraisal_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE performance_appraisal_performanceappraisal_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.performance_appraisal_performanceappraisal_id_seq OWNER TO "www-data";

--
-- Name: performance_appraisal_performanceappraisal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE performance_appraisal_performanceappraisal_id_seq OWNED BY performance_appraisal_performanceappraisal.id;


--
-- Name: personnel_userprofile; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE personnel_userprofile (
    id integer NOT NULL,
    user_id integer NOT NULL,
    initials character varying(3) NOT NULL,
    sort_user_columns character varying(256),
    user_columns character varying(256)
);


ALTER TABLE public.personnel_userprofile OWNER TO "www-data";

--
-- Name: personnel_userprofile_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE personnel_userprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.personnel_userprofile_id_seq OWNER TO "www-data";

--
-- Name: personnel_userprofile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE personnel_userprofile_id_seq OWNED BY personnel_userprofile.id;


--
-- Name: reversion_revision; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE reversion_revision (
    id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    user_id integer,
    comment text NOT NULL
);


ALTER TABLE public.reversion_revision OWNER TO "www-data";

--
-- Name: reversion_revision_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE reversion_revision_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.reversion_revision_id_seq OWNER TO "www-data";

--
-- Name: reversion_revision_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE reversion_revision_id_seq OWNED BY reversion_revision.id;


--
-- Name: reversion_version; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE reversion_version (
    id integer NOT NULL,
    revision_id integer NOT NULL,
    object_id text NOT NULL,
    content_type_id integer NOT NULL,
    format character varying(255) NOT NULL,
    serialized_data text NOT NULL,
    object_repr text NOT NULL
);


ALTER TABLE public.reversion_version OWNER TO "www-data";

--
-- Name: reversion_version_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE reversion_version_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.reversion_version_id_seq OWNER TO "www-data";

--
-- Name: reversion_version_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE reversion_version_id_seq OWNED BY reversion_version.id;


--
-- Name: salesorders_lineitem; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE salesorders_lineitem (
    id integer NOT NULL,
    salesordernumber_id integer NOT NULL,
    flavor_id integer NOT NULL,
    quantity numeric(9,2) NOT NULL,
    unit_price numeric(9,3) NOT NULL,
    quantity_price numeric(9,3) NOT NULL,
    ship_date date NOT NULL,
    due_date date NOT NULL
);


ALTER TABLE public.salesorders_lineitem OWNER TO "www-data";

--
-- Name: salesorders_lineitem_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE salesorders_lineitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.salesorders_lineitem_id_seq OWNER TO "www-data";

--
-- Name: salesorders_lineitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE salesorders_lineitem_id_seq OWNED BY salesorders_lineitem.id;


--
-- Name: salesorders_salesordernumber; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE salesorders_salesordernumber (
    id integer NOT NULL,
    number integer NOT NULL,
    create_date date NOT NULL,
    customer_id integer,
    open boolean NOT NULL,
    CONSTRAINT salesorders_salesordernumber_number_check CHECK ((number >= 0))
);


ALTER TABLE public.salesorders_salesordernumber OWNER TO "www-data";

--
-- Name: salesorders_salesordernumber_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE salesorders_salesordernumber_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.salesorders_salesordernumber_id_seq OWNER TO "www-data";

--
-- Name: salesorders_salesordernumber_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE salesorders_salesordernumber_id_seq OWNED BY salesorders_salesordernumber.id;


--
-- Name: siteconfig_siteconfiguration; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE siteconfig_siteconfiguration (
    id integer NOT NULL,
    site_id integer NOT NULL,
    version character varying(20) NOT NULL,
    settings text NOT NULL
);


ALTER TABLE public.siteconfig_siteconfiguration OWNER TO "www-data";

--
-- Name: siteconfig_siteconfiguration_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE siteconfig_siteconfiguration_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.siteconfig_siteconfiguration_id_seq OWNER TO "www-data";

--
-- Name: siteconfig_siteconfiguration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE siteconfig_siteconfiguration_id_seq OWNED BY siteconfig_siteconfiguration.id;


--
-- Name: solutionfixer_solution; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE solutionfixer_solution (
    id integer NOT NULL,
    ingredient_id integer NOT NULL,
    my_base_id integer,
    my_solvent_id integer,
    percentage numeric(4,2),
    status_id integer
);


ALTER TABLE public.solutionfixer_solution OWNER TO "www-data";

--
-- Name: solutionfixer_solution_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE solutionfixer_solution_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.solutionfixer_solution_id_seq OWNER TO "www-data";

--
-- Name: solutionfixer_solution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE solutionfixer_solution_id_seq OWNED BY solutionfixer_solution.id;


--
-- Name: solutionfixer_solutionmatchcache; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE solutionfixer_solutionmatchcache (
    my_pk integer NOT NULL,
    id integer NOT NULL,
    value integer NOT NULL,
    label character varying(150) NOT NULL,
    solution_id integer NOT NULL
);


ALTER TABLE public.solutionfixer_solutionmatchcache OWNER TO "www-data";

--
-- Name: solutionfixer_solutionmatchcache_my_pk_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE solutionfixer_solutionmatchcache_my_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.solutionfixer_solutionmatchcache_my_pk_seq OWNER TO "www-data";

--
-- Name: solutionfixer_solutionmatchcache_my_pk_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE solutionfixer_solutionmatchcache_my_pk_seq OWNED BY solutionfixer_solutionmatchcache.my_pk;


--
-- Name: solutionfixer_solutionstatus; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE solutionfixer_solutionstatus (
    id integer NOT NULL,
    status_name character varying(20) NOT NULL,
    status_order smallint NOT NULL,
    CONSTRAINT solutionfixer_solutionstatus_status_order_check CHECK ((status_order >= 0))
);


ALTER TABLE public.solutionfixer_solutionstatus OWNER TO "www-data";

--
-- Name: solutionfixer_solutionstatus_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE solutionfixer_solutionstatus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.solutionfixer_solutionstatus_id_seq OWNER TO "www-data";

--
-- Name: solutionfixer_solutionstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE solutionfixer_solutionstatus_id_seq OWNED BY solutionfixer_solutionstatus.id;


--
-- Name: south_migrationhistory; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE south_migrationhistory (
    id integer NOT NULL,
    app_name character varying(255) NOT NULL,
    migration character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.south_migrationhistory OWNER TO "www-data";

--
-- Name: south_migrationhistory_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE south_migrationhistory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.south_migrationhistory_id_seq OWNER TO "www-data";

--
-- Name: south_migrationhistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE south_migrationhistory_id_seq OWNED BY south_migrationhistory.id;


--
-- Name: supplier; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE supplier (
    id integer NOT NULL,
    supplier_name character varying(50) NOT NULL
);


ALTER TABLE public.supplier OWNER TO "www-data";

--
-- Name: thumbnail_kvstore; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE thumbnail_kvstore (
    key character varying(200) NOT NULL,
    value text NOT NULL
);


ALTER TABLE public.thumbnail_kvstore OWNER TO "www-data";

--
-- Name: unified_adapter_application; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE unified_adapter_application (
    id integer NOT NULL,
    product_info_id integer NOT NULL,
    application_type_id integer NOT NULL,
    usage_level numeric(5,3) NOT NULL,
    memo text NOT NULL
);


ALTER TABLE public.unified_adapter_application OWNER TO "www-data";

--
-- Name: unified_adapter_application_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE unified_adapter_application_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.unified_adapter_application_id_seq OWNER TO "www-data";

--
-- Name: unified_adapter_application_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE unified_adapter_application_id_seq OWNED BY unified_adapter_application.id;


--
-- Name: unified_adapter_applicationtype; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE unified_adapter_applicationtype (
    id integer NOT NULL,
    name character varying(40) NOT NULL
);


ALTER TABLE public.unified_adapter_applicationtype OWNER TO "www-data";

--
-- Name: unified_adapter_applicationtype_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE unified_adapter_applicationtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.unified_adapter_applicationtype_id_seq OWNER TO "www-data";

--
-- Name: unified_adapter_applicationtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE unified_adapter_applicationtype_id_seq OWNED BY unified_adapter_applicationtype.id;


--
-- Name: unified_adapter_productinfo; Type: TABLE; Schema: public; Owner: www-data; Tablespace: 
--

CREATE TABLE unified_adapter_productinfo (
    id integer NOT NULL,
    allergens character varying(50) NOT NULL,
    approved_promote character varying(20) NOT NULL,
    concentrate boolean NOT NULL,
    customer character varying(60) NOT NULL,
    description character varying(60) NOT NULL,
    dry boolean NOT NULL,
    duplication boolean NOT NULL,
    emulsion boolean NOT NULL,
    experimental_number integer,
    export_only character varying(200) NOT NULL,
    flash numeric(5,2) NOT NULL,
    gmo_free boolean NOT NULL,
    heat_stable boolean NOT NULL,
    initials character varying(20) NOT NULL,
    keyword_1 character varying(40) NOT NULL,
    keyword_2 character varying(41) NOT NULL,
    kosher character varying(200) NOT NULL,
    liquid boolean NOT NULL,
    location_code character varying(20) NOT NULL,
    memo text NOT NULL,
    microsensitive character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    nat_art character varying(20) NOT NULL,
    no_diacetyl boolean NOT NULL,
    no_msg boolean NOT NULL,
    no_pg boolean NOT NULL,
    nutri_on_file boolean NOT NULL,
    organic boolean NOT NULL,
    organoleptic_properties text NOT NULL,
    oil_soluble boolean NOT NULL,
    percentage_yield smallint NOT NULL,
    production_number integer,
    prop_65 boolean NOT NULL,
    same_as character varying(200) NOT NULL,
    sold boolean NOT NULL,
    solubility character varying(200) NOT NULL,
    specific_gravity numeric(4,3) NOT NULL,
    testing_procedure text NOT NULL,
    transfat boolean NOT NULL,
    unitprice numeric(7,3) NOT NULL,
    CONSTRAINT unified_adapter_productinfo_experimental_number_check CHECK ((experimental_number >= 0)),
    CONSTRAINT unified_adapter_productinfo_percentage_yield_check CHECK ((percentage_yield >= 0)),
    CONSTRAINT unified_adapter_productinfo_production_number_check CHECK ((production_number >= 0))
);


ALTER TABLE public.unified_adapter_productinfo OWNER TO "www-data";

--
-- Name: unified_adapter_productinfo_id_seq; Type: SEQUENCE; Schema: public; Owner: www-data
--

CREATE SEQUENCE unified_adapter_productinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.unified_adapter_productinfo_id_seq OWNER TO "www-data";

--
-- Name: unified_adapter_productinfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: www-data
--

ALTER SEQUENCE unified_adapter_productinfo_id_seq OWNED BY unified_adapter_productinfo.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE "Customers" ALTER COLUMN id SET DEFAULT nextval('"Customers_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE "Experimental Formulas" ALTER COLUMN id SET DEFAULT nextval('"Experimental Formulas_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE "ExperimentalLog" ALTER COLUMN id SET DEFAULT nextval('"ExperimentalLog_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE "Flavors - Formulae" ALTER COLUMN id SET DEFAULT nextval('"Flavors - Formulae_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE access_epsiformula ALTER COLUMN id SET DEFAULT nextval('access_epsiformula_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE access_flavoriterorder ALTER COLUMN id SET DEFAULT nextval('access_flavoriterorder_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE access_formulatree ALTER COLUMN id SET DEFAULT nextval('access_formulatree_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE access_leafweight ALTER COLUMN id SET DEFAULT nextval('access_leafweight_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE access_purchaseorder ALTER COLUMN id SET DEFAULT nextval('access_purchaseorder_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE access_purchaseorderlineitem ALTER COLUMN id SET DEFAULT nextval('access_purchaseorderlineitem_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE auth_message ALTER COLUMN id SET DEFAULT nextval('auth_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE django_comment_flags ALTER COLUMN id SET DEFAULT nextval('django_comment_flags_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE django_comments ALTER COLUMN id SET DEFAULT nextval('django_comments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE djcelery_crontabschedule ALTER COLUMN id SET DEFAULT nextval('djcelery_crontabschedule_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE djcelery_intervalschedule ALTER COLUMN id SET DEFAULT nextval('djcelery_intervalschedule_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE djcelery_periodictask ALTER COLUMN id SET DEFAULT nextval('djcelery_periodictask_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE djcelery_taskstate ALTER COLUMN id SET DEFAULT nextval('djcelery_taskstate_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE djcelery_workerstate ALTER COLUMN id SET DEFAULT nextval('djcelery_workerstate_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE docvault_doc ALTER COLUMN id SET DEFAULT nextval('docvault_doc_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE docvault_page ALTER COLUMN id SET DEFAULT nextval('docvault_page_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE fdileague_game ALTER COLUMN id SET DEFAULT nextval('fdileague_game_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE fdileague_player ALTER COLUMN id SET DEFAULT nextval('fdileague_player_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE fdileague_scoring ALTER COLUMN id SET DEFAULT nextval('fdileague_scoring_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE fdileague_team ALTER COLUMN id SET DEFAULT nextval('fdileague_team_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE fdileague_teamstats ALTER COLUMN id SET DEFAULT nextval('fdileague_teamstats_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE fdileague_yearscore ALTER COLUMN id SET DEFAULT nextval('fdileague_yearscore_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE flavor_usage_application ALTER COLUMN id SET DEFAULT nextval('flavor_usage_application_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE flavor_usage_applicationtype ALTER COLUMN id SET DEFAULT nextval('flavor_usage_applicationtype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE haccp_koshergroup ALTER COLUMN id SET DEFAULT nextval('haccp_koshergroup_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE haccp_qualitytest ALTER COLUMN id SET DEFAULT nextval('haccp_qualitytest_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE haccp_receivinglog ALTER COLUMN id SET DEFAULT nextval('haccp_receivinglog_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE haccp_watertest ALTER COLUMN id SET DEFAULT nextval('haccp_watertest_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE lot_lot ALTER COLUMN id SET DEFAULT nextval('lot_lot_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_experimentalretain ALTER COLUMN id SET DEFAULT nextval('newqc_experimentalretain_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_importretain ALTER COLUMN id SET DEFAULT nextval('newqc_importretain_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_lot ALTER COLUMN id SET DEFAULT nextval('newqc_lot_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_productinfo ALTER COLUMN id SET DEFAULT nextval('newqc_productinfo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_retain ALTER COLUMN id SET DEFAULT nextval('newqc_retain_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_rmimportretain ALTER COLUMN id SET DEFAULT nextval('newqc_rmimportretain_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_rminfo ALTER COLUMN id SET DEFAULT nextval('newqc_rminfo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_rmretain ALTER COLUMN id SET DEFAULT nextval('newqc_rmretain_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE newqc_testcard ALTER COLUMN id SET DEFAULT nextval('newqc_testcard_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE performance_appraisal_department ALTER COLUMN id SET DEFAULT nextval('performance_appraisal_department_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE performance_appraisal_performanceappraisal ALTER COLUMN id SET DEFAULT nextval('performance_appraisal_performanceappraisal_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE personnel_userprofile ALTER COLUMN id SET DEFAULT nextval('personnel_userprofile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE reversion_revision ALTER COLUMN id SET DEFAULT nextval('reversion_revision_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE reversion_version ALTER COLUMN id SET DEFAULT nextval('reversion_version_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE salesorders_lineitem ALTER COLUMN id SET DEFAULT nextval('salesorders_lineitem_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE salesorders_salesordernumber ALTER COLUMN id SET DEFAULT nextval('salesorders_salesordernumber_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE siteconfig_siteconfiguration ALTER COLUMN id SET DEFAULT nextval('siteconfig_siteconfiguration_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE solutionfixer_solution ALTER COLUMN id SET DEFAULT nextval('solutionfixer_solution_id_seq'::regclass);


--
-- Name: my_pk; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE solutionfixer_solutionmatchcache ALTER COLUMN my_pk SET DEFAULT nextval('solutionfixer_solutionmatchcache_my_pk_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE solutionfixer_solutionstatus ALTER COLUMN id SET DEFAULT nextval('solutionfixer_solutionstatus_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE south_migrationhistory ALTER COLUMN id SET DEFAULT nextval('south_migrationhistory_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE unified_adapter_application ALTER COLUMN id SET DEFAULT nextval('unified_adapter_application_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE unified_adapter_applicationtype ALTER COLUMN id SET DEFAULT nextval('unified_adapter_applicationtype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: www-data
--

ALTER TABLE unified_adapter_productinfo ALTER COLUMN id SET DEFAULT nextval('unified_adapter_productinfo_id_seq'::regclass);


--
-- Name: Customers_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Customers"
    ADD CONSTRAINT "Customers_pkey" PRIMARY KEY (id);


--
-- Name: Experimental Formulas_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Experimental Formulas"
    ADD CONSTRAINT "Experimental Formulas_pkey" PRIMARY KEY (id);


--
-- Name: Experimental Products_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Experimental Products"
    ADD CONSTRAINT "Experimental Products_pkey" PRIMARY KEY ("ProductID");


--
-- Name: ExperimentalLog_ExperimentalNum_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "ExperimentalLog"
    ADD CONSTRAINT "ExperimentalLog_ExperimentalNum_key" UNIQUE ("ExperimentalNum");


--
-- Name: ExperimentalLog_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "ExperimentalLog"
    ADD CONSTRAINT "ExperimentalLog_pkey" PRIMARY KEY (id);


--
-- Name: Flavors - Formulae_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Flavors - Formulae"
    ADD CONSTRAINT "Flavors - Formulae_pkey" PRIMARY KEY (id);


--
-- Name: Incoming_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Incoming"
    ADD CONSTRAINT "Incoming_pkey" PRIMARY KEY ("IncomingID");


--
-- Name: Products - Special Information_flavor_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Products - Special Information"
    ADD CONSTRAINT "Products - Special Information_flavor_id_key" UNIQUE (flavor_id);


--
-- Name: Products - Special Information_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Products - Special Information"
    ADD CONSTRAINT "Products - Special Information_pkey" PRIMARY KEY ("FlavorNumber");


--
-- Name: Products_FlavorNumber_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Products"
    ADD CONSTRAINT "Products_FlavorNumber_key" UNIQUE ("FlavorNumber");


--
-- Name: Products_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Products"
    ADD CONSTRAINT "Products_pkey" PRIMARY KEY ("ProductID");


--
-- Name: Purchases_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Purchases"
    ADD CONSTRAINT "Purchases_pkey" PRIMARY KEY ("POEntry");


--
-- Name: Raw Materials_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Raw Materials"
    ADD CONSTRAINT "Raw Materials_pkey" PRIMARY KEY ("RawMaterialCode");


--
-- Name: ShipTo_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "ShipTo"
    ADD CONSTRAINT "ShipTo_pkey" PRIMARY KEY ("ShipToID");


--
-- Name: Shippers_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Shippers"
    ADD CONSTRAINT "Shippers_pkey" PRIMARY KEY ("ShipperID");


--
-- Name: Suppliers_SupplierCode_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Suppliers"
    ADD CONSTRAINT "Suppliers_SupplierCode_key" UNIQUE ("SupplierCode");


--
-- Name: Suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY "Suppliers"
    ADD CONSTRAINT "Suppliers_pkey" PRIMARY KEY ("ID");


--
-- Name: access_epsiformula_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY access_epsiformula
    ADD CONSTRAINT access_epsiformula_pkey PRIMARY KEY (id);


--
-- Name: access_flavoriterorder_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY access_flavoriterorder
    ADD CONSTRAINT access_flavoriterorder_pkey PRIMARY KEY (id);


--
-- Name: access_formulatree_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY access_formulatree
    ADD CONSTRAINT access_formulatree_pkey PRIMARY KEY (id);


--
-- Name: access_leafweight_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY access_leafweight
    ADD CONSTRAINT access_leafweight_pkey PRIMARY KEY (id);


--
-- Name: access_purchaseorder_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY access_purchaseorder
    ADD CONSTRAINT access_purchaseorder_pkey PRIMARY KEY (id);


--
-- Name: access_purchaseorderlineitem_legacy_purchase_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY access_purchaseorderlineitem
    ADD CONSTRAINT access_purchaseorderlineitem_legacy_purchase_id_key UNIQUE (legacy_purchase_id);


--
-- Name: access_purchaseorderlineitem_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY access_purchaseorderlineitem
    ADD CONSTRAINT access_purchaseorderlineitem_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_message_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_user_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_key UNIQUE (user_id, group_id);


--
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_user_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_key UNIQUE (user_id, permission_id);


--
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_comment_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY django_comment_flags
    ADD CONSTRAINT django_comment_flags_pkey PRIMARY KEY (id);


--
-- Name: django_comment_flags_user_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY django_comment_flags
    ADD CONSTRAINT django_comment_flags_user_id_key UNIQUE (user_id, comment_id, flag);


--
-- Name: django_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY django_comments
    ADD CONSTRAINT django_comments_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: djcelery_crontabschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_crontabschedule
    ADD CONSTRAINT djcelery_crontabschedule_pkey PRIMARY KEY (id);


--
-- Name: djcelery_intervalschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_intervalschedule
    ADD CONSTRAINT djcelery_intervalschedule_pkey PRIMARY KEY (id);


--
-- Name: djcelery_periodictask_name_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_periodictask
    ADD CONSTRAINT djcelery_periodictask_name_key UNIQUE (name);


--
-- Name: djcelery_periodictask_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_periodictask
    ADD CONSTRAINT djcelery_periodictask_pkey PRIMARY KEY (id);


--
-- Name: djcelery_periodictasks_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_periodictasks
    ADD CONSTRAINT djcelery_periodictasks_pkey PRIMARY KEY (ident);


--
-- Name: djcelery_taskstate_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_taskstate
    ADD CONSTRAINT djcelery_taskstate_pkey PRIMARY KEY (id);


--
-- Name: djcelery_taskstate_task_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_taskstate
    ADD CONSTRAINT djcelery_taskstate_task_id_key UNIQUE (task_id);


--
-- Name: djcelery_workerstate_hostname_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_workerstate
    ADD CONSTRAINT djcelery_workerstate_hostname_key UNIQUE (hostname);


--
-- Name: djcelery_workerstate_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY djcelery_workerstate
    ADD CONSTRAINT djcelery_workerstate_pkey PRIMARY KEY (id);


--
-- Name: docvault_doc_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY docvault_doc
    ADD CONSTRAINT docvault_doc_pkey PRIMARY KEY (id);


--
-- Name: docvault_page_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY docvault_page
    ADD CONSTRAINT docvault_page_pkey PRIMARY KEY (id);


--
-- Name: epsitest_ExperimentalNum_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY epsitest
    ADD CONSTRAINT "epsitest_ExperimentalNum_key" UNIQUE ("ExperimentalNum");


--
-- Name: epsitest_FlavorNumber_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY epsitest
    ADD CONSTRAINT "epsitest_FlavorNumber_key" UNIQUE ("FlavorNumber");


--
-- Name: epsitest_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY epsitest
    ADD CONSTRAINT epsitest_pkey PRIMARY KEY ("ProductID");


--
-- Name: fdileague_game_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY fdileague_game
    ADD CONSTRAINT fdileague_game_pkey PRIMARY KEY (id);


--
-- Name: fdileague_player_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY fdileague_player
    ADD CONSTRAINT fdileague_player_pkey PRIMARY KEY (id);


--
-- Name: fdileague_scoring_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY fdileague_scoring
    ADD CONSTRAINT fdileague_scoring_pkey PRIMARY KEY (id);


--
-- Name: fdileague_team_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY fdileague_team
    ADD CONSTRAINT fdileague_team_pkey PRIMARY KEY (id);


--
-- Name: fdileague_teamstats_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY fdileague_teamstats
    ADD CONSTRAINT fdileague_teamstats_pkey PRIMARY KEY (id);


--
-- Name: fdileague_yearscore_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY fdileague_yearscore
    ADD CONSTRAINT fdileague_yearscore_pkey PRIMARY KEY (id);


--
-- Name: flavor_usage_application_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY flavor_usage_application
    ADD CONSTRAINT flavor_usage_application_pkey PRIMARY KEY (id);


--
-- Name: flavor_usage_applicationtype_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY flavor_usage_applicationtype
    ADD CONSTRAINT flavor_usage_applicationtype_pkey PRIMARY KEY (id);


--
-- Name: haccp_koshergroup_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY haccp_koshergroup
    ADD CONSTRAINT haccp_koshergroup_pkey PRIMARY KEY (id);


--
-- Name: haccp_qualitytest_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY haccp_qualitytest
    ADD CONSTRAINT haccp_qualitytest_pkey PRIMARY KEY (id);


--
-- Name: haccp_receivinglog_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY haccp_receivinglog
    ADD CONSTRAINT haccp_receivinglog_pkey PRIMARY KEY (id);


--
-- Name: haccp_thermometertest_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY haccp_thermometertest
    ADD CONSTRAINT haccp_thermometertest_pkey PRIMARY KEY (qualitytest_ptr_id);


--
-- Name: haccp_tobaccobeetletest_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY haccp_tobaccobeetletest
    ADD CONSTRAINT haccp_tobaccobeetletest_pkey PRIMARY KEY (qualitytest_ptr_id);


--
-- Name: haccp_watertest_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY haccp_watertest
    ADD CONSTRAINT haccp_watertest_pkey PRIMARY KEY (id);


--
-- Name: lot_lot_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY lot_lot
    ADD CONSTRAINT lot_lot_pkey PRIMARY KEY (id);


--
-- Name: newqc_experimentalretain_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_experimentalretain
    ADD CONSTRAINT newqc_experimentalretain_pkey PRIMARY KEY (id);


--
-- Name: newqc_importretain_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_importretain
    ADD CONSTRAINT newqc_importretain_pkey PRIMARY KEY (id);


--
-- Name: newqc_lot_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_lot
    ADD CONSTRAINT newqc_lot_pkey PRIMARY KEY (id);


--
-- Name: newqc_productinfo_flavor_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_productinfo
    ADD CONSTRAINT newqc_productinfo_flavor_id_key UNIQUE (flavor_id);


--
-- Name: newqc_productinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_productinfo
    ADD CONSTRAINT newqc_productinfo_pkey PRIMARY KEY (id);


--
-- Name: newqc_retain_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_retain
    ADD CONSTRAINT newqc_retain_pkey PRIMARY KEY (id);


--
-- Name: newqc_rmimportretain_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_rmimportretain
    ADD CONSTRAINT newqc_rmimportretain_pkey PRIMARY KEY (id);


--
-- Name: newqc_rminfo_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_rminfo
    ADD CONSTRAINT newqc_rminfo_pkey PRIMARY KEY (id);


--
-- Name: newqc_rmretain_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_rmretain
    ADD CONSTRAINT newqc_rmretain_pkey PRIMARY KEY (id);


--
-- Name: newqc_testcard_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY newqc_testcard
    ADD CONSTRAINT newqc_testcard_pkey PRIMARY KEY (id);


--
-- Name: performance_appraisal_department_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY performance_appraisal_department
    ADD CONSTRAINT performance_appraisal_department_pkey PRIMARY KEY (id);


--
-- Name: performance_appraisal_performanceappraisal_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY performance_appraisal_performanceappraisal
    ADD CONSTRAINT performance_appraisal_performanceappraisal_pkey PRIMARY KEY (id);


--
-- Name: personnel_userprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY personnel_userprofile
    ADD CONSTRAINT personnel_userprofile_pkey PRIMARY KEY (id);


--
-- Name: personnel_userprofile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY personnel_userprofile
    ADD CONSTRAINT personnel_userprofile_user_id_key UNIQUE (user_id);


--
-- Name: reversion_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY reversion_revision
    ADD CONSTRAINT reversion_revision_pkey PRIMARY KEY (id);


--
-- Name: reversion_version_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY reversion_version
    ADD CONSTRAINT reversion_version_pkey PRIMARY KEY (id);


--
-- Name: salesorders_lineitem_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY salesorders_lineitem
    ADD CONSTRAINT salesorders_lineitem_pkey PRIMARY KEY (id);


--
-- Name: salesorders_salesordernumber_number_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY salesorders_salesordernumber
    ADD CONSTRAINT salesorders_salesordernumber_number_key UNIQUE (number);


--
-- Name: salesorders_salesordernumber_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY salesorders_salesordernumber
    ADD CONSTRAINT salesorders_salesordernumber_pkey PRIMARY KEY (id);


--
-- Name: siteconfig_siteconfiguration_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY siteconfig_siteconfiguration
    ADD CONSTRAINT siteconfig_siteconfiguration_pkey PRIMARY KEY (id);


--
-- Name: solutionfixer_solution_ingredient_id_key; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY solutionfixer_solution
    ADD CONSTRAINT solutionfixer_solution_ingredient_id_key UNIQUE (ingredient_id);


--
-- Name: solutionfixer_solution_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY solutionfixer_solution
    ADD CONSTRAINT solutionfixer_solution_pkey PRIMARY KEY (id);


--
-- Name: solutionfixer_solutionmatchcache_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY solutionfixer_solutionmatchcache
    ADD CONSTRAINT solutionfixer_solutionmatchcache_pkey PRIMARY KEY (my_pk);


--
-- Name: solutionfixer_solutionstatus_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY solutionfixer_solutionstatus
    ADD CONSTRAINT solutionfixer_solutionstatus_pkey PRIMARY KEY (id);


--
-- Name: south_migrationhistory_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY south_migrationhistory
    ADD CONSTRAINT south_migrationhistory_pkey PRIMARY KEY (id);


--
-- Name: supplier_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY supplier
    ADD CONSTRAINT supplier_pkey PRIMARY KEY (id);


--
-- Name: thumbnail_kvstore_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY thumbnail_kvstore
    ADD CONSTRAINT thumbnail_kvstore_pkey PRIMARY KEY (key);


--
-- Name: unified_adapter_application_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY unified_adapter_application
    ADD CONSTRAINT unified_adapter_application_pkey PRIMARY KEY (id);


--
-- Name: unified_adapter_applicationtype_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY unified_adapter_applicationtype
    ADD CONSTRAINT unified_adapter_applicationtype_pkey PRIMARY KEY (id);


--
-- Name: unified_adapter_productinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: www-data; Tablespace: 
--

ALTER TABLE ONLY unified_adapter_productinfo
    ADD CONSTRAINT unified_adapter_productinfo_pkey PRIMARY KEY (id);


--
-- Name: Flavors - Formulae_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX "Flavors - Formulae_flavor_id" ON "Flavors - Formulae" USING btree (flavor_id);


--
-- Name: Flavors - Formulae_ingredient_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX "Flavors - Formulae_ingredient_id" ON "Flavors - Formulae" USING btree (ingredient_id);


--
-- Name: Raw Materials_sub_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX "Raw Materials_sub_flavor_id" ON "Raw Materials" USING btree (sub_flavor_id);


--
-- Name: access_epsiformula_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_epsiformula_flavor_id ON access_epsiformula USING btree (flavor_id);


--
-- Name: access_epsiformula_ingredient_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_epsiformula_ingredient_id ON access_epsiformula USING btree (ingredient_id);


--
-- Name: access_flavoriterorder_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_flavoriterorder_flavor_id ON access_flavoriterorder USING btree (flavor_id);


--
-- Name: access_formulatree_formula_row_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_formulatree_formula_row_id ON access_formulatree USING btree (formula_row_id);


--
-- Name: access_formulatree_leaf; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_formulatree_leaf ON access_formulatree USING btree (leaf);


--
-- Name: access_formulatree_node_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_formulatree_node_flavor_id ON access_formulatree USING btree (node_flavor_id);


--
-- Name: access_formulatree_node_ingredient_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_formulatree_node_ingredient_id ON access_formulatree USING btree (node_ingredient_id);


--
-- Name: access_formulatree_root_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_formulatree_root_flavor_id ON access_formulatree USING btree (root_flavor_id);


--
-- Name: access_leafweight_ingredient_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_leafweight_ingredient_id ON access_leafweight USING btree (ingredient_id);


--
-- Name: access_leafweight_root_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_leafweight_root_flavor_id ON access_leafweight USING btree (root_flavor_id);


--
-- Name: access_purchaseorder_ship_to_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_purchaseorder_ship_to_id ON access_purchaseorder USING btree (ship_to_id);


--
-- Name: access_purchaseorder_shipper_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_purchaseorder_shipper_id ON access_purchaseorder USING btree (shipper_id);


--
-- Name: access_purchaseorder_supplier_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_purchaseorder_supplier_id ON access_purchaseorder USING btree (supplier_id);


--
-- Name: access_purchaseorderlineitem_po_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_purchaseorderlineitem_po_id ON access_purchaseorderlineitem USING btree (po_id);


--
-- Name: access_purchaseorderlineitem_raw_material_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX access_purchaseorderlineitem_raw_material_id ON access_purchaseorderlineitem USING btree (raw_material_id);


--
-- Name: auth_message_user_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- Name: django_comment_flags_comment_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX django_comment_flags_comment_id ON django_comment_flags USING btree (comment_id);


--
-- Name: django_comment_flags_flag; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX django_comment_flags_flag ON django_comment_flags USING btree (flag);


--
-- Name: django_comment_flags_user_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX django_comment_flags_user_id ON django_comment_flags USING btree (user_id);


--
-- Name: django_comments_content_type_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX django_comments_content_type_id ON django_comments USING btree (content_type_id);


--
-- Name: django_comments_site_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX django_comments_site_id ON django_comments USING btree (site_id);


--
-- Name: django_comments_user_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX django_comments_user_id ON django_comments USING btree (user_id);


--
-- Name: djcelery_periodictask_crontab_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_periodictask_crontab_id ON djcelery_periodictask USING btree (crontab_id);


--
-- Name: djcelery_periodictask_interval_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_periodictask_interval_id ON djcelery_periodictask USING btree (interval_id);


--
-- Name: djcelery_taskstate_hidden; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_taskstate_hidden ON djcelery_taskstate USING btree (hidden);


--
-- Name: djcelery_taskstate_name; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_taskstate_name ON djcelery_taskstate USING btree (name);


--
-- Name: djcelery_taskstate_name_like; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_taskstate_name_like ON djcelery_taskstate USING btree (name varchar_pattern_ops);


--
-- Name: djcelery_taskstate_state; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_taskstate_state ON djcelery_taskstate USING btree (state);


--
-- Name: djcelery_taskstate_state_like; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_taskstate_state_like ON djcelery_taskstate USING btree (state varchar_pattern_ops);


--
-- Name: djcelery_taskstate_tstamp; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_taskstate_tstamp ON djcelery_taskstate USING btree (tstamp);


--
-- Name: djcelery_taskstate_worker_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_taskstate_worker_id ON djcelery_taskstate USING btree (worker_id);


--
-- Name: djcelery_workerstate_last_heartbeat; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX djcelery_workerstate_last_heartbeat ON djcelery_workerstate USING btree (last_heartbeat);


--
-- Name: docvault_doc_user_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX docvault_doc_user_id ON docvault_doc USING btree (user_id);


--
-- Name: docvault_page_doc_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX docvault_page_doc_id ON docvault_page USING btree (doc_id);


--
-- Name: fdileague_scoring_extra_point_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX fdileague_scoring_extra_point_id ON fdileague_scoring USING btree (extra_point_id);


--
-- Name: fdileague_scoring_game_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX fdileague_scoring_game_id ON fdileague_scoring USING btree (game_id);


--
-- Name: fdileague_scoring_qb_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX fdileague_scoring_qb_id ON fdileague_scoring USING btree (qb_id);


--
-- Name: fdileague_scoring_scorer_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX fdileague_scoring_scorer_id ON fdileague_scoring USING btree (scorer_id);


--
-- Name: fdileague_scoring_team_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX fdileague_scoring_team_id ON fdileague_scoring USING btree (team_id);


--
-- Name: fdileague_yearscore_player_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX fdileague_yearscore_player_id ON fdileague_yearscore USING btree (player_id);


--
-- Name: flavor_usage_application_application_type_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX flavor_usage_application_application_type_id ON flavor_usage_application USING btree (application_type_id);


--
-- Name: flavor_usage_application_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX flavor_usage_application_flavor_id ON flavor_usage_application USING btree (flavor_id);


--
-- Name: haccp_receivinglog_kosher_group_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX haccp_receivinglog_kosher_group_id ON haccp_receivinglog USING btree (kosher_group_id);


--
-- Name: haccp_receivinglog_supplier_id_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX haccp_receivinglog_supplier_id_id ON haccp_receivinglog USING btree (supplier_id_id);


--
-- Name: lot_lot_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX lot_lot_flavor_id ON lot_lot USING btree (flavor_id);


--
-- Name: newqc_rmretain_ir_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX newqc_rmretain_ir_id ON newqc_rmretain USING btree (ir_id);


--
-- Name: newqc_testcard_retain_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX newqc_testcard_retain_id ON newqc_testcard USING btree (retain_id);


--
-- Name: performance_appraisal_performanceappraisal_department_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX performance_appraisal_performanceappraisal_department_id ON performance_appraisal_performanceappraisal USING btree (department_id);


--
-- Name: reversion_revision_user_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX reversion_revision_user_id ON reversion_revision USING btree (user_id);


--
-- Name: reversion_version_content_type_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX reversion_version_content_type_id ON reversion_version USING btree (content_type_id);


--
-- Name: reversion_version_revision_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX reversion_version_revision_id ON reversion_version USING btree (revision_id);


--
-- Name: salesorders_lineitem_flavor_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX salesorders_lineitem_flavor_id ON salesorders_lineitem USING btree (flavor_id);


--
-- Name: salesorders_lineitem_salesordernumber_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX salesorders_lineitem_salesordernumber_id ON salesorders_lineitem USING btree (salesordernumber_id);


--
-- Name: salesorders_salesordernumber_customer_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX salesorders_salesordernumber_customer_id ON salesorders_salesordernumber USING btree (customer_id);


--
-- Name: siteconfig_siteconfiguration_site_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX siteconfig_siteconfiguration_site_id ON siteconfig_siteconfiguration USING btree (site_id);


--
-- Name: solutionfixer_solution_my_base_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX solutionfixer_solution_my_base_id ON solutionfixer_solution USING btree (my_base_id);


--
-- Name: solutionfixer_solution_my_solvent_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX solutionfixer_solution_my_solvent_id ON solutionfixer_solution USING btree (my_solvent_id);


--
-- Name: solutionfixer_solution_status_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX solutionfixer_solution_status_id ON solutionfixer_solution USING btree (status_id);


--
-- Name: solutionfixer_solutionmatchcache_solution_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX solutionfixer_solutionmatchcache_solution_id ON solutionfixer_solutionmatchcache USING btree (solution_id);


--
-- Name: unified_adapter_application_application_type_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX unified_adapter_application_application_type_id ON unified_adapter_application USING btree (application_type_id);


--
-- Name: unified_adapter_application_product_info_id; Type: INDEX; Schema: public; Owner: www-data; Tablespace: 
--

CREATE INDEX unified_adapter_application_product_info_id ON unified_adapter_application USING btree (product_info_id);


--
-- Name: Flavors - Formulae_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY "Flavors - Formulae"
    ADD CONSTRAINT "Flavors - Formulae_flavor_id_fkey" FOREIGN KEY (flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: Flavors - Formulae_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY "Flavors - Formulae"
    ADD CONSTRAINT "Flavors - Formulae_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES "Raw Materials"("RawMaterialCode") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: Products - Special Information_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY "Products - Special Information"
    ADD CONSTRAINT "Products - Special Information_flavor_id_fkey" FOREIGN KEY (flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_epsiformula_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_epsiformula
    ADD CONSTRAINT access_epsiformula_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES "Raw Materials"("RawMaterialCode") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_flavoriterorder_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_flavoriterorder
    ADD CONSTRAINT access_flavoriterorder_flavor_id_fkey FOREIGN KEY (flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_formulatree_formula_row_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_formulatree
    ADD CONSTRAINT access_formulatree_formula_row_id_fkey FOREIGN KEY (formula_row_id) REFERENCES "Flavors - Formulae"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_formulatree_node_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_formulatree
    ADD CONSTRAINT access_formulatree_node_flavor_id_fkey FOREIGN KEY (node_flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_formulatree_node_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_formulatree
    ADD CONSTRAINT access_formulatree_node_ingredient_id_fkey FOREIGN KEY (node_ingredient_id) REFERENCES "Raw Materials"("RawMaterialCode") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_formulatree_root_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_formulatree
    ADD CONSTRAINT access_formulatree_root_flavor_id_fkey FOREIGN KEY (root_flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_leafweight_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_leafweight
    ADD CONSTRAINT access_leafweight_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES "Raw Materials"("RawMaterialCode") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_leafweight_root_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_leafweight
    ADD CONSTRAINT access_leafweight_root_flavor_id_fkey FOREIGN KEY (root_flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_purchaseorder_ship_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_purchaseorder
    ADD CONSTRAINT access_purchaseorder_ship_to_id_fkey FOREIGN KEY (ship_to_id) REFERENCES "ShipTo"("ShipToID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_purchaseorder_shipper_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_purchaseorder
    ADD CONSTRAINT access_purchaseorder_shipper_id_fkey FOREIGN KEY (shipper_id) REFERENCES "Shippers"("ShipperID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_purchaseorder_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_purchaseorder
    ADD CONSTRAINT access_purchaseorder_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES "Suppliers"("ID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_purchaseorderlineitem_po_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_purchaseorderlineitem
    ADD CONSTRAINT access_purchaseorderlineitem_po_id_fkey FOREIGN KEY (po_id) REFERENCES access_purchaseorder(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_purchaseorderlineitem_raw_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_purchaseorderlineitem
    ADD CONSTRAINT access_purchaseorderlineitem_raw_material_id_fkey FOREIGN KEY (raw_material_id) REFERENCES "Raw Materials"("RawMaterialCode") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_comment_flags_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY django_comment_flags
    ADD CONSTRAINT django_comment_flags_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES django_comments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_comment_flags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY django_comment_flags
    ADD CONSTRAINT django_comment_flags_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_comments_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY django_comments
    ADD CONSTRAINT django_comments_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_comments_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY django_comments
    ADD CONSTRAINT django_comments_site_id_fkey FOREIGN KEY (site_id) REFERENCES django_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY django_comments
    ADD CONSTRAINT django_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: djcelery_periodictask_crontab_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY djcelery_periodictask
    ADD CONSTRAINT djcelery_periodictask_crontab_id_fkey FOREIGN KEY (crontab_id) REFERENCES djcelery_crontabschedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: djcelery_periodictask_interval_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY djcelery_periodictask
    ADD CONSTRAINT djcelery_periodictask_interval_id_fkey FOREIGN KEY (interval_id) REFERENCES djcelery_intervalschedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: djcelery_taskstate_worker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY djcelery_taskstate
    ADD CONSTRAINT djcelery_taskstate_worker_id_fkey FOREIGN KEY (worker_id) REFERENCES djcelery_workerstate(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: docvault_doc_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY docvault_doc
    ADD CONSTRAINT docvault_doc_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: docvault_page_doc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY docvault_page
    ADD CONSTRAINT docvault_page_doc_id_fkey FOREIGN KEY (doc_id) REFERENCES docvault_doc(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fdileague_scoring_extra_point_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY fdileague_scoring
    ADD CONSTRAINT fdileague_scoring_extra_point_id_fkey FOREIGN KEY (extra_point_id) REFERENCES fdileague_player(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fdileague_scoring_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY fdileague_scoring
    ADD CONSTRAINT fdileague_scoring_game_id_fkey FOREIGN KEY (game_id) REFERENCES fdileague_game(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fdileague_scoring_qb_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY fdileague_scoring
    ADD CONSTRAINT fdileague_scoring_qb_id_fkey FOREIGN KEY (qb_id) REFERENCES fdileague_player(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fdileague_scoring_scorer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY fdileague_scoring
    ADD CONSTRAINT fdileague_scoring_scorer_id_fkey FOREIGN KEY (scorer_id) REFERENCES fdileague_player(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fdileague_scoring_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY fdileague_scoring
    ADD CONSTRAINT fdileague_scoring_team_id_fkey FOREIGN KEY (team_id) REFERENCES fdileague_team(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fdileague_yearscore_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY fdileague_yearscore
    ADD CONSTRAINT fdileague_yearscore_player_id_fkey FOREIGN KEY (player_id) REFERENCES fdileague_player(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: flavor_id_refs_ProductID_1813cbc4; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_epsiformula
    ADD CONSTRAINT "flavor_id_refs_ProductID_1813cbc4" FOREIGN KEY (flavor_id) REFERENCES epsitest("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: flavor_usage_application_application_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY flavor_usage_application
    ADD CONSTRAINT flavor_usage_application_application_type_id_fkey FOREIGN KEY (application_type_id) REFERENCES flavor_usage_applicationtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: flavor_usage_application_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY flavor_usage_application
    ADD CONSTRAINT flavor_usage_application_flavor_id_fkey FOREIGN KEY (flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: haccp_receivinglog_kosher_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY haccp_receivinglog
    ADD CONSTRAINT haccp_receivinglog_kosher_group_id_fkey FOREIGN KEY (kosher_group_id) REFERENCES haccp_koshergroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: haccp_thermometertest_qualitytest_ptr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY haccp_thermometertest
    ADD CONSTRAINT haccp_thermometertest_qualitytest_ptr_id_fkey FOREIGN KEY (qualitytest_ptr_id) REFERENCES haccp_qualitytest(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: haccp_tobaccobeetletest_qualitytest_ptr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY haccp_tobaccobeetletest
    ADD CONSTRAINT haccp_tobaccobeetletest_qualitytest_ptr_id_fkey FOREIGN KEY (qualitytest_ptr_id) REFERENCES haccp_qualitytest(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ir_id_refs_id_2ec2ed70; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY newqc_retain
    ADD CONSTRAINT ir_id_refs_id_2ec2ed70 FOREIGN KEY (ir_id) REFERENCES newqc_importretain(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: legacy_purchase_id_refs_POEntry_b77a1cd9; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY access_purchaseorderlineitem
    ADD CONSTRAINT "legacy_purchase_id_refs_POEntry_b77a1cd9" FOREIGN KEY (legacy_purchase_id) REFERENCES "Purchases"("POEntry") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: lot_lot_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY lot_lot
    ADD CONSTRAINT lot_lot_flavor_id_fkey FOREIGN KEY (flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: newqc_lot_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY newqc_lot
    ADD CONSTRAINT newqc_lot_flavor_id_fkey FOREIGN KEY (flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: newqc_productinfo_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY newqc_productinfo
    ADD CONSTRAINT newqc_productinfo_flavor_id_fkey FOREIGN KEY (flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: newqc_retain_lot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY newqc_retain
    ADD CONSTRAINT newqc_retain_lot_id_fkey FOREIGN KEY (lot_id) REFERENCES newqc_lot(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: newqc_rmretain_ir_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY newqc_rmretain
    ADD CONSTRAINT newqc_rmretain_ir_id_fkey FOREIGN KEY (ir_id) REFERENCES newqc_rmimportretain(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: performance_appraisal_performanceappraisal_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY performance_appraisal_performanceappraisal
    ADD CONSTRAINT performance_appraisal_performanceappraisal_department_id_fkey FOREIGN KEY (department_id) REFERENCES performance_appraisal_department(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: personnel_userprofile_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY personnel_userprofile
    ADD CONSTRAINT personnel_userprofile_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reversion_revision_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY reversion_revision
    ADD CONSTRAINT reversion_revision_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reversion_version_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY reversion_version
    ADD CONSTRAINT reversion_version_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reversion_version_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY reversion_version
    ADD CONSTRAINT reversion_version_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES reversion_revision(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: salesorders_lineitem_flavor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY salesorders_lineitem
    ADD CONSTRAINT salesorders_lineitem_flavor_id_fkey FOREIGN KEY (flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: salesorders_lineitem_salesordernumber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY salesorders_lineitem
    ADD CONSTRAINT salesorders_lineitem_salesordernumber_id_fkey FOREIGN KEY (salesordernumber_id) REFERENCES salesorders_salesordernumber(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: salesorders_salesordernumber_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY salesorders_salesordernumber
    ADD CONSTRAINT salesorders_salesordernumber_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES "Customers"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: siteconfig_siteconfiguration_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY siteconfig_siteconfiguration
    ADD CONSTRAINT siteconfig_siteconfiguration_site_id_fkey FOREIGN KEY (site_id) REFERENCES django_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: solutionfixer_solution_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY solutionfixer_solution
    ADD CONSTRAINT solutionfixer_solution_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES "Raw Materials"("RawMaterialCode") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: solutionfixer_solution_my_base_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY solutionfixer_solution
    ADD CONSTRAINT solutionfixer_solution_my_base_id_fkey FOREIGN KEY (my_base_id) REFERENCES "Raw Materials"("RawMaterialCode") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: solutionfixer_solution_my_solvent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY solutionfixer_solution
    ADD CONSTRAINT solutionfixer_solution_my_solvent_id_fkey FOREIGN KEY (my_solvent_id) REFERENCES "Raw Materials"("RawMaterialCode") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: solutionfixer_solutionmatchcache_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY solutionfixer_solutionmatchcache
    ADD CONSTRAINT solutionfixer_solutionmatchcache_solution_id_fkey FOREIGN KEY (solution_id) REFERENCES solutionfixer_solution(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: status_id_refs_id_7a8d0e1b; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY solutionfixer_solution
    ADD CONSTRAINT status_id_refs_id_7a8d0e1b FOREIGN KEY (status_id) REFERENCES solutionfixer_solutionstatus(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sub_flavor_id_refs_ProductID_3cf79d16; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY "Raw Materials"
    ADD CONSTRAINT "sub_flavor_id_refs_ProductID_3cf79d16" FOREIGN KEY (sub_flavor_id) REFERENCES "Products"("ProductID") DEFERRABLE INITIALLY DEFERRED;


--
-- Name: supplier_id_id_refs_id_b2dc83c9; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY haccp_receivinglog
    ADD CONSTRAINT supplier_id_id_refs_id_b2dc83c9 FOREIGN KEY (supplier_id_id) REFERENCES supplier(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: unified_adapter_application_application_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY unified_adapter_application
    ADD CONSTRAINT unified_adapter_application_application_type_id_fkey FOREIGN KEY (application_type_id) REFERENCES unified_adapter_applicationtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: unified_adapter_application_product_info_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY unified_adapter_application
    ADD CONSTRAINT unified_adapter_application_product_info_id_fkey FOREIGN KEY (product_info_id) REFERENCES unified_adapter_productinfo(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: unified_adapter_productinfo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: www-data
--

ALTER TABLE ONLY unified_adapter_productinfo
    ADD CONSTRAINT unified_adapter_productinfo_id_fkey FOREIGN KEY (id) REFERENCES unified_adapter_productinfo(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

