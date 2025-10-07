def get_dataset_summary():
    "This will be visible to the agent at all times, so keep it short, but let the agent know if the dataset can answer the question of the user."
    return """
    Point Topic Telecommunications Ontology: Comprehensive structured knowledge base for UK telecom market analysis.
    
    CORE CAPABILITIES:
    - Organization analysis: ISPs, network operators, corporate relationships, ownership structures
    - Infrastructure mapping: Networks, coverage areas, technology types (fiber, cable, wireless)
    - Service analysis: Broadband offerings, pricing, technology specifications
    - Market structure: Retail vs wholesale relationships, consolidations, mergers
    - Temporal analysis: Historical changes, entity lifecycles, market evolution
    - Geographical data: Coverage areas, location-based analysis
    
    QUERY TYPES SUPPORTED:
    - "Who owns/operates network X?" - Corporate relationships and ownership
    - "Which ISPs use fiber networks?" - Technology and service analysis  
    - "Show market consolidations over time" - Historical M&A analysis
    - "What services does ISP X offer?" - Service portfolio analysis
    - "Which networks cover location Y?" - Geographic coverage analysis
    - "Find retail-only ISPs" - Business model classification
    
    DATA SCOPE: UK telecommunications market with 3-tier ontology (core/business/documents), temporal validity, enforced relationships.
    """

def get_db_info():
    return f"""
    {DB_INFO}

    {DB_SCHEMA}

    {SQL_EXAMPLES}
    """

DB_INFO = """
ONTOLOGY STRUCTURE AND QUERYING GUIDE

The Point Topic Telecommunications Ontology is a structured knowledge representation system for telecommunications market data, 
implemented as a relational database in Snowflake with the schema: ONTOLOGY_NEW.{entity_type}.{entity_name}

ONTOLOGY LEVELS:

- 'core': Ontologically-defined foundational entities and relationships (~10-500 rows per table)
  - Stable schema, rarely changes
  - Enforced foreign key constraints and validation rules
  - Contains fundamental telecom concepts (organizations, networks, links, services)
  
- 'business': Core entities plus business data entities (thousands to millions of rows)
  - Includes coverage data, subscriber counts, service offerings
  - May have relaxed constraints for data ingestion flexibility
  
- 'business_documents': All above plus document/dataset metadata entities
  - DCAT-compliant dataset and publication metadata
  - Links business data to source documents and publications
  - Currently mainly news items from ISPReview.co.uk

ENTITY TYPES AND DATABASE SCHEMA:

1. CLASS (ONTOLOGY_NEW.CLASS.{entity_name})
   - Fundamental concepts/things in telecom domain
   - Examples: foaf_organization, cto_network, cto_link, cto_broadband_service
   - Represent "what things are" (ISPs, networks, services, locations)

2. OBJECT_PROPERTY (ONTOLOGY_NEW.OBJECT_PROPERTY.{entity_name}) 
   - Relationships between classes
   - Examples: cto_uses_network (ISP uses Network), cto_owns_network (Operator owns Network)
   - Represent "how things relate to each other"

3. DATA_PROPERTY (ONTOLOGY_NEW.DATA_PROPERTY.{entity_name})
   - Attributes/properties of classes with specific values
   - Examples: cto_is_retail_only (boolean), cto_has_subscribers (integer)
   - Represent "what properties things have"

TEMPORAL VALIDITY:

All entities support temporal validity with valid_from and valid_to date fields, enabling historical analysis
and tracking of changes over time (e.g., when ISP changed ownership, when network was decommissioned).

IMPORTANT NOTE ON COLUMN TYPES:
Despite the metadata schema showing date types, all columns are actually stored as VARCHAR in Snowflake.
When filtering by dates, convert varchar to date using TO_DATE() function (Snowflake syntax).

GEOGRAPHICAL SCOPE:

Primarily UK telecommunications market, with country field for international expansion.
Location entities use standard geographical identifiers (postcodes, administrative areas).

METADATA ACCESS:

Entity schemas and constraints are defined in ONTOLOGY_NEW.UTILS.UTIL_ONTO_METADATA_ENTITY table.
This contains JSON metadata for each entity including column definitions, foreign keys, and validation rules.

OTHER NOTES:

Organization types are: "ISP", "Network Operator", "Non Telco Organization"
United Kingdom is spelled as: "United Kingdom"
Tip for querying: It is recommended to start with a simple query to a table like FOAF_ORGANIZATION, CTO_NETWORK, CTO_USES_NETWORK 
or similar to check the spelling of values you are interested in.
"""

SQL_EXAMPLES = [
    {
        'request': 'List all ISPs',
        'response': """
SELECT * 
FROM ONTOLOGY_NEW.CLASS.FOAF_ORGANIZATION 
WHERE organization_name IN (
    SELECT organization_name 
    FROM ONTOLOGY_NEW.OBJECT_PROPERTY.CTO_IS_ORGANIZATION_TYPE 
    WHERE organization_type_name = 'ISP'
)
        """
    },
    {
        'request': 'Get all networks',
        'response': """
SELECT * 
FROM ONTOLOGY_NEW.CLASS.CTO_NETWORK
        """
    },
    {
        'request': 'Find retail-only ISPs',
        'response': """
SELECT * 
FROM ONTOLOGY_NEW.DATA_PROPERTY.CTO_IS_RETAIL_ONLY 
WHERE is_retail_only = 1
        """
    },
    {
        'request': 'Show current ISP-Network relationships',
        'response': """
SELECT 
    un.isp_name,
    un.network_name,
    un.valid_from,
    un.valid_to
FROM ONTOLOGY_NEW.OBJECT_PROPERTY.CTO_USES_NETWORK un
WHERE un.valid_to IS NULL OR TO_DATE(un.valid_to) > CURRENT_DATE()
        """
    },
    {
        'request': 'Show network ownership relationships',
        'response': """
SELECT 
    network_operator_name,
    network_name,
    valid_from,
    valid_to
FROM ONTOLOGY_NEW.OBJECT_PROPERTY.CTO_OWNS_NETWORK
        """
    },
    {
        'request': 'Find service offerings by ISPs',
        'response': """
SELECT 
    obs.isp_name,
    obs.broadband_service_name,
    bs.tech,
    bs.fastest_down,
    bs.fastest_up,
    bs.monthly_cost
FROM ONTOLOGY_NEW.OBJECT_PROPERTY.CTO_OFFERS_BROADBAND_SERVICE obs
JOIN ONTOLOGY_NEW.CLASS.CTO_BROADBAND_SERVICE bs 
    ON obs.broadband_service_name = bs.broadband_service_name
        """
    },
    {
        'request': 'Get active organizations only',
        'response': """
SELECT * 
FROM ONTOLOGY_NEW.CLASS.FOAF_ORGANIZATION
WHERE valid_to IS NULL OR TO_DATE(valid_to) > CURRENT_DATE()
        """
    },
    {
        'request': 'Historical organizatin snapshot from 2023',
        'response': """
SELECT * 
FROM ONTOLOGY_NEW.CLASS.FOAF_ORGANIZATION
WHERE TO_DATE(valid_from) <= '2023-01-01' 
    AND (valid_to IS NULL OR TO_DATE(valid_to) > '2023-01-01')
        """
    },
    {
        'request': 'Analyze market structure with organization relationships',
        'response': """
SELECT 
    o.organization_name,
    ot.organization_type_name,
    o.country
FROM ONTOLOGY_NEW.CLASS.FOAF_ORGANIZATION o
JOIN ONTOLOGY_NEW.OBJECT_PROPERTY.CTO_IS_ORGANIZATION_TYPE ot 
    ON o.organization_name = ot.organization_name
        """
    },
    {
        'request': 'Analyze current ISP-network operator-network usage patterns',
        'response': """
SELECT 
    un.isp_name,
    un.network_name,
    own.network_operator_name
FROM ONTOLOGY_NEW.OBJECT_PROPERTY.CTO_USES_NETWORK un
JOIN ONTOLOGY_NEW.OBJECT_PROPERTY.CTO_OWNS_NETWORK own 
    ON un.network_name = own.network_name
WHERE un.valid_to IS NULL OR TO_DATE(un.valid_to) > CURRENT_DATE()
        """
    }
]

# can we not get this directly from snowflake? (ONTOLOGY_NEW.UTILS.UTIL_ONTO_METADATA_ENTITY)
DB_SCHEMA = '''
"ENTITY","METADATA","ID"
"cto_broadband_service","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": null, ""description"": ""Any service specifically related to providing broadband services."", ""parent"": ""cto_service"", ""unique_on"": ""broadband_service_name"", ""children"": null, ""columns"": [{""name"": ""broadband_service_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""service_type"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""isp_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""tech"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""fastest_down"", ""data_types"": ""number"", ""nullable"": true}, {""name"": ""guaranteed_down"", ""data_types"": ""number"", ""nullable"": true}, {""name"": ""fastest_up"", ""data_types"": ""number"", ""nullable"": true}, {""name"": ""guaranteed_up"", ""data_types"": ""number"", ""nullable"": true}, {""name"": ""monthly_cost"", ""data_types"": ""number"", ""nullable"": true}, {""name"": ""setup_cost"", ""data_types"": ""number"", ""nullable"": true}, {""name"": ""local_currency"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""contract_length"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""bundle_home_phone"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""bundle_mobile_phone"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""bundle_video"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""country"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""tech"", ""references_table"": ""cto_link"", ""references_column"": ""link_name""}], ""enforced_foreign_keys"": false, ""label"": ""Broadband Services"", ""in_ontology"": ""business""}","af5813bb-3e82-4a54-a49c-c367152e0e38"
"cto_concept_entity","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": null, ""description"": ""A conceptual entity. Generally, an entity that does not occupy space in the physical world. Mutually exclusive with cto_physical_entities."", ""parent"": null, ""unique_on"": ""concept_entity_name"", ""children"": [""foaf_organization""], ""columns"": [{""name"": ""concept_entity_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Conceptual Entities"", ""in_ontology"": ""business""}","90d24dd5-895c-4cc6-a67f-410ad6ca5f8a"
"cto_has_corporate_relationship","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""cto_organization""], ""description"": ""Indicates that one organization has an ownership/investment stake in another organization."", ""columns"": [{""name"": ""relationship_from"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""relationship_to"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""relationship_type"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""relationship_from"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}, {""column"": ""relationship_to"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}], ""enforced_foreign_keys"": true, ""label"": ""Has Corporate Relationship"", ""in_ontology"": ""core""}","910b3e6b-98eb-4d33-a26b-3d153c25f8d7"
"cto_has_coverage_area","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""cto_network"", ""dcterms_location""], ""description"": ""Relates a network to the geographical areas it covers."", ""columns"": [{""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""location_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""country"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""network_name"", ""references_table"": ""cto_network"", ""references_column"": ""network_name""}, {""column"": ""location_name"", ""references_table"": ""dcterms_location"", ""references_column"": ""location_name""}], ""enforced_foreign_keys"": false, ""label"": ""Has Coverage Area"", ""in_ontology"": ""business""}","8283e710-2c62-4b4b-af3e-b327edcfd080"
"cto_has_coverage_data","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""cto_network"", ""dcterms_location""], ""description"": ""coverage level of a network at a location (percentage, population, or otherwise)"", ""columns"": [{""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""location_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""value"", ""data_types"": ""number"", ""nullable"": false}, {""name"": ""unit"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""country"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""network_name"", ""references_table"": ""cto_network"", ""references_column"": ""network_name""}, {""column"": ""location_name"", ""references_table"": ""dcterms_location"", ""references_column"": ""location_name""}], ""enforced_foreign_keys"": true, ""label"": ""Has Coverage Data"", ""in_ontology"": ""business""}","0f975001-22a8-478c-bd79-c034483e9611"
"cto_has_roadworks_location","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""foaf_organization"", ""dcterms_location""], ""description"": ""Relates a telco organization to locations where it is known to promote roadworks."", ""columns"": [{""name"": ""organization_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""location_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""country"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""organization_name"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}, {""column"": ""location_name"", ""references_table"": ""dcterms_location"", ""references_column"": ""location_name""}], ""enforced_foreign_keys"": false, ""label"": ""Has Build Location"", ""in_ontology"": ""business""}","68d14eaa-94df-4c4f-be1c-31dc4519e48c"
"cto_has_subscribers","{""entity_type"": ""data_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""domain"": ""cto_network"", ""range"": ""integer"", ""description"": ""Specifies the number of subscribers for a ISP, network operator or network."", ""columns"": [{""name"": ""isp_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""network_operator_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""link_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""subscriber_count"", ""data_types"": ""integer"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Has Subscribers"", ""in_ontology"": ""business""}","17608312-d08b-450f-aba4-377c575d2ccf"
"cto_is_business_only","{""entity_type"": ""data_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""domain"": ""foaf_organization"", ""range"": ""boolean"", ""description"": ""Specifies whether an organization (ISP or Network Operator) is business-only (exclusively sells to business customers)."", ""columns"": [{""name"": ""isp_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""is_business_only"", ""data_types"": ""boolean"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""isp_name"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}], ""enforced_foreign_keys"": true, ""label"": ""Is Business Only"", ""in_ontology"": ""core""}","29157c3b-7618-4fa5-8044-27ecd0a0d0dd"
"cto_is_consolidated","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""foaf_organization"", ""cto_network""], ""description"": ""Relates a network or organization to the network or organization it is consolidated into."", ""columns"": [{""name"": ""consolidated_from"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""consolidated_to"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""announced_at"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""completed_at"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""is_merged"", ""data_types"": ""boolean"", ""nullable"": true}, {""name"": ""is_acquired"", ""data_types"": ""boolean"", ""nullable"": true}, {""name"": ""is_dissolved"", ""data_types"": ""boolean"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""country"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Is Consolidated"", ""in_ontology"": ""core""}","31be10ed-6d62-4f37-8d77-59abd4be716d"
"cto_is_network_segment","{""entity_type"": ""data_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""domain"": ""cto_network"", ""range"": ""boolean"", ""description"": ""Indicates whether a network represents a segment or part of a larger network infrastructure, rather than a complete network."", ""columns"": [{""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""is_network_segment"", ""data_types"": ""boolean"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""network_name"", ""references_table"": ""cto_network"", ""references_column"": ""network_name""}], ""enforced_foreign_keys"": true, ""label"": ""Is Network Segment"", ""in_ontology"": ""core""}","a607d0fa-4c2f-4e83-8824-93c6b2ad7bc0"
"cto_is_network_type","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""cto_network"", ""cto_network_type""], ""description"": ""Relates a network to its type classification (e.g., Fixed, Satellite, Mobile, Hybrid)."", ""columns"": [{""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""network_type_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""network_name"", ""references_table"": ""cto_network"", ""references_column"": ""network_name""}, {""column"": ""network_type_name"", ""references_table"": ""cto_network_type"", ""references_column"": ""network_type_name""}], ""enforced_foreign_keys"": true, ""label"": ""Is Network Type"", ""in_ontology"": ""core""}","fbb9b433-75dc-4824-bac5-0d24a14016dd"
"cto_is_organization_type","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""foaf_organization"", ""cto_organization_type""], ""description"": ""Relates an organization to its type classification (e.g., ISP, Network Operator, Non-Telco Organization)."", ""columns"": [{""name"": ""organization_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""organization_type_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""organization_name"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}, {""column"": ""organization_type_name"", ""references_table"": ""cto_organization_type"", ""references_column"": ""organization_type_name""}], ""enforced_foreign_keys"": true, ""label"": ""Is Organization Type"", ""in_ontology"": ""core""}","0cd3ead8-0e09-47d4-8839-6c3808d34cbb"
"cto_is_retail_only","{""entity_type"": ""data_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""domain"": ""foaf_organization"", ""range"": ""boolean"", ""description"": ""Specifies whether an ISP is retail-only (does not own any network infrastructure)."", ""columns"": [{""name"": ""isp_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""is_retail_only"", ""data_types"": ""boolean"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""isp_name"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}], ""enforced_foreign_keys"": true, ""label"": ""Is Retail Only"", ""in_ontology"": ""core""}","eb712a3f-aa0e-4f4b-b292-005a73add458"
"cto_is_wholesale_only","{""entity_type"": ""data_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""domain"": ""foaf_organization"", ""range"": ""boolean"", ""description"": ""Specifies whether a network operator is only wholesale (does not sell services directly to end-users)."", ""columns"": [{""name"": ""network_operator_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""is_wholesale_only"", ""data_types"": ""boolean"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""network_operator_name"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}], ""enforced_foreign_keys"": true, ""label"": ""Is Wholesale Only"", ""in_ontology"": ""core""}","961f85e3-34bd-43af-a381-205a0031c18c"
"cto_link","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": [""cto_uses_link"", ""cto_supports_link_standard""], ""description"": ""The physical transmission medium or infrastructure type used to connect a premises or network endpoint to the broadband access network."", ""parent"": null, ""unique_on"": ""link_name"", ""children"": null, ""columns"": [{""name"": ""link_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Links"", ""in_ontology"": ""core""}","0ad8cb1f-8751-4cca-a7b1-b581e8bc93c6"
"cto_link_standard","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": [""cto_supports_link_standard"", ""cto_uses_link_standard""], ""description"": ""The data transmission standard or protocol used over the physical transmission medium/infrastructure (cto_link) to deliver broadband connectivity."", ""parent"": null, ""unique_on"": ""link_standard_name"", ""children"": null, ""columns"": [{""name"": ""link_standard_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Link Standards"", ""in_ontology"": ""core""}","8b879cab-2b54-4ec9-90b6-90944f313fff"
"cto_network","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": [""cto_owns_network"", ""cto_uses_network"", ""cto_uses_link"", ""cto_has_coverage_area""], ""description"": ""Any physical infrastructure network that forms a telecom-related network and occupies physical space in/on the ground."", ""parent"": ""cto_physical_infrastructure"", ""unique_on"": ""network_name"", ""children"": [""cto_link""], ""columns"": [{""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""country"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Networks"", ""in_ontology"": ""core""}","ac95d35c-e226-4e0b-ade2-cb89f206c3f4"
"cto_network_type","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": null, ""description"": ""A classification type for networks based on their technology and service delivery method (e.g., Fixed, Satellite, Mobile, Hybrid)."", ""parent"": null, ""unique_on"": ""network_type_name"", ""children"": null, ""columns"": [{""name"": ""network_type_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Network Types"", ""in_ontology"": ""core""}","ee8170a6-b651-4197-9590-9397afbc2f40"
"cto_offers_broadband_service","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""foaf_organization"", ""cto_broadband_service""], ""description"": ""Relates an ISP to the broadband services it offers to customers."", ""columns"": [{""name"": ""isp_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""broadband_service_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""isp_name"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}, {""column"": ""broadband_service_name"", ""references_table"": ""cto_broadband_service"", ""references_column"": ""broadband_service_name""}], ""enforced_foreign_keys"": false, ""label"": ""Offers Broadband Service"", ""in_ontology"": ""business""}","5079e30d-9038-40bb-b0db-4274a20154e7"
"cto_organization_type","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": null, ""description"": ""A classification type for organizations based on their role in the telecom industry (e.g., ISP, Network Operator, Non-Telco Organization)."", ""parent"": null, ""unique_on"": ""organization_type_name"", ""children"": null, ""columns"": [{""name"": ""organization_type_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Organization Types"", ""in_ontology"": ""core""}","ced721c2-f731-49a1-beb9-30fa84d2736a"
"cto_owns_network","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""foaf_organization"", ""cto_network""], ""description"": ""Relates a telco organization to the network it owns."", ""columns"": [{""name"": ""network_operator_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""network_operator_name"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}, {""column"": ""network_name"", ""references_table"": ""cto_network"", ""references_column"": ""network_name""}], ""enforced_foreign_keys"": true, ""label"": ""Owns Network"", ""in_ontology"": ""core""}","fb3786f5-ad6c-48e2-a2f9-b14399d6281b"
"cto_physical_entities","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": null, ""description"": ""A physical entity. Generally, an entity that occupies space in the physical world. Mutually exclusive with cto_concept_entity."", ""parent"": null, ""unique_on"": ""physical_entity_name"", ""children"": [""cto_physical_infrastructure""], ""columns"": [{""name"": ""physical_entity_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Physical Entities"", ""in_ontology"": ""business""}","97e9f29e-25a5-4785-9bb4-0bfe6f752ddf"
"cto_physical_infrastructure","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": null, ""description"": ""Categories of physical infrastructure, which must occupy physical space in/on the ground."", ""parent"": null, ""unique_on"": ""physical_infrastructure_name"", ""children"": [""cto_network""], ""columns"": [{""name"": ""physical_infrastructure_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Physical Infrastructure"", ""in_ontology"": ""business""}","7e7843b0-bfd7-4558-946d-fe0b53aa6412"
"cto_service","{""entity_type"": ""class"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_properties"": null, ""description"": ""Any service provided by a company to a user. Includes broadband/entertainment/mobile services."", ""parent"": ""cto_concept_entity"", ""unique_on"": ""service_name"", ""children"": [""cto_broadband_service"", ""cto_cellular_service""], ""columns"": [{""name"": ""service_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Services"", ""in_ontology"": ""business""}","1df55235-8d5f-4430-9339-3fd58388b531"
"cto_supports_link_standard","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""cto_link"", ""cto_link_standard""], ""description"": ""Relates a physical transmission medium/infrastructure link to the protocol/standard."", ""columns"": [{""name"": ""link_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""link_standard_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""link_name"", ""references_table"": ""cto_link"", ""references_column"": ""link_name""}, {""column"": ""link_standard_name"", ""references_table"": ""cto_link_standard"", ""references_column"": ""link_standard_name""}], ""enforced_foreign_keys"": true, ""label"": ""Supports Link Standard"", ""in_ontology"": ""core""}","faad0372-5af6-4e9b-b0d4-544a28a10020"
"cto_uses_link","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""cto_network"", ""cto_link""], ""description"": ""Relates a network to the link technology it uses."", ""columns"": [{""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""link_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""network_name"", ""references_table"": ""cto_network"", ""references_column"": ""network_name""}, {""column"": ""link_name"", ""references_table"": ""cto_link"", ""references_column"": ""link_name""}], ""enforced_foreign_keys"": true, ""label"": ""Uses Link"", ""in_ontology"": ""core""}","78e27f76-dc9f-4b92-89f4-978e1cecb9b5"
"cto_uses_link_standard","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""cto_network"", ""cto_link_standard""], ""description"": ""Relates a network to the protocol/standard used by the physical link infrastructure."", ""columns"": [{""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""link_standard_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""network_name"", ""references_table"": ""cto_network"", ""references_column"": ""network_name""}, {""column"": ""link_standard_name"", ""references_table"": ""cto_link_standard"", ""references_column"": ""link_standard_name""}], ""enforced_foreign_keys"": true, ""label"": ""Uses Link Standard"", ""in_ontology"": ""core""}","2c520ffa-f57a-4108-9c3a-1f7b4d8b2b5b"
"cto_uses_network","{""entity_type"": ""object_property"", ""is_defined_by"": ""Common Telecoms Ontology (Point Topic)"", ""related_classes"": [""foaf_organization"", ""cto_network""], ""description"": ""Relates an ISP to the network it uses to provide services."", ""columns"": [{""name"": ""isp_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""network_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""isp_name"", ""references_table"": ""foaf_organization"", ""references_column"": ""organization_name""}, {""column"": ""network_name"", ""references_table"": ""cto_network"", ""references_column"": ""network_name""}], ""enforced_foreign_keys"": true, ""label"": ""Uses Network"", ""in_ontology"": ""core""}","4c7d6fb5-2325-4690-8491-f97518d31b60"
"dcat_catalogue","{""entity_type"": ""class"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_properties"": null, ""description"": ""A catalogue or repository that hosts the Datasets or Data Services being described."", ""parent"": null, ""unique_on"": ""id"", ""children"": [null], ""columns"": [{""name"": ""title"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""description"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""publisher"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""creator"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""service"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""geographical_coverage"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""temporal_coverage"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""themes"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""release_date"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""modification_date"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""language"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""rights"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Catalogues"", ""in_ontology"": ""documents""}","968dc68b-a5ee-4213-b495-c59e8a642407"
"dcat_data_service","{""entity_type"": ""class"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_properties"": null, ""description"": ""A collection of operations that provides access to one or more datasets or data processing functions."", ""parent"": ""dcat_catalogued_resource"", ""unique_on"": ""title"", ""children"": null, ""columns"": [{""name"": ""title"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""description"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""publisher"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""theme"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""format"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""access_rights"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""licence"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""landing_page"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""serves_dataset"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Data Services"", ""in_ontology"": ""documents""}","d93e0036-701c-4d4c-9610-1b94697a4175"
"dcat_dataset","{""entity_type"": ""class"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_properties"": null, ""description"": ""A conceptual entity that represents the information published. (doesn't have to be a dataset, can also be an article, webpage)."", ""parent"": ""dcat_catalogued_resource"", ""unique_on"": ""dataset_name"", ""children"": null, ""columns"": [{""name"": ""dataset_name"", ""data_types"": ""name"", ""nullable"": false}, {""name"": ""title"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""description"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""publisher"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""release_date"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""version"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""type"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""theme"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""keyword"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""language"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""geographical_coverage"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""temporal_coverage"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""spatial_resolution"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""temporal_resolution"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""in_series"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""documentation"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""source"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""related_resource"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""was_generated_by"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""related_entities_raw"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""related_entities_cto"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Datasets"", ""in_ontology"": ""documents""}","7b33c5ae-9f84-4348-8282-702530f3590a"
"dcat_dataset_series","{""entity_type"": ""class"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_properties"": null, ""description"": ""A collection of datasets that are published separately, but share some characteristics that group them."", ""parent"": ""dcat_catalogued_resource"", ""unique_on"": ""title"", ""children"": null, ""columns"": [{""name"": ""title"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""description"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""publisher"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Dataset Series"", ""in_ontology"": ""documents""}","03b72773-b677-4ed5-93ed-7efcea0fc25a"
"dcat_geographical_coverage","{""entity_type"": ""object_property"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_classes"": [""dcat_dataset"", ""dcterms_location""], ""description"": ""A geographical area covered by the Catalogue. (note: may be merged with cto_has_coverage_area in the future)"", ""columns"": [{""name"": ""object_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""location_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Geographical Coverage"", ""in_ontology"": ""documents""}","d3f7a20b-8de5-4db2-93b8-bfbd1b1b5f50"
"dcat_has_record","{""entity_type"": ""object_property"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_classes"": [""dcat_catalogue"", ""dcat_dataset""], ""description"": ""A Catalogue Record that is part of the Catalogue."", ""columns"": [{""name"": ""catalgue_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""dataset_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Has Record"", ""in_ontology"": ""documents""}","f12472db-4eef-4853-819e-6b8865d7d984"
"dcat_in_series","{""entity_type"": ""object_property"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_classes"": [""dcat_dataset"", ""dcat_dataset_series""], ""description"": ""A dataset series of which the dataset is part."", ""columns"": [{""name"": ""dataset_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""dataset_series_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""In Series"", ""in_ontology"": ""documents""}","a133195e-e360-4438-9d15-2c777ccb635c"
"dcat_is_publisher","{""entity_type"": ""object_property"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_classes"": [""foaf_organization"", ""dcat_catalogue"", ""dcat_dataset"", ""dcat_data_service"", ""dcat_dataset_series""], ""description"": ""An entity (organisation) responsible for making something available."", ""columns"": [{""name"": ""organization_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""object_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Is Publisher"", ""in_ontology"": ""documents""}","f8157805-ff7f-416b-96f7-dd148254dcc9"
"dcat_serves_dataset","{""entity_type"": ""object_property"", ""is_defined_by"": ""DCAT (European Commission)"", ""related_classes"": [""dcat_data_service"", ""dcat_dataset""], ""description"": ""This property refers to a collection of data that this data service can distribute."", ""columns"": [{""name"": ""data_service_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""dataset_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Serves Dataset"", ""in_ontology"": ""documents""}","6bcdbcb5-d97f-4729-b550-8a17e40aceb9"
"dcterms_location","{""entity_type"": ""class"", ""is_defined_by"": ""Dublin Core Metadata Initiative"", ""related_properties"": [""cto_has_coverage_area"", ""cto_has_build_location""], ""description"": ""A spatial region or named place. Any spatial thing considered to be a location, e.g. country, street, postcode, NUTS3 ID."", ""parent"": ""wgs84_spatial_thing"", ""unique_on"": ""id"", ""children"": [""cto_postcode"", ""cto_address""], ""columns"": [{""name"": ""location_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""geo"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""foreign_keys"": [{""column"": ""location_name"", ""references_table"": ""wgs84_spatial_thing"", ""references_column"": ""spatial_thing_name""}], ""enforced_foreign_keys"": false, ""label"": ""Locations"", ""in_ontology"": ""business""}","b2a452af-b8f2-44fb-813a-b40ee0fbf8a7"
"foaf_is_topic","{""entity_type"": ""object_property"", ""is_defined_by"": ""FOAF"", ""related_classes"": [""foaf_organization"", ""dcat_catalogue"", ""dcat_dataset""], ""description"": ""A topic of some page or document."", ""columns"": [{""name"": ""organization_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""object_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Is Topic"", ""in_ontology"": ""documents""}","1934f6f9-f66d-43ed-a91b-55e5c761d7dc"
"foaf_organization","{""entity_type"": ""class"", ""is_defined_by"": ""Friend of a Friend Ontology"", ""related_properties"": null, ""description"": ""Any kind of organization. The Organization class represents a kind of Agent corresponding to social instititutions such as companies, societies etc."", ""parent"": null, ""unique_on"": ""organization_name"", ""children"": null, ""columns"": [{""name"": ""organization_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""country"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Organizations"", ""in_ontology"": ""core""}","8cecfa9f-843b-4135-91b9-5ab6391bfaea"
"wgs84_spatial_thing","{""entity_type"": ""class"", ""is_defined_by"": ""WGS84 Geo Positioning Ontology"", ""related_properties"": null, ""description"": ""Anything with spatial extent, i.e. size, shape, or position. e.g. people, places, bowling balls, as well as abstract areas like cubes."", ""parent"": null, ""unique_on"": ""spatial_thing_name"", ""children"": [""dcterms_location""], ""columns"": [{""name"": ""spatial_thing_name"", ""data_types"": ""string"", ""nullable"": false}, {""name"": ""geo"", ""data_types"": ""string"", ""nullable"": true}, {""name"": ""valid_from"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""valid_to"", ""data_types"": ""date"", ""nullable"": true}, {""name"": ""comment"", ""data_types"": ""string"", ""nullable"": true}], ""label"": ""Spatial Things"", ""in_ontology"": ""business""}","69d62b2a-78ea-4c38-9d61-eac329777a4b"
'''
