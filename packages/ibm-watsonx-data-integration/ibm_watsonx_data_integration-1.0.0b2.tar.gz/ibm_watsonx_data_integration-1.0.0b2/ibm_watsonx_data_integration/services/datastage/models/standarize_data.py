STANDARDIZE_DATA = {
    "AUADDR": [
        {
            "name": "LotType_AUADDR",
            "description": "Standardized lot descriptor, typically 'LOT'",
            "max_length": 4,
        },
        {
            "name": "LotNumber_AUADDR",
            "description": "Value affiliated with the LotType column",
            "max_length": 10,
        },
        {
            "name": "HouseNumber1_AUADDR",
            "description": "First house number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "HouseNumber1Suffix_AUADDR",
            "description": "Suffix of the first house number as determined by the rule set, for example 'A' is the suffix in 123A Main St",
            "max_length": 3,
        },
        {
            "name": "HouseNumber2_AUADDR",
            "description": "Second house number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "HouseNumber2Suffix_AUADDR",
            "description": "Suffix of the second house number as determined by the rule set, for example 'A' is the suffix in 123A Main St",
            "max_length": 3,
        },
        {
            "name": "StreetName_AUADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "StreetType_AUADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 5,
        },
        {
            "name": "StreetSuffix_AUADDR",
            "description": "Suffix of the street that appears after the street type, for example North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "PostalDelType_AUADDR",
            "description": "Standardized Postal Delivery descriptor",
            "max_length": 12,
        },
        {
            "name": "PostalDelNumber_AUADDR",
            "description": "The value affiliated with the PostalDelType column",
            "max_length": 10,
        },
        {
            "name": "PostalDelNumberSuffix_AUADDR",
            "description": "Suffix of the postal delivery number as determined by the rule set",
            "max_length": 3,
        },
        {
            "name": "FloorType_AUADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 3,
        },
        {
            "name": "FloorNumber_AUADDR",
            "description": "Value affiliated with the FloorType column",
            "max_length": 10,
        },
        {
            "name": "UnitType_AUADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 5,
        },
        {
            "name": "UnitNumber_AUADDR",
            "description": "Value that is affiliated with the UnitType column",
            "max_length": 10,
        },
        {
            "name": "MultiUnitType_AUADDR",
            "description": "Additional unit descriptor such as Apt, Unit, or Suite populated only if multiple units are found",
            "max_length": 5,
        },
        {
            "name": "MultiUnitNumber_AUADDR",
            "description": "Value affiliated with the MultiUnitType column",
            "max_length": 10,
        },
        {
            "name": "BuildingName1_AUADDR",
            "description": "Name of the first building as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "BuildingName2_AUADDR",
            "description": "Name of the second building as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "AdditionalAddress_AUADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "AddressType_AUADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "StreetNameNYSIIS_AUADDR",
            "description": "Phonetic sound of the StreetName column",
            "max_length": 8,
        },
        {
            "name": "StreetNameRVSNDX_AUADDR",
            "description": "Numerical representation of the reverse phonetic sound of the StreetName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_AUADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_AUADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_AUADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_AUADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_AUADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "AUAREA": [
        {
            "name": "LocalityName_AUAREA",
            "description": "Name of the locality as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "StateAbbreviation_AUAREA",
            "description": "State abbreviation as determined by the rule set",
            "max_length": 4,
        },
        {
            "name": "PostCode_AUAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 4,
        },
        {
            "name": "CountryCode_AUAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 3,
        },
        {
            "name": "LocalityNameNYSIIS_AUAREA",
            "description": "Phonetic sound of the LocalityName column",
            "max_length": 8,
        },
        {
            "name": "LocalityNameRVSNDX_AUAREA",
            "description": "Numerical representation of the reverse phonetic sound of the LocalityName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_AUAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_AUAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_AUAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_AUAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_AUAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "AUNAME": [
        {
            "name": "NameType_AUNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_AUNAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_AUNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_AUNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_AUNAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_AUNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_AUNAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_AUNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_AUNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_AUNAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_AUNAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_AUNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_AUNAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_AUNAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_AUNAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_AUNAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_AUNAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_AUNAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_AUNAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_AUNAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_AUNAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_AUNAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_AUNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_AUNAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_AUNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_AUNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_AUNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_AUNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_AUNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_AUNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "AUPREP": [
        {
            "name": "NameDomain_AUPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_AUPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_AUPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_AUPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_AUPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_AUPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_AUPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_AUPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_AUPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_AUPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_AUPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_AUPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_AUPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "CNADDR": [
        {
            "name": "ISOCountryCode_CNADDR",
            "description": "ISO\u56fd\u5bb6\u4ee3\u7801",
            "max_length": 2,
        },
        {
            "name": "ProvinceName_CNADDR",
            "description": "\u7701\u540d\u79f0",
            "max_length": 3,
        },
        {
            "name": "ProvinceType_CNADDR",
            "description": "\u7701\u7c7b\u578b",
            "max_length": 7,
        },
        {
            "name": "CityName_CNADDR",
            "description": "\u5e02\u540d\u79f0",
            "max_length": 4,
        },
        {
            "name": "CityType_CNADDR",
            "description": "\u5e02\u7c7b\u578b",
            "max_length": 8,
        },
        {
            "name": "CountyName_CNADDR",
            "description": "\u53bf\u540d\u79f0",
            "max_length": 6,
        },
        {
            "name": "CountyType_CNADDR",
            "description": "\u53bf\u7c7b\u578b",
            "max_length": 8,
        },
        {
            "name": "DistrictName_CNADDR",
            "description": "\u533a\u540d\u79f0",
            "max_length": 4,
        },
        {
            "name": "DistrictType_CNADDR",
            "description": "\u533a\u7c7b\u578b",
            "max_length": 5,
        },
        {
            "name": "TownName_CNADDR",
            "description": "\u4e61\u9547\u540d\u79f0",
            "max_length": 5,
        },
        {
            "name": "TownType_CNADDR",
            "description": "\u4e61\u9547\u7c7b\u578b",
            "max_length": 5,
        },
        {
            "name": "IndustrialPark_CNADDR",
            "description": "\u5de5\u4e1a\u533a\u540d\u79f0",
            "max_length": 6,
        },
        {
            "name": "IndustrialParkType_CNADDR",
            "description": "\u5de5\u4e1a\u533a\u7c7b\u578b",
            "max_length": 6,
        },
        {
            "name": "VillageCommunityName_CNADDR",
            "description": "\u6751\u6216\u793e\u533a\u540d\u79f0",
            "max_length": 6,
        },
        {
            "name": "VillageCommunityType_CNADDR",
            "description": "\u6751\u6216\u793e\u533a\u7c7b\u578b",
            "max_length": 4,
        },
        {
            "name": "VillageGroupName_CNADDR",
            "description": "\u6751\u7ec4\u540d\u79f0",
            "max_length": 6,
        },
        {
            "name": "VillageGroupType_CNADDR",
            "description": "\u6751\u7ec4\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "PostBox_CNADDR",
            "description": "\u4fe1\u7bb1",
            "max_length": 5,
        },
        {
            "name": "PostBoxBranch_CNADDR",
            "description": "\u5206\u4fe1\u7bb1",
            "max_length": 5,
        },
        {
            "name": "StreetName_CNADDR",
            "description": "\u9053\u8def\u540d\u79f0",
            "max_length": 20,
        },
        {
            "name": "StreetDirection_CNADDR",
            "description": "\u9053\u8def\u65b9\u5411",
            "max_length": 2,
        },
        {
            "name": "StreetType_CNADDR",
            "description": "\u9053\u8def\u7c7b\u578b",
            "max_length": 4,
        },
        {
            "name": "StreetBranchLevel1_CNADDR",
            "description": "\u8def\u6bb5\u540d\u79f0",
            "max_length": 6,
        },
        {
            "name": "TypeOfLevel1_CNADDR",
            "description": "\u8def\u6bb5\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "StreetBranchLevel2_CNADDR",
            "description": "\u8857\u5df7\u540d\u79f0",
            "max_length": 8,
        },
        {
            "name": "TypeOfLevel2_CNADDR",
            "description": "\u8857\u5df7\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "StreetBranchLevel3_CNADDR",
            "description": "\u91cc\u5f04\u540d\u79f0",
            "max_length": 4,
        },
        {
            "name": "TypeOfLevel3_CNADDR",
            "description": "\u91cc\u5f04\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "StreetBranchLevel4_CNADDR",
            "description": "\u652f\u5f04\u540d\u79f0",
            "max_length": 4,
        },
        {
            "name": "TypeOfLevel4_CNADDR",
            "description": "\u652f\u5f04\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "StreetNumberValue_CNADDR",
            "description": "\u8857\u9053\u53f7",
            "max_length": 10,
        },
        {
            "name": "TypeOfNumber_CNADDR",
            "description": "\u53f7\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "BuildingOrganizationName_CNADDR",
            "description": "\u5efa\u7b51\u53ca\u7ec4\u7ec7\u540d\u79f0",
            "max_length": 30,
        },
        {
            "name": "GradeClassInformation_CNADDR",
            "description": "\u5e74\u7ea7\u73ed\u7ea7\u4fe1\u606f",
            "max_length": 10,
        },
        {
            "name": "BlockValue_CNADDR",
            "description": "\u697c\u680b",
            "max_length": 4,
        },
        {
            "name": "BlockType_CNADDR",
            "description": "\u697c\u680b\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "UnitValue_CNADDR",
            "description": "\u5355\u5143\u6570\u503c",
            "max_length": 4,
        },
        {
            "name": "UnitType_CNADDR",
            "description": "\u5355\u5143\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "FloorValue_CNADDR",
            "description": "\u697c\u5c42",
            "max_length": 4,
        },
        {
            "name": "FloorType_CNADDR",
            "description": "\u697c\u5c42\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "RoomValue_CNADDR",
            "description": "\u623f\u95f4\u53f7\u7801",
            "max_length": 8,
        },
        {
            "name": "RoomType_CNADDR",
            "description": "\u623f\u95f4\u7c7b\u578b",
            "max_length": 4,
        },
        {
            "name": "AdditionalAddress_CNADDR",
            "description": "\u5176\u5b83\u4fe1\u606f",
            "max_length": 20,
        },
        {
            "name": "ExplanationData_CNADDR",
            "description": "\u6ce8\u91ca\u4fe1\u606f",
            "max_length": 20,
        },
        {
            "name": "UnhandledPattern_CNADDR",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CNADDR",
            "description": "UnhandledData",
            "max_length": 50,
        },
        {
            "name": "InputPattern_CNADDR",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CNADDR",
            "description": "ExceptionData",
            "max_length": 10,
        },
        {
            "name": "UserOverrideFlag_CNADDR",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
        {
            "name": "ExceptionFlag_CNADDR",
            "description": "\u6807\u5fd7\u57df",
            "max_length": 2,
        },
        {"name": "Area_CNADDR", "description": "Area\u57df", "max_length": 30},
    ],
    "CNAREA": [
        {
            "name": "ISOCountryCode_CNAREA",
            "description": "ISO\u56fd\u5bb6\u4ee3\u7801",
            "max_length": 2,
        },
        {
            "name": "ZipCode_CNAREA",
            "description": "\u90ae\u7f16",
            "max_length": 6,
        },
        {
            "name": "ProvinceName_CNAREA",
            "description": "\u7701\u540d\u79f0",
            "max_length": 3,
        },
        {
            "name": "ProvinceType_CNAREA",
            "description": "\u7701\u7c7b\u578b",
            "max_length": 5,
        },
        {
            "name": "CityName_CNAREA",
            "description": "\u5e02\u540d\u79f0",
            "max_length": 8,
        },
        {
            "name": "CityType_CNAREA",
            "description": "\u5e02\u7c7b\u578b",
            "max_length": 3,
        },
        {
            "name": "CountyName_CNAREA",
            "description": "\u53bf\u540d\u79f0",
            "max_length": 8,
        },
        {
            "name": "CountyType_CNAREA",
            "description": "\u53bf\u7c7b\u578b",
            "max_length": 3,
        },
        {
            "name": "DistrictName_CNAREA",
            "description": "\u533a\u540d\u79f0",
            "max_length": 8,
        },
        {
            "name": "DistrictType_CNAREA",
            "description": "\u533a\u7c7b\u578b",
            "max_length": 3,
        },
        {
            "name": "ProvinceCityMismatch_CNAREA",
            "description": "\u7701\u5e02\u53bf\u533a\u4e0d\u5339\u914d",
            "max_length": 15,
        },
        {
            "name": "CityTypeMismatch_CNAREA",
            "description": "\u5e02\u7c7b\u578b\u4e0d\u5339\u914d",
            "max_length": 15,
        },
        {
            "name": "ProvinceTypeMismatch_CNAREA",
            "description": "\u7701\u7c7b\u578b\u4e0d\u5339\u914d",
            "max_length": 15,
        },
        {
            "name": "UnhandledPattern_CNAREA",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CNAREA",
            "description": "UnhandledData",
            "max_length": 50,
        },
        {
            "name": "InputPattern_CNAREA",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CNAREA",
            "description": "ExceptionData",
            "max_length": 10,
        },
        {
            "name": "UserOverrideFlag_CNAREA",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "CNNAME": [
        {
            "name": "OrganizationName_CNNAME",
            "description": "\u7ec4\u7ec7",
            "max_length": 40,
        },
        {
            "name": "IndividualName_CNNAME",
            "description": "\u4e2a\u4eba",
            "max_length": 8,
        },
        {
            "name": "SurnameGroup_CNNAME",
            "description": "\u59d3\u6c0f",
            "max_length": 4,
        },
        {
            "name": "GivenName_CNNAME",
            "description": "\u540d\u5b57",
            "max_length": 4,
        },
        {
            "name": "ExplanationData_CNNAME",
            "description": "\u6ce8\u91ca\u4fe1\u606f",
            "max_length": 10,
        },
        {
            "name": "PrimaryON_CNNAME",
            "description": "\u4e3b\u540d",
            "max_length": 20,
        },
        {
            "name": "BranchON_CNNAME",
            "description": "\u5206\u652f",
            "max_length": 20,
        },
        {
            "name": "INON_CNNAME",
            "description": "\u8fde\u7ed3\u4fe1\u606f",
            "max_length": 50,
        },
        {
            "name": "NameSuffix_CNNAME",
            "description": "\u540e\u7f00",
            "max_length": 10,
        },
        {
            "name": "PossiblePrimaryName_CNNAME",
            "description": "\u53ef\u80fd\u7684\u4e3b\u540d",
            "max_length": 30,
        },
        {
            "name": "PossibleAdditionalName_CNNAME",
            "description": "\u53ef\u80fd\u7684\u5206\u652f\u540d",
            "max_length": 30,
        },
        {
            "name": "NameType_CNNAME",
            "description": "\u7c7b\u578b",
            "max_length": 6,
        },
        {
            "name": "UnhandledPattern_CNNAME",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CNNAME",
            "description": "UnhandledData",
            "max_length": 50,
        },
        {
            "name": "InputPattern_CNNAME",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CNNAME",
            "description": "ExceptionData",
            "max_length": 10,
        },
        {
            "name": "UserOverrideFlag_CNNAME",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "CNPHONE": [
        {
            "name": "CountryCode_CNPHONE",
            "description": "Country_Code",
            "max_length": 6,
        },
        {
            "name": "DialingCode_CNPHONE",
            "description": "Dialing_Code",
            "max_length": 1,
        },
        {
            "name": "RegionCode_CNPHONE",
            "description": "Region_Code",
            "max_length": 3,
        },
        {
            "name": "LineNumber_CNPHONE",
            "description": "Line_Number",
            "max_length": 9,
        },
        {
            "name": "MobileNumber_CNPHONE",
            "description": "Mobile_Number",
            "max_length": 11,
        },
        {
            "name": "Extension_CNPHONE",
            "description": "Extension",
            "max_length": 8,
        },
        {
            "name": "AreaCode_CNPHONE",
            "description": "Area_Code",
            "max_length": 6,
        },
        {
            "name": "UnhandledPattern_CNPHONE",
            "description": "Unhandled_Pattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CNPHONE",
            "description": "Unhandled_Data",
            "max_length": 40,
        },
        {
            "name": "InputPattern_CNPHONE",
            "description": "Input_Pattern",
            "max_length": 20,
        },
        {
            "name": "ExceptionData_CNPHONE",
            "description": "Exception_Data",
            "max_length": 40,
        },
        {
            "name": "UserOverrideFlag_CNPHONE",
            "description": "User_Override_Flag",
            "max_length": 2,
        },
        {
            "name": "ValidFlag_CNPHONE",
            "description": "Valid_Flag",
            "max_length": 2,
        },
        {
            "name": "InvalidData_CNPHONE",
            "description": "Invalid_Data",
            "max_length": 20,
        },
        {
            "name": "InvalidReason_CNPHONE",
            "description": "Invalid_Reason",
            "max_length": 2,
        },
    ],
    "HKADDR": [
        {
            "name": "ISOCountryCode_HKADDR",
            "description": "ISO",
            "max_length": 2,
        },
        {
            "name": "CityName_HKADDR",
            "description": "CityName",
            "max_length": 10,
        },
        {"name": "Area_HKADDR", "description": "Area", "max_length": 15},
        {
            "name": "District_HKADDR",
            "description": "District",
            "max_length": 25,
        },
        {
            "name": "SubDistrict_HKADDR",
            "description": "SubDistrict",
            "max_length": 20,
        },
        {
            "name": "RoomValue_HKADDR",
            "description": "RoomValue",
            "max_length": 11,
        },
        {
            "name": "RoomType_HKADDR",
            "description": "RoomType",
            "max_length": 10,
        },
        {
            "name": "UnitName_HKADDR",
            "description": "UnitName",
            "max_length": 30,
        },
        {
            "name": "UnitNumber_HKADDR",
            "description": "UnitNumber",
            "max_length": 20,
        },
        {
            "name": "UnitType_HKADDR",
            "description": "UnitType",
            "max_length": 20,
        },
        {
            "name": "FloorValue_HKADDR",
            "description": "FloorValue",
            "max_length": 24,
        },
        {
            "name": "FloorType_HKADDR",
            "description": "FloorType",
            "max_length": 5,
        },
        {
            "name": "BlockValue_HKADDR",
            "description": "BlockValue",
            "max_length": 8,
        },
        {
            "name": "BlockType_HKADDR",
            "description": "BlockType",
            "max_length": 10,
        },
        {
            "name": "TowerValue_HKADDR",
            "description": "TowerValue",
            "max_length": 8,
        },
        {
            "name": "TowerType_HKADDR",
            "description": "TowerType",
            "max_length": 10,
        },
        {
            "name": "BuildingPhaseValue_HKADDR",
            "description": "BuildingPhaseValue",
            "max_length": 7,
        },
        {
            "name": "BuildingPhaseType_HKADDR",
            "description": "BuildingPhaseType",
            "max_length": 5,
        },
        {"name": "AreaVaue_HKADDR", "description": "AreaVaue", "max_length": 5},
        {
            "name": "AreaDescriptor_HKADDR",
            "description": "AreaDescriptor",
            "max_length": 5,
        },
        {
            "name": "EstateValue_HKADDR",
            "description": "EstateValue",
            "max_length": 8,
        },
        {
            "name": "EstateQualifier_HKADDR",
            "description": "EstateQualifier",
            "max_length": 20,
        },
        {
            "name": "EstateSuffix_HKADDR",
            "description": "EstateSuffix",
            "max_length": 7,
        },
        {
            "name": "EstateName_HKADDR",
            "description": "EstateName",
            "max_length": 40,
        },
        {
            "name": "EstateType_HKADDR",
            "description": "EstateType",
            "max_length": 20,
        },
        {
            "name": "ComplexBuildingsName_HKADDR",
            "description": "ComplexBuildingsName",
            "max_length": 40,
        },
        {
            "name": "ComplexBuildingsType_HKADDR",
            "description": "ComplexBuildingsType",
            "max_length": 10,
        },
        {
            "name": "Building_Number_HKADDR",
            "description": "Building_Number",
            "max_length": 10,
        },
        {
            "name": "SingleBuildingName_HKADDR",
            "description": "SingleBuildingName",
            "max_length": 40,
        },
        {
            "name": "SingleBuildingDescriptor_HKADDR",
            "description": "SingleBuildingDescriptor",
            "max_length": 35,
        },
        {
            "name": "BuildingSuffix_HKADDR",
            "description": "BuildingSuffix",
            "max_length": 7,
        },
        {
            "name": "DependentThoroughfareQualifier_HKADDR",
            "description": "DependentThoroughfareQualifier",
            "max_length": 20,
        },
        {
            "name": "DependentThoroughfareValue_HKADDR",
            "description": "DependentThoroughfareValue",
            "max_length": 8,
        },
        {
            "name": "DependentThoroughfareName_HKADDR",
            "description": "DependentThoroughfareName",
            "max_length": 40,
        },
        {
            "name": "DependentThoroughfareDescriptor_HKADDR",
            "description": "DependentThoroughfareDescriptor",
            "max_length": 20,
        },
        {
            "name": "DependentThoroughfareSuffix_HKADDR",
            "description": "DependentThoroughfareSuffix",
            "max_length": 7,
        },
        {
            "name": "ThoroughfareNameSEC_HKADDR",
            "description": "ThoroughfareName&SEC",
            "max_length": 40,
        },
        {
            "name": "ThoroughfareDescriptorSEC_HKADDR",
            "description": "ThoroughfareDescriptor&SEC",
            "max_length": 20,
        },
        {
            "name": "POBoxDescriptor_HKADDR",
            "description": "POBoxDescriptor",
            "max_length": 6,
        },
        {
            "name": "POBoxValue_HKADDR",
            "description": "POBoxValue",
            "max_length": 6,
        },
        {
            "name": "POBoxName_HKADDR",
            "description": "POBoxName",
            "max_length": 16,
        },
        {
            "name": "OrgnizationName_HKADDR",
            "description": "OrgnizationName",
            "max_length": 70,
        },
        {
            "name": "LotAndLane_HKADDR",
            "description": "LOT&LANE",
            "max_length": 13,
        },
        {
            "name": "LotAndLaneType_HKADDR",
            "description": "LOT&LANE_TYPE",
            "max_length": 10,
        },
        {"name": "DD_HKADDR", "description": "DD", "max_length": 13},
        {"name": "DDType_HKADDR", "description": "DD_TYPE", "max_length": 10},
        {
            "name": "AddressType_HKADDR",
            "description": "AddressType",
            "max_length": 1,
        },
        {
            "name": "UnhandledPattern_HKADDR",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_HKADDR",
            "description": "UnhandledData",
            "max_length": 50,
        },
        {
            "name": "InputPattern_HKADDR",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_HKADDR",
            "description": "ExceptionData",
            "max_length": 30,
        },
        {
            "name": "ExplanationData_HKADDR",
            "description": "ExplanationData",
            "max_length": 20,
        },
        {
            "name": "UserOverrideFlag_HKADDR",
            "description": "UserOverrideFlag",
            "max_length": 6,
        },
    ],
    "HKCADDR": [
        {
            "name": "ISOCountryCode_HKCADDR",
            "description": "ISO\u56fd\u5bb6\u4ee3\u7801",
            "max_length": 2,
        },
        {"name": "CityName_HKCADDR", "description": "\u5e02", "max_length": 2},
        {
            "name": "Area_HKCADDR",
            "description": "\u533a\u57df1",
            "max_length": 4,
        },
        {
            "name": "District_HKCADDR",
            "description": "\u533a\u57df2",
            "max_length": 4,
        },
        {
            "name": "SubDistrict_HKCADDR",
            "description": "\u533a\u57df3",
            "max_length": 8,
        },
        {
            "name": "VillageEstateName_HKCADDR",
            "description": "\u6751\u6216\u793e\u533a\u540d\u79f0",
            "max_length": 12,
        },
        {
            "name": "VillageEstateType_HKCADDR",
            "description": "\u6751\u6216\u793e\u533a\u7c7b\u578b",
            "max_length": 4,
        },
        {
            "name": "Streetname_HKCADDR",
            "description": "\u9053\u8def\u540d\u79f0",
            "max_length": 10,
        },
        {
            "name": "StreetType_HKCADDR",
            "description": "\u9053\u8def\u7c7b\u578b",
            "max_length": 4,
        },
        {
            "name": "StreetDirection_HKCADDR",
            "description": "\u9053\u8def\u65b9\u5411",
            "max_length": 2,
        },
        {
            "name": "StreetBranchLevel1_HKCADDR",
            "description": "\u8def\u6bb5\u540d\u79f0",
            "max_length": 10,
        },
        {
            "name": "TypeofLevel1_HKCADDR",
            "description": "\u8def\u6bb5\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "StreetBranchLevel2_HKCADDR",
            "description": "\u8def\u6bb5\u540d\u79f0",
            "max_length": 12,
        },
        {
            "name": "TypeofLevel2_HKCADDR",
            "description": "\u8def\u6bb5\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "StreetNumbervaule_HKCADDR",
            "description": "\u8857\u9053\u53f7",
            "max_length": 10,
        },
        {
            "name": "TypeofNumber_HKCADDR",
            "description": "\u53f7\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "Building_HKCADDR",
            "description": "\u5efa\u7b51\u540d\u79f0",
            "max_length": 25,
        },
        {
            "name": "OrganizationName_HKCADDR",
            "description": "\u7ec4\u7ec7\u540d\u79f0",
            "max_length": 25,
        },
        {
            "name": "GradeClassinformation_HKCADDR",
            "description": "\u5e74\u7ea7\u73ed\u7ea7\u4fe1\u606f",
            "max_length": 20,
        },
        {
            "name": "BlockValue_HKCADDR",
            "description": "\u697c\u680b",
            "max_length": 8,
        },
        {
            "name": "BlockType_HKCADDR",
            "description": "\u697c\u680b\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "UnitValue_HKCADDR",
            "description": "\u5355\u5143\u6570\u503c",
            "max_length": 10,
        },
        {
            "name": "UnitType_HKCADDR",
            "description": "\u5355\u5143\u7c7b\u578b",
            "max_length": 4,
        },
        {
            "name": "FloorValue_HKCADDR",
            "description": "\u697c\u5c42",
            "max_length": 6,
        },
        {
            "name": "FloorType_HKCADDR",
            "description": "\u697c\u5c42\u7c7b\u578b",
            "max_length": 2,
        },
        {
            "name": "RoomValue_HKCADDR",
            "description": "\u623f\u95f4\u53f7\u7801",
            "max_length": 10,
        },
        {
            "name": "RoomType_HKCADDR",
            "description": "\u623f\u95f4\u7c7b\u578b",
            "max_length": 4,
        },
        {
            "name": "PostBox_HKCADDR",
            "description": "\u4fe1\u7bb1",
            "max_length": 5,
        },
        {
            "name": "PostBoxType_HKCADDR",
            "description": "\u4fe1\u7bb1\u7c7b\u578b",
            "max_length": 8,
        },
        {
            "name": "AdditionalAddress_HKCADDR",
            "description": "\u5176\u5b83\u4fe1\u606f",
            "max_length": 20,
        },
        {
            "name": "ExplanationData_HKCADDR",
            "description": "\u6ce8\u91ca\u4fe1\u606f",
            "max_length": 20,
        },
        {
            "name": "UnhandledPattern_HKCADDR",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_HKCADDR",
            "description": "UnhandledData",
            "max_length": 50,
        },
        {
            "name": "InputPattern_HKCADDR",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_HKCADDR",
            "description": "ExceptionData",
            "max_length": 10,
        },
        {
            "name": "UserOverrideFlag_HKCADDR",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
        {
            "name": "Flagforconfusedinformation_HKCADDR",
            "description": "\u6807\u5fd7\u57df",
            "max_length": 2,
        },
    ],
    "HKCNAME": [
        {
            "name": "OrganizationName_HKCNAME",
            "description": "\u7d44\u7e54",
            "max_length": 40,
        },
        {
            "name": "IndividualName_HKCNAME",
            "description": "\u500b\u4eba",
            "max_length": 8,
        },
        {
            "name": "SurnameGroup_HKCNAME",
            "description": "\u59d3\u6c0f",
            "max_length": 4,
        },
        {
            "name": "OriginalSurnameGroup_HKCNAME",
            "description": "\u539f\u59d3\u6c0f",
            "max_length": 4,
        },
        {
            "name": "GivenName_HKCNAME",
            "description": "\u540d\u5b57",
            "max_length": 4,
        },
        {
            "name": "EnglishName_HKCNAME",
            "description": "\u82f1\u6587\u540d\u5b57",
            "max_length": 4,
        },
        {
            "name": "ExplanationData_HKCNAME",
            "description": "\u8a3b\u91cb\u4fe1\u606f",
            "max_length": 10,
        },
        {
            "name": "OrganizationValue_HKCNAME",
            "description": "\u7d44\u7e54\u540d",
            "max_length": 40,
        },
        {
            "name": "OrganizationType_HKCNAME",
            "description": "\u7d44\u7e54\u985e\u578b",
            "max_length": 10,
        },
        {
            "name": "PrimaryON_HKCNAME",
            "description": "\u4e3b\u540d",
            "max_length": 20,
        },
        {
            "name": "BranchON_HKCNAME",
            "description": "\u5206\u652f",
            "max_length": 20,
        },
        {
            "name": "INON_HKCNAME",
            "description": "\u9023\u7d50\u4fe1\u606f",
            "max_length": 50,
        },
        {
            "name": "NameSuffix_HKCNAME",
            "description": "\u5f8c\u7db4",
            "max_length": 10,
        },
        {
            "name": "NameType_HKCNAME",
            "description": "\u985e\u578b",
            "max_length": 6,
        },
        {
            "name": "UnhandledPattern_HKCNAME",
            "description": "Unhandled_Pattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_HKCNAME",
            "description": "Unhandled_Data",
            "max_length": 50,
        },
        {
            "name": "InputPattern_HKCNAME",
            "description": "Input_Pattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_HKCNAME",
            "description": "Exception_Data",
            "max_length": 10,
        },
        {
            "name": "UserOverrideFlag_HKCNAME",
            "description": "User_Override_Flag",
            "max_length": 2,
        },
    ],
    "HKNAME": [
        {
            "name": "OrganizationName_HKNAME",
            "description": "OrganizationName",
            "max_length": 70,
        },
        {
            "name": "IndividualName_HKNAME",
            "description": "IndividualName",
            "max_length": 30,
        },
        {
            "name": "OtherName_HKNAME",
            "description": "OtherName",
            "max_length": 30,
        },
        {"name": "Surname_HKNAME", "description": "Surname", "max_length": 10},
        {
            "name": "HSurname_HKNAME",
            "description": "HSurname",
            "max_length": 10,
        },
        {
            "name": "MiddleName_HKNAME",
            "description": "MiddleName",
            "max_length": 20,
        },
        {
            "name": "FirstName_HKNAME",
            "description": "FirstName",
            "max_length": 20,
        },
        {
            "name": "ExplanationData_HKNAME",
            "description": "ExplanationData",
            "max_length": 40,
        },
        {
            "name": "OrganizationValue_HKNAME",
            "description": "OrganizationValue",
            "max_length": 60,
        },
        {
            "name": "OrganizationType_HKNAME",
            "description": "OrganizationType",
            "max_length": 10,
        },
        {
            "name": "PrimaryON_HKNAME",
            "description": "PrimaryON",
            "max_length": 70,
        },
        {
            "name": "BranchON_HKNAME",
            "description": "BranchON",
            "max_length": 20,
        },
        {"name": "INON_HKNAME", "description": "IN_ON", "max_length": 70},
        {
            "name": "NameSuffix_HKNAME",
            "description": "NameSuffix",
            "max_length": 20,
        },
        {"name": "NameType_HKNAME", "description": "NameType", "max_length": 6},
        {
            "name": "UnhandledPattern_HKNAME",
            "description": "Unhandled_Pattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_HKNAME",
            "description": "Unhandled_Data",
            "max_length": 50,
        },
        {
            "name": "InputPattern_HKNAME",
            "description": "Input_Pattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_HKNAME",
            "description": "Exception_Data",
            "max_length": 10,
        },
        {
            "name": "UserOverrideFlag_HKNAME",
            "description": "User_Override_Flag",
            "max_length": 2,
        },
    ],
    "HKPHONE": [
        {
            "name": "ResidualPhone_HKPHONE",
            "description": "Residual_phone",
            "max_length": 15,
        },
        {
            "name": "ExtensionForRes_HKPHONE",
            "description": "Extension_for_Res",
            "max_length": 8,
        },
        {
            "name": "MobileNumber_HKPHONE",
            "description": "Mobile_Number",
            "max_length": 15,
        },
        {
            "name": "OfficePhone_HKPHONE",
            "description": "Office_phone",
            "max_length": 15,
        },
        {
            "name": "ExtensionForOffice_HKPHONE",
            "description": "Extension_for_Office",
            "max_length": 8,
        },
        {
            "name": "PagerPhone_HKPHONE",
            "description": "Pager_phone",
            "max_length": 15,
        },
        {
            "name": "PagerAcc_HKPHONE",
            "description": "Pager_acc",
            "max_length": 8,
        },
        {
            "name": "FaxPhone_HKPHONE",
            "description": "Fax_phone",
            "max_length": 15,
        },
        {
            "name": "ExtensionForMobile_HKPHONE",
            "description": "Extension_for_Mobile",
            "max_length": 8,
        },
        {
            "name": "UnhandledPattern_HKPHONE",
            "description": "Unhandled_Pattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_HKPHONE",
            "description": "Unhandled_Data",
            "max_length": 40,
        },
        {
            "name": "InputPattern_HKPHONE",
            "description": "Input_Pattern",
            "max_length": 20,
        },
        {
            "name": "ExceptionData_HKPHONE",
            "description": "Exception_Data",
            "max_length": 40,
        },
        {
            "name": "UserOverrideFlag_HKPHONE",
            "description": "User_Override_Flag",
            "max_length": 2,
        },
        {
            "name": "ValidFlag_HKPHONE",
            "description": "Valid_Flag",
            "max_length": 4,
        },
        {
            "name": "InValidData_HKPHONE",
            "description": "InValid_Data",
            "max_length": 20,
        },
    ],
    "INAPAD": [
        {
            "name": "DoorNumber_INAPAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INAPAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INAPAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INAPAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INAPAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INAPAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INAPAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INAPAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INAPAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INAPAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INAPAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INAPAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INAPAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INAPAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INAPAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INAPAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INAPAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INAPAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INAPAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INAPAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INAPAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INAPAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INAPAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INAPAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INAPAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INAPAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INAPAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INAPAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INAPAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INAPAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INAPAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INAPAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INAPAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INAPAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INAPAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INAPAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INAPAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INAPAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INAREA": [
        {
            "name": "Taluk_INAREA",
            "description": "Taluk, town or city information from the input data",
            "max_length": 50,
        },
        {
            "name": "District_INAREA",
            "description": "District information from the input data",
            "max_length": 30,
        },
        {
            "name": "State_INAREA",
            "description": "State information from the input data",
            "max_length": 50,
        },
        {
            "name": "PinCode_INAREA",
            "description": "Pin code information from the input data",
            "max_length": 10,
        },
        {
            "name": "Country_INAREA",
            "description": "Country information from the input data",
            "max_length": 30,
        },
        {
            "name": "RouteInformation_INAREA",
            "description": "Route (VIA) information from the input data",
            "max_length": 100,
        },
        {
            "name": "StateIdentifier_INAREA",
            "description": "Two character code that designates the state to which the address belongs",
            "max_length": 2,
        },
        {
            "name": "UnhandledPattern_INAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 250,
        },
        {
            "name": "InputPattern_INAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_INAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "PincodeValidationFlag_INAREA",
            "description": "Indicator of whether the pin code from the input data is valid; values are - N=Pin code not validated, L=Pin code fewer than 6 digits, G=Pin code greater than 6 digits,V=Valid, I=Invalid",
            "max_length": 2,
        },
    ],
    "INASAD": [
        {
            "name": "DoorNumber_INASAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INASAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INASAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INASAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INASAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INASAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INASAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INASAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INASAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INASAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INASAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INASAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INASAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INASAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INASAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INASAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INASAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INASAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INASAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INASAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INASAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INASAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INASAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INASAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INASAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INASAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INASAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INASAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INASAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INASAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INASAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INASAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INASAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INASAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INASAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INASAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INASAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INASAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INBHAD": [
        {
            "name": "DoorNumber_INBHAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INBHAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INBHAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INBHAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INBHAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INBHAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INBHAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INBHAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INBHAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INBHAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INBHAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INBHAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INBHAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INBHAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INBHAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INBHAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INBHAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INBHAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INBHAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INBHAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INBHAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INBHAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INBHAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INBHAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INBHAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INBHAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INBHAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INBHAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INBHAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INBHAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INBHAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INBHAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INBHAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INBHAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INBHAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INBHAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INBHAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INBHAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INDLAD": [
        {
            "name": "DoorNumber_INDLAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INDLAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INDLAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INDLAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INDLAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INDLAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INDLAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INDLAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INDLAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INDLAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INDLAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INDLAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INDLAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INDLAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INDLAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INDLAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INDLAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INDLAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INDLAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INDLAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INDLAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INDLAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INDLAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INDLAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INDLAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INDLAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INDLAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INDLAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INDLAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INDLAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INDLAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INDLAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INDLAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INDLAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INDLAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INDLAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INDLAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INDLAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INGJAD": [
        {
            "name": "DoorNumber_INGJAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INGJAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INGJAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INGJAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INGJAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INGJAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INGJAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INGJAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INGJAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INGJAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INGJAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INGJAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INGJAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INGJAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INGJAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INGJAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INGJAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INGJAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INGJAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INGJAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INGJAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INGJAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INGJAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INGJAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INGJAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INGJAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INGJAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INGJAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INGJAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INGJAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INGJAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INGJAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INGJAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INGJAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INGJAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INGJAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INGJAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INGJAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INHPAD": [
        {
            "name": "DoorNumber_INHPAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INHPAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INHPAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INHPAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INHPAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INHPAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INHPAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INHPAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INHPAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INHPAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INHPAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INHPAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INHPAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INHPAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INHPAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INHPAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INHPAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INHPAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INHPAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INHPAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INHPAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INHPAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INHPAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INHPAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INHPAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INHPAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INHPAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INHPAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INHPAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INHPAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INHPAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INHPAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INHPAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INHPAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INHPAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INHPAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INHPAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INHPAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INHRAD": [
        {
            "name": "DoorNumber_INHRAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INHRAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INHRAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INHRAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INHRAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INHRAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INHRAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INHRAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INHRAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INHRAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INHRAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INHRAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INHRAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INHRAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INHRAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INHRAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INHRAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INHRAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INHRAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INHRAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INHRAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INHRAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INHRAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INHRAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INHRAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INHRAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INHRAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INHRAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INHRAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INHRAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INHRAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INHRAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INHRAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INHRAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INHRAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INHRAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INHRAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INHRAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INJKAD": [
        {
            "name": "DoorNumber_INJKAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INJKAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INJKAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INJKAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INJKAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INJKAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INJKAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INJKAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INJKAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INJKAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INJKAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INJKAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INJKAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INJKAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INJKAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INJKAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INJKAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INJKAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INJKAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INJKAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INJKAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INJKAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INJKAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INJKAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INJKAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INJKAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INJKAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INJKAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INJKAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INJKAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INJKAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INJKAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INJKAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INJKAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INJKAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INJKAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INJKAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INJKAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INKAAD": [
        {
            "name": "DoorNumber_INKAAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INKAAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INKAAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INKAAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INKAAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INKAAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INKAAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INKAAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INKAAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INKAAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INKAAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INKAAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INKAAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INKAAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INKAAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INKAAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INKAAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INKAAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INKAAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INKAAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INKAAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INKAAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INKAAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INKAAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INKAAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INKAAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INKAAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INKAAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INKAAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INKAAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INKAAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INKAAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INKAAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INKAAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INKAAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INKAAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INKAAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INKAAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INKEAD": [
        {
            "name": "DoorNumber_INKEAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INKEAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INKEAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INKEAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INKEAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INKEAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INKEAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INKEAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INKEAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INKEAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INKEAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INKEAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INKEAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INKEAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INKEAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INKEAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INKEAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INKEAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INKEAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INKEAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INKEAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INKEAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INKEAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INKEAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INKEAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INKEAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INKEAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INKEAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INKEAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INKEAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INKEAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INKEAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INKEAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INKEAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INKEAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INKEAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INKEAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INKEAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INMHAD": [
        {
            "name": "DoorNumber_INMHAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INMHAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INMHAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INMHAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INMHAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INMHAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INMHAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INMHAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INMHAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INMHAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INMHAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INMHAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INMHAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INMHAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INMHAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INMHAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INMHAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INMHAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INMHAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INMHAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INMHAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INMHAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INMHAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INMHAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INMHAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INMHAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INMHAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INMHAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INMHAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INMHAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INMHAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INMHAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INMHAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INMHAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INMHAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INMHAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INMHAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INMHAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INMPAD": [
        {
            "name": "DoorNumber_INMPAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INMPAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INMPAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INMPAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INMPAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INMPAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INMPAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INMPAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INMPAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INMPAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INMPAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INMPAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INMPAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INMPAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INMPAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INMPAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INMPAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INMPAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INMPAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INMPAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INMPAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INMPAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INMPAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INMPAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INMPAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INMPAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INMPAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INMPAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INMPAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INMPAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INMPAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INMPAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INMPAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INMPAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INMPAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INMPAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INMPAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INMPAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INNAME": [
        {
            "name": "NameType_INNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_INNAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_INNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "NameInitials_INNAME",
            "description": "Name Initials",
            "max_length": 20,
        },
        {
            "name": "FirstName_INNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 128,
        },
        {
            "name": "MiddleName_INNAME",
            "description": "Middle Name of the Individual",
            "max_length": 128,
        },
        {
            "name": "PrimaryName_INNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 128,
        },
        {
            "name": "NameSuffix_INNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 50,
        },
        {
            "name": "AdditionalName_INNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "PrimaryNameNYSIIS_INNAME",
            "description": "Phonetic sound of the PrimaryName column",
            "max_length": 8,
        },
        {
            "name": "FirstNameNYSIIS_INNAME",
            "description": "Phonetic sound of the FirstName column",
            "max_length": 8,
        },
        {
            "name": "PrimaryNameSNDX_INNAME",
            "description": "Numerical representation of the phonetic sound of the PrimaryName column",
            "max_length": 4,
        },
        {
            "name": "FirstNameSNDX_INNAME",
            "description": "Numerical representation of the phonetic sound of the FirstName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_INNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_INNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_INNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_INNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INORAD": [
        {
            "name": "DoorNumber_INORAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INORAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INORAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INORAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INORAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INORAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INORAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INORAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INORAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INORAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INORAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INORAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INORAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INORAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INORAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INORAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INORAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INORAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INORAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INORAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INORAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INORAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INORAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INORAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INORAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INORAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INORAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INORAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INORAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INORAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INORAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INORAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INORAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INORAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INORAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INORAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INORAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INORAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INPBAD": [
        {
            "name": "DoorNumber_INPBAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INPBAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INPBAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INPBAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INPBAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INPBAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INPBAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INPBAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INPBAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INPBAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INPBAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INPBAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INPBAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INPBAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INPBAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INPBAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INPBAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INPBAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INPBAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INPBAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INPBAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INPBAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INPBAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INPBAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INPBAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INPBAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INPBAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INPBAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INPBAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INPBAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INPBAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INPBAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INPBAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INPBAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INPBAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INPBAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INPBAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INPBAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INRJAD": [
        {
            "name": "DoorNumber_INRJAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INRJAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INRJAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INRJAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INRJAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INRJAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INRJAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INRJAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INRJAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INRJAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INRJAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INRJAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INRJAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INRJAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INRJAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INRJAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INRJAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INRJAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INRJAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INRJAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INRJAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INRJAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INRJAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INRJAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INRJAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INRJAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INRJAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INRJAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INRJAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INRJAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INRJAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INRJAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INRJAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INRJAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INRJAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INRJAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INRJAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INRJAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INTNAD": [
        {
            "name": "DoorNumber_INTNAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INTNAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INTNAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INTNAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INTNAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INTNAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INTNAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INTNAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INTNAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INTNAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INTNAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INTNAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INTNAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INTNAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INTNAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INTNAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INTNAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INTNAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INTNAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INTNAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INTNAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INTNAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INTNAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INTNAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INTNAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INTNAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INTNAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INTNAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INTNAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INTNAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INTNAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INTNAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INTNAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INTNAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INTNAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INTNAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INTNAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INTNAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INUPAD": [
        {
            "name": "DoorNumber_INUPAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INUPAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INUPAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INUPAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INUPAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INUPAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INUPAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INUPAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INUPAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INUPAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INUPAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INUPAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INUPAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INUPAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INUPAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INUPAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INUPAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INUPAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INUPAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INUPAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INUPAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INUPAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INUPAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INUPAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INUPAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INUPAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INUPAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INUPAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INUPAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INUPAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INUPAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INUPAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INUPAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INUPAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INUPAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INUPAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INUPAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INUPAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "INWBAD": [
        {
            "name": "DoorNumber_INWBAD",
            "description": "Door number from the input data",
            "max_length": 50,
        },
        {
            "name": "PlotNumber_INWBAD",
            "description": "Plot number from the input data",
            "max_length": 50,
        },
        {
            "name": "FloorValue_INWBAD",
            "description": "Floor value from the input data",
            "max_length": 50,
        },
        {
            "name": "BuildingName_INWBAD",
            "description": "Building name from the input data; building names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingType_INWBAD",
            "description": "Building type from the input data;  building types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "BuildingInfo_INWBAD",
            "description": "Building information, which is a concatenation of the building name and building type; groups of building information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Unit_INWBAD",
            "description": "Unit information from the input data",
            "max_length": 100,
        },
        {
            "name": "StreetName_INWBAD",
            "description": "Street name from the input data; street names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetType_INWBAD",
            "description": "Street type from the input data; street types are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "StreetInfo_INWBAD",
            "description": "Street information, which is a concatenation of the street name and street type; groups of street information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "LandmarkPosition_INWBAD",
            "description": "Landmark position from the input data; landmark positions are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "Landmark_INWBAD",
            "description": "Landmark names from the input data; landmark names are separated by a comma",
            "max_length": 100,
        },
        {
            "name": "LandmarkInfo_INWBAD",
            "description": "Landmark information, which is a concatenation of the landmark position and landmark name; groups of landmark information are separated by a comma",
            "max_length": 200,
        },
        {
            "name": "Area_INWBAD",
            "description": "Area or village information from the input data",
            "max_length": 100,
        },
        {
            "name": "Subarea_INWBAD",
            "description": "A smaller area within an area from the input data",
            "max_length": 100,
        },
        {
            "name": "Locality_INWBAD",
            "description": "Locality information from the input data",
            "max_length": 200,
        },
        {
            "name": "AdditionalInfo_INWBAD",
            "description": "Additional address information",
            "max_length": 200,
        },
        {
            "name": "CompanyName_INWBAD",
            "description": "Organization name from the input data",
            "max_length": 200,
        },
        {
            "name": "RelationshipInfo_INWBAD",
            "description": "Relationship information from the input data",
            "max_length": 200,
        },
        {
            "name": "DoorMatch_INWBAD",
            "description": "DoorNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "PlotMatch_INWBAD",
            "description": "PlotNumber column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "FloorMatch_INWBAD",
            "description": "FloorValue column with special characters removed",
            "max_length": 50,
        },
        {
            "name": "UnitMatch_INWBAD",
            "description": "Unit column with spaces removed",
            "max_length": 50,
        },
        {
            "name": "SubareaMatch_INWBAD",
            "description": "SubArea column with spaces removed",
            "max_length": 200,
        },
        {
            "name": "ConcatenatedBldgName_INWBAD",
            "description": "BuildingName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISBuilding_INWBAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 8,
        },
        {
            "name": "SoundexBuilding_INWBAD",
            "description": "Phonetic sound of the ConcatenatedBldgName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedStreetName_INWBAD",
            "description": "StreetName column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISStreet_INWBAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_INWBAD",
            "description": "Phonetic sound of the ConcatenatedStreetName column",
            "max_length": 4,
        },
        {
            "name": "ConcatenatedLandmarkPos_INWBAD",
            "description": "LandmarkPosition column concatenated without space and comma",
            "max_length": 200,
        },
        {
            "name": "NYSIISArea_INWBAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 8,
        },
        {
            "name": "SoundexArea_INWBAD",
            "description": "Phonetic sound of the ConcatenatedLandmarkPos column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_INWBAD",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_INWBAD",
            "description": "Data that is not processed by the rule set",
            "max_length": 200,
        },
        {
            "name": "InputPattern_INWBAD",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 100,
        },
        {
            "name": "ExceptionData_INWBAD",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_INWBAD",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "JP1PHN": [
        {
            "name": "PhoneNumber_JP1PHN",
            "description": "\u96fb\u8a71\u756a\u53f7(\u7d50\u5408)",
            "max_length": 20,
        },
        {
            "name": "CountryCode_JP1PHN",
            "description": "\u56fd\u30b3\u30fc\u30c9",
            "max_length": 2,
        },
        {
            "name": "DialingCode_JP1PHN",
            "description": "DialingCode\uff08\u5e02\u5916\u5c40\u756a\u306e\u5148\u982d\u306b\u3042\u308b\u6570\u5b57\u3002\u901a\u5e380)",
            "max_length": 1,
        },
        {
            "name": "AreaCode_JP1PHN",
            "description": "\u5e02\u5916\u5c40\u756a(DialingCode\u3092\u53d6\u308a\u9664\u3044\u305f\u3082\u306e)",
            "max_length": 5,
        },
        {
            "name": "Exchange_JP1PHN",
            "description": "\u5c40\u756a",
            "max_length": 4,
        },
        {"name": "Line_JP1PHN", "description": "\u756a\u53f7", "max_length": 8},
        {
            "name": "SpecialNumberFlag_JP1PHN",
            "description": "\u7279\u6b8a\u5c40\u756a\u30d5\u30e9\u30b0 \u30d5\u30ea\u30fc\u30c0\u30a4\u30e4\u30eb\u306a\u3069\u306e\u7279\u6b8a\u756a\u53f7(0\u306b\u7d9a\u304f\u6570\u5b57\u304cJPSPEC.TBL)\u306e\u5834\u5408Y",
            "max_length": 1,
        },
        {
            "name": "UnhandledPattern_JP1PHN",
            "description": "\u4e0d\u6271\u30d1\u30bf\u30fc\u30f3(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 10,
        },
        {
            "name": "UnhandledData_JP1PHN",
            "description": "\u4e0d\u6271\u30c7\u30fc\u30bf(\u30eb\u30fc\u30eb\u3067\u51e6\u7406\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 20,
        },
        {
            "name": "InputPattern_JP1PHN",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 10,
        },
        {
            "name": "ExceptionData_JP1PHN",
            "description": "\u4f8b\u5916\u30c7\u30fc\u30bf",
            "max_length": 20,
        },
        {
            "name": "UserOverrideFlag_JP1PHN",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
    ],
    "JP2PHN": [
        {
            "name": "PhoneNumber_JP2PHN",
            "description": "\u96fb\u8a71\u756a\u53f7(\u7d50\u5408)",
            "max_length": 20,
        },
        {
            "name": "CountryCode_JP2PHN",
            "description": "\u56fd\u30b3\u30fc\u30c9",
            "max_length": 2,
        },
        {
            "name": "DialingCode_JP2PHN",
            "description": "DialingCode\uff08\u5e02\u5916\u5c40\u756a\u306e\u5148\u982d\u306b\u3042\u308b\u6570\u5b57\u3002\u901a\u5e380)",
            "max_length": 1,
        },
        {
            "name": "AreaCode_JP2PHN",
            "description": "\u5e02\u5916\u5c40\u756a(DialingCode\u3092\u53d6\u308a\u9664\u3044\u305f\u3082\u306e)",
            "max_length": 5,
        },
        {
            "name": "Exchange_JP2PHN",
            "description": "\u5c40\u756a",
            "max_length": 4,
        },
        {"name": "Line_JP2PHN", "description": "\u756a\u53f7", "max_length": 8},
        {
            "name": "SpecialNumberFlag_JP2PHN",
            "description": "\u7279\u6b8a\u5c40\u756a\u30d5\u30e9\u30b0 \u30d5\u30ea\u30fc\u30c0\u30a4\u30e4\u30eb\u306a\u3069\u306e\u7279\u6b8a\u756a\u53f7(0\u306b\u7d9a\u304f\u6570\u5b57\u304cJPSPEC.TBL)\u306e\u5834\u5408Y",
            "max_length": 1,
        },
        {
            "name": "UnhandledPattern_JP2PHN",
            "description": "\u4e0d\u6271\u30d1\u30bf\u30fc\u30f3(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 10,
        },
        {
            "name": "UnhandledData_JP2PHN",
            "description": "\u4e0d\u6271\u30c7\u30fc\u30bf(\u30eb\u30fc\u30eb\u3067\u51e6\u7406\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 20,
        },
        {
            "name": "InputPattern_JP2PHN",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 10,
        },
        {
            "name": "ExceptionData_JP2PHN",
            "description": "\u4f8b\u5916\u30c7\u30fc\u30bf",
            "max_length": 20,
        },
        {
            "name": "UserOverrideFlag_JP2PHN",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
    ],
    "JPADDR": [
        {
            "name": "OazaType_JPADDR",
            "description": "\u5927\u5b57\u30bf\u30a4\u30d7(\u300c\u5b57\u300d\u307e\u305f\u306f\u300c\u5927\u5b57\u300d)",
            "max_length": 6,
        },
        {
            "name": "OazaValue_JPADDR",
            "description": "\u5927\u5b57\u5024",
            "max_length": 30,
        },
        {
            "name": "KoazaType_JPADDR",
            "description": "\u5c0f\u5b57\u30bf\u30a4\u30d7(\u300c\u5b57\u300d\u300c\u5c0f\u5b57\u300d)",
            "max_length": 6,
        },
        {
            "name": "KoazaValue_JPADDR",
            "description": "\u5c0f\u5b57\u5024",
            "max_length": 30,
        },
        {
            "name": "AliasValue_JPADDR",
            "description": "\u901a\u79f0",
            "max_length": 20,
        },
        {
            "name": "AddressNumber1_JPADDR",
            "description": "\u6570\u5024\uff11",
            "max_length": 12,
        },
        {
            "name": "TypeofNumber1_JPADDR",
            "description": "\u6570\u5024\u30bf\u30a4\u30d7\uff11",
            "max_length": 6,
        },
        {
            "name": "AddressNumber2_JPADDR",
            "description": "\u6570\u5024\uff12",
            "max_length": 12,
        },
        {
            "name": "TypeofNumber2_JPADDR",
            "description": "\u6570\u5024\u30bf\u30a4\u30d7\uff12",
            "max_length": 6,
        },
        {
            "name": "AddressNumber3_JPADDR",
            "description": "\u6570\u5024\uff13",
            "max_length": 12,
        },
        {
            "name": "TypeofNumber3_JPADDR",
            "description": "\u6570\u5024\u30bf\u30a4\u30d7\uff13",
            "max_length": 4,
        },
        {
            "name": "BuildingName_JPADDR",
            "description": "\u5efa\u7269\u540d",
            "max_length": 50,
        },
        {
            "name": "BuildingValueType_JPADDR",
            "description": "\u5efa\u7269\u756a\u53f7\u30bf\u30a4\u30d7",
            "max_length": 6,
        },
        {
            "name": "BuildingValue_JPADDR",
            "description": "\u5efa\u7269\u756a\u53f7",
            "max_length": 5,
        },
        {
            "name": "FloorType_JPADDR",
            "description": "\u30d5\u30ed\u30a2\u30bf\u30a4\u30d7 \u300c\u968e\u300d\u300cF\u300d\u306a\u3069",
            "max_length": 4,
        },
        {
            "name": "FloorValue_JPADDR",
            "description": "\u30d5\u30ed\u30a2\u5024(\u968e)",
            "max_length": 5,
        },
        {
            "name": "RoomType_JPADDR",
            "description": "\u90e8\u5c4b\u756a\u53f7\u30bf\u30a4\u30d7(\u90e8\u5c4b\u756a\u53f7\u306b\u3064\u3044\u305f\u5358\u4f4d\u3002\u53f7\u5ba4\u306a\u3069\u3002)",
            "max_length": 6,
        },
        {
            "name": "RoomValue_JPADDR",
            "description": "\u90e8\u5c4b\u756a\u53f7",
            "max_length": 5,
        },
        {
            "name": "CareofValue_JPADDR",
            "description": "\u6c17\u4ed8\u30fb\u69d8\u65b9\u5024",
            "max_length": 40,
        },
        {
            "name": "CareofType_JPADDR",
            "description": "\u6c17\u4ed8\u30fb\u69d8\u65b9\u30bf\u30a4\u30d7",
            "max_length": 6,
        },
        {
            "name": "PostBoxPrefix_JPADDR",
            "description": "\u79c1\u66f8\u7bb1\u30d7\u30ea\u30d5\u30a3\u30af\u30b9 \u300c\u79c1\u66f8\u7bb1\u300d\u306a\u3069",
            "max_length": 8,
        },
        {
            "name": "PostBoxValue_JPADDR",
            "description": "\u79c1\u66f8\u7bb1\u5024",
            "max_length": 5,
        },
        {
            "name": "PostBoxSuffix_JPADDR",
            "description": "\u79c1\u66f8\u7bb1\u30b5\u30d5\u30a3\u30c3\u30af\u30b9 \u300c\u53f7\u300d\u306a\u3069",
            "max_length": 4,
        },
        {
            "name": "AdditionalAddress_JPADDR",
            "description": "\u305d\u306e\u4ed6\u4f4f\u6240\u60c5\u5831",
            "max_length": 50,
        },
        {
            "name": "UnhandledPattern_JPADDR",
            "description": "\u30a2\u30f3\u30cf\u30f3\u30c9\u30eb\u30fb\u30d1\u30bf\u30fc\u30f3 (\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_JPADDR",
            "description": "\u30a2\u30f3\u30cf\u30f3\u30c9\u30eb\u30fb\u30c7\u30fc\u30bf (\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 50,
        },
        {
            "name": "InputPattern_JPADDR",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 30,
        },
        {
            "name": "OazaKoazaPattern_JPADDR",
            "description": "\u5927\u5b57\u5c0f\u5b57\u30d1\u30bf\u30fc\u30f3\uff08\u5927\u5b57\u5c0f\u5b57\u30c6\u30fc\u30d6\u30eb\u691c\u7d22\u5f8c\u306e\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 30,
        },
        {
            "name": "ExceptionalData_JPADDR",
            "description": "\u4f8b\u5916\u30c7\u30fc\u30bf",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_JPADDR",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
        {
            "name": "KyotoStreetFlag_JPADDR",
            "description": "\u4eac\u90fd\u901a\u308a\u540d\u30d5\u30e9\u30b0 \u4eac\u90fd\u901a\u308a\u540d\u306e\u4f4f\u6240\u306e\u5834\u5408Y",
            "max_length": 1,
        },
        {
            "name": "BuildingFlag_JPADDR",
            "description": "\u9ad8\u5c64\u30c6\u30ca\u30f3\u30c8\u30d3\u30eb\u30d5\u30e9\u30b0 CLS\u30d5\u30a1\u30a4\u30eb\u306b\u767b\u9332\u3055\u308c\u305f\u9ad8\u5c64\u30c6\u30ca\u30f3\u30c8\u30d3\u30eb\u306e\u5834\u5408Y",
            "max_length": 1,
        },
        {
            "name": "NumberOrderInfo_JPADDR",
            "description": "\u756a\u53f7\u9806\u5e8f\u60c5\u5831 \u5efa\u7269\u540d\u3088\u308a\u524d\u306e\u6570\u5024\u3092\u90e8\u5c4b\u756a\u53f7\u3068\u3057\u305f\u3068\u304d\u300cR1\u300d",
            "max_length": 10,
        },
    ],
    "JPAREA": [
        {
            "name": "ISOCountryCode_JPAREA",
            "description": "\uff29\uff33\uff2f\u56fd\u30b3\u30fc\u30c9",
            "max_length": 2,
        },
        {
            "name": "Prefecture_JPAREA",
            "description": "\u90fd\u9053\u5e9c\u770c\u540d",
            "max_length": 12,
        },
        {
            "name": "City_JPAREA",
            "description": "\u5e02\u753a\u6751\u540d",
            "max_length": 34,
        },
        {
            "name": "PrefectureName_JPAREA",
            "description": "\u90fd\u9053\u5e9c\u770c\u5024",
            "max_length": 8,
        },
        {
            "name": "PrefectureType_JPAREA",
            "description": "\u90fd\u9053\u5e9c\u770c\u30bf\u30a4\u30d7",
            "max_length": 4,
        },
        {
            "name": "CityName_JPAREA",
            "description": "\u5e02\u753a\u6751\u5024",
            "max_length": 30,
        },
        {
            "name": "CityType_JPAREA",
            "description": "\u5e02\u753a\u6751\u30bf\u30a4\u30d7",
            "max_length": 4,
        },
        {
            "name": "AddressDomain_JPAREA",
            "description": "\u4f4f\u6240\u30c9\u30e1\u30a4\u30f3(\u5e02\u533a\u753a\u6751\u3088\u308a\u8a73\u7d30\u306e\u4f4f\u6240)",
            "max_length": 100,
        },
        {
            "name": "JIS5Code_JPAREA",
            "description": "JIS5\u30b3\u30fc\u30c9",
            "max_length": 5,
        },
        {
            "name": "UnhandledPattern_JPAREA",
            "description": "\u4e0d\u6271\u30d1\u30bf\u30fc\u30f3(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_JPAREA",
            "description": "\u4e0d\u6271\u30c7\u30fc\u30bf(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 50,
        },
        {
            "name": "InputPattern_JPAREA",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_JPAREA",
            "description": "\u4f8b\u5916\u30c7\u30fc\u30bf",
            "max_length": 50,
        },
        {
            "name": "CityVerifiedFlag_JPAREA",
            "description": "\u5e02\u753a\u6751\u5024\u4e0d\u660e\u30d5\u30e9\u30b0(\u672a\u4f7f\u7528)",
            "max_length": 1,
        },
        {
            "name": "UserOverrideFlag_JPAREA",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
    ],
    "JPDATE": [
        {
            "name": "ValidFlag_JPDATE",
            "description": "\u65e5\u4ed8\u6b63\u5f53\u6027\u78ba\u8a8d\u30d5\u30e9\u30b0",
            "max_length": 1,
        },
        {
            "name": "EraIndicator_JPDATE",
            "description": "\u5143\u53f7",
            "max_length": 1,
        },
        {
            "name": "DateYYYYMMDD_JPDATE",
            "description": "\u65e5\u4ed8(\uff39\uff39\uff39\uff39\uff2d\uff2d\uff24\uff24)",
            "max_length": 8,
        },
        {
            "name": "Year_JPDATE",
            "description": "\u897f\u66a6(YYYY)",
            "max_length": 4,
        },
        {"name": "Month_JPDATE", "description": "\u6708(MM)", "max_length": 2},
        {"name": "Day_JPDATE", "description": "\u65e5(DD)", "max_length": 2},
        {
            "name": "UnhandledPattern_JPDATE",
            "description": "\u30a2\u30f3\u30cf\u30f3\u30c9\u30eb\u30fb\u30d1\u30bf\u30fc\u30f3 (\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 10,
        },
        {
            "name": "UnhandledData_JPDATE",
            "description": "\u30a2\u30f3\u30cf\u30f3\u30c9\u30eb\u30fb\u30c7\u30fc\u30bf (\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 20,
        },
        {
            "name": "InputPattern_JPDATE",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 10,
        },
        {
            "name": "ExceptionData_JPDATE",
            "description": "\u4f8b\u5916\u30c7\u30fc\u30bf(\u672a\u4f7f\u7528)",
            "max_length": 10,
        },
        {
            "name": "ExceptionReason_JPDATE",
            "description": "\u4f8b\u5916(\u672a\u4f7f\u7528)",
            "max_length": 2,
        },
        {
            "name": "UserOverrideFlag_JPDATE",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
    ],
    "JPKANA": [
        {
            "name": "KanjiAddress_JPKANA",
            "description": "\u6f22\u5b57\u4f4f\u6240",
            "max_length": 100,
        },
        {
            "name": "ConversionFlag_JPKANA",
            "description": "\u6f22\u5b57\u5909\u63db\u30d5\u30e9\u30b0 \u770c\u307e\u3067\u5909\u63db=1,\u5e02\u753a\u6751\u307e\u3067\u5909\u63db=2,\u5927\u5b57\u30ec\u30d9\u30eb\u307e\u3067\u5909\u63db=3 \u5909\u63db\u306a\u3057=4",
            "max_length": 1,
        },
        {
            "name": "InputPattern_JPKANA",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 50,
        },
        {
            "name": "UnhandledPattern_JPKANA",
            "description": "\u4e0d\u6271\u30d1\u30bf\u30fc\u30f3(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_JPKANA",
            "description": "\u4e0d\u6271\u30c7\u30fc\u30bf(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_JPKANA",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
    ],
    "JPKNAM": [
        {
            "name": "NamePrefix_JPKNAM",
            "description": "\u6cd5\u4eba\u683c",
            "max_length": 20,
        },
        {
            "name": "PrefixFlag_JPKNAM",
            "description": "\u6cd5\u4eba\u683c\u30d5\u30e9\u30b0 \u524d\u682a=1 \u5f8c\u682a=2",
            "max_length": 1,
        },
        {
            "name": "PositionTitle_JPKNAM",
            "description": "\u5f79\u8077\u540d",
            "max_length": 20,
        },
        {
            "name": "CorporationName_JPKNAM",
            "description": "\u6cd5\u4eba\u540d",
            "max_length": 50,
        },
        {
            "name": "CorporationNameKanji_JPKNAM",
            "description": "\u6cd5\u4eba\u540d\u6f22\u5b57\u5019\u88dc",
            "max_length": 50,
        },
        {
            "name": "BranchName_JPKNAM",
            "description": "\u679d\u540d",
            "max_length": 30,
        },
        {
            "name": "BranchType_JPKNAM",
            "description": "\u679d\u540d\u30bf\u30a4\u30d7",
            "max_length": 10,
        },
        {
            "name": "PrimaryName_JPKNAM",
            "description": "\u59d3",
            "max_length": 20,
        },
        {
            "name": "PrimaryNameKanji_JPKNAM",
            "description": "\u59d3\uff08\u6f22\u5b57\u5019\u88dc\uff09",
            "max_length": 20,
        },
        {"name": "FirstName_JPKNAM", "description": "\u540d", "max_length": 10},
        {
            "name": "FirstNameKanji_JPKNAM",
            "description": "\u540d\uff08\u6f22\u5b57\u5019\u88dc\uff09",
            "max_length": 10,
        },
        {
            "name": "CustomerName_JPKNAM",
            "description": "\u59d3\u540d\uff08\u9023\u7d50\uff09",
            "max_length": 30,
        },
        {
            "name": "AdditionalName_JPKNAM",
            "description": "\u4ed6\u306e\u540d\u524d\u60c5\u5831",
            "max_length": 50,
        },
        {
            "name": "UnhandledPattern_JPKNAM",
            "description": "\u4e0d\u6271\u30d1\u30bf\u30fc\u30f3 (\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_JPKNAM",
            "description": "\u4e0d\u6271\u30c7\u30fc\u30bf(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 50,
        },
        {
            "name": "InputPattern_JPKNAM",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_JPKNAM",
            "description": "\u4f8b\u5916\u30c7\u30fc\u30bf(\u672a\u4f7f\u7528)",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_JPKNAM",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
    ],
    "JPNAME": [
        {
            "name": "NamePrefix_JPNAME",
            "description": "\u6cd5\u4eba\u683c",
            "max_length": 20,
        },
        {
            "name": "PrefixFlag_JPNAME",
            "description": "\u6cd5\u4eba\u683c\u30d5\u30e9\u30b0 \u524d\u682a=1,\u5f8c\u682a=2",
            "max_length": 1,
        },
        {
            "name": "PositionTitle_JPNAME",
            "description": "\u5f79\u8077\u540d",
            "max_length": 20,
        },
        {
            "name": "CorporationName_JPNAME",
            "description": "\u6cd5\u4eba\u540d",
            "max_length": 50,
        },
        {
            "name": "CorporationNameInput_JPNAME",
            "description": "\u6cd5\u4eba\u540d\uff08\u5165\u529b\u3068\u540c\u3058\u6f22\u5b57\u8868\u8a18\uff09",
            "max_length": 50,
        },
        {
            "name": "BranchName_JPNAME",
            "description": "\u679d\u540d(\u652f\u5e97\u540d\u306a\u3069)",
            "max_length": 30,
        },
        {
            "name": "BranchNameInput_JPNAME",
            "description": "\u679d\u540d(\u5165\u529b\u3068\u540c\u3058\u6f22\u5b57\u8868\u8a18)",
            "max_length": 30,
        },
        {
            "name": "BranchNameType_JPNAME",
            "description": "\u679d\u540d\u30bf\u30a4\u30d7",
            "max_length": 10,
        },
        {
            "name": "PrimaryName_JPNAME",
            "description": "\u59d3",
            "max_length": 20,
        },
        {
            "name": "PrimaryNameInput_JPNAME",
            "description": "\u59d3(\u5165\u529b\u3068\u540c\u3058\u6f22\u5b57\u8868\u8a18)",
            "max_length": 20,
        },
        {"name": "FirstName_JPNAME", "description": "\u540d", "max_length": 10},
        {
            "name": "FirstNameInput_JPNAME",
            "description": "\u540d(\u5165\u529b\u3068\u540c\u3058\u6f22\u5b57\u8868\u8a18)",
            "max_length": 10,
        },
        {
            "name": "CustomerName_JPNAME",
            "description": "\u59d3\u540d\uff08\u9023\u7d50\uff09",
            "max_length": 50,
        },
        {
            "name": "AdditionalName_JPNAME",
            "description": "\u4ed6\u306e\u540d\u524d\u60c5\u5831",
            "max_length": 50,
        },
        {
            "name": "UnhandledPattern_JPNAME",
            "description": "\u4e0d\u6271\u30d1\u30bf\u30fc\u30f3(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_JPNAME",
            "description": "\u4e0d\u6271\u30c7\u30fc\u30bf(\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 50,
        },
        {
            "name": "InputPattern_JPNAME",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_JPNAME",
            "description": "\u4f8b\u5916\u30c7\u30fc\u30bf",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_JPNAME",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
    ],
    "JPTRIM": [
        {
            "name": "TrimmedValueKanji_JPTRIM",
            "description": "\u7a7a\u767d\u524a\u9664\u6e08\u307f\u6a19\u6e96\u5316\u7528\u30c7\u30fc\u30bf",
            "max_length": 100,
        },
        {
            "name": "TrimmedValueLookup_JPTRIM",
            "description": "JPKANA\u5fa9\u5143\u7528\u30ab\u30ca\u30c7\u30fc\u30bf",
            "max_length": 100,
        },
        {
            "name": "SourceFieldFlag_JPTRIM",
            "description": '"\u30ab\u30ca\u51e6\u7406\u306e\u5834\u5408\u300c1\u300d\u6f22\u5b57\u4f4f\u6240\u306e\u51e6\u7406\u306e\u5834\u5408\u300c2\u300d;0201-0201',
            "max_length": 1,
        },
        {
            "name": "InputPattern_JPTRIM",
            "description": "\u5165\u529b\u30d1\u30bf\u30fc\u30f3",
            "max_length": 50,
        },
        {
            "name": "UnhandledPattern_JPTRIM",
            "description": "\u4e0d\u6271\u30d1\u30bf\u30fc\u30f3 (\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30d1\u30bf\u30fc\u30f3)",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_JPTRIM",
            "description": "\u4e0d\u6271\u30c7\u30fc\u30bf (\u30eb\u30fc\u30eb\u3067\u30cf\u30f3\u30c9\u30eb\u3057\u306a\u304b\u3063\u305f\u30c7\u30fc\u30bf)",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_JPTRIM",
            "description": "\u30aa\u30fc\u30d0\u30fc\u30e9\u30a4\u30c9\u304c\u9069\u7528\u3055\u308c\u305f\u304b\u3069\u3046\u304b\u306e\u30d5\u30e9\u30b0",
            "max_length": 2,
        },
    ],
    "KOADDR": [
        {
            "name": "OldAreaName_KOADDR",
            "description": "OldAreaName",
            "max_length": 30,
        },
        {
            "name": "SanIdentifier_KOADDR",
            "description": "SanIdentifier",
            "max_length": 3,
        },
        {
            "name": "BunjiValue_KOADDR",
            "description": "BunjiValue",
            "max_length": 30,
        },
        {"name": "HoValue_KOADDR", "description": "HoValue", "max_length": 15},
        {
            "name": "TongValue_KOADDR",
            "description": "TongValue",
            "max_length": 15,
        },
        {
            "name": "BanValue_KOADDR",
            "description": "BanValue",
            "max_length": 15,
        },
        {
            "name": "BlockValue_KOADDR",
            "description": "BlockValue",
            "max_length": 15,
        },
        {
            "name": "LotValue_KOADDR",
            "description": "LotValue",
            "max_length": 15,
        },
        {
            "name": "PiljiValue_KOADDR",
            "description": "PiljiValue",
            "max_length": 15,
        },
        {
            "name": "FloorValue01_KOADDR",
            "description": "FloorValue01",
            "max_length": 15,
        },
        {
            "name": "StreetValue_KOADDR",
            "description": "StreetValue",
            "max_length": 30,
        },
        {
            "name": "StreetMBun_KOADDR",
            "description": "StreetMBun",
            "max_length": 15,
        },
        {
            "name": "StreetSBun_KOADDR",
            "description": "StreetSBun",
            "max_length": 15,
        },
        {
            "name": "ZoneName_KOADDR",
            "description": "ZoneName",
            "max_length": 50,
        },
        {"name": "ZoneBun_KOADDR", "description": "ZoneBun", "max_length": 30},
        {
            "name": "VillageName_KOADDR",
            "description": "VillageName",
            "max_length": 50,
        },
        {
            "name": "BldgMName1_KOADDR",
            "description": "BldgMName1",
            "max_length": 50,
        },
        {
            "name": "BldgMName2_KOADDR",
            "description": "BldgMName2",
            "max_length": 50,
        },
        {
            "name": "BldgMName3_KOADDR",
            "description": "BldgMName3",
            "max_length": 50,
        },
        {
            "name": "BuildingType_KOADDR",
            "description": "BuildingType",
            "max_length": 24,
        },
        {
            "name": "BuildingSequence_KOADDR",
            "description": "BuildingSequence",
            "max_length": 15,
        },
        {
            "name": "BuildingComplex_KOADDR",
            "description": "BuildingComplex",
            "max_length": 15,
        },
        {
            "name": "BldgSName1_KOADDR",
            "description": "BldgSName1",
            "max_length": 50,
        },
        {
            "name": "BldgSName2_KOADDR",
            "description": "BldgSName2",
            "max_length": 50,
        },
        {
            "name": "PostOfficeBox_KOADDR",
            "description": "PostOfficeBox",
            "max_length": 50,
        },
        {
            "name": "FloorValue02_KOADDR",
            "description": "FloorValue02",
            "max_length": 15,
        },
        {
            "name": "DongValue_KOADDR",
            "description": "DongValue",
            "max_length": 15,
        },
        {
            "name": "FloorValue03_KOADDR",
            "description": "FloorValue03",
            "max_length": 15,
        },
        {
            "name": "RoomValue_KOADDR",
            "description": "RoomValue",
            "max_length": 15,
        },
        {
            "name": "OtherBldgName_KOADDR",
            "description": "OtherBldgName",
            "max_length": 100,
        },
        {
            "name": "ExceptErr_KOADDR",
            "description": "ExceptErr",
            "max_length": 3,
        },
        {
            "name": "RemainderValue_KOADDR",
            "description": "RemainderValue",
            "max_length": 100,
        },
        {
            "name": "AddressType_KOADDR",
            "description": "AddressType",
            "max_length": 3,
        },
        {
            "name": "UnhandledPattern_KOADDR",
            "description": "UnhandledPattern",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_KOADDR",
            "description": "UnhandledData",
            "max_length": 250,
        },
        {
            "name": "InputPattern_KOADDR",
            "description": "InputPattern",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_KOADDR",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "KOAREA": [
        {
            "name": "SpecialMetroName_KOAREA",
            "description": "SpecialMetroName",
            "max_length": 6,
        },
        {
            "name": "SpecialMetroType_KOAREA",
            "description": "SpecialMetroType",
            "max_length": 9,
        },
        {
            "name": "MetroName_KOAREA",
            "description": "MetroName",
            "max_length": 6,
        },
        {
            "name": "MetroType_KOAREA",
            "description": "MetroType",
            "max_length": 9,
        },
        {"name": "DoName_KOAREA", "description": "DoName", "max_length": 9},
        {"name": "DoType_KOAREA", "description": "DoType", "max_length": 3},
        {"name": "SiName_KOAREA", "description": "SiName", "max_length": 9},
        {"name": "SiType_KOAREA", "description": "SiType", "max_length": 3},
        {"name": "GunName_KOAREA", "description": "GunName", "max_length": 9},
        {"name": "GunType_KOAREA", "description": "GunType", "max_length": 3},
        {"name": "GuName_KOAREA", "description": "GuName", "max_length": 12},
        {"name": "GuType_KOAREA", "description": "GuType", "max_length": 3},
        {"name": "EupName_KOAREA", "description": "EupName", "max_length": 15},
        {"name": "EupType_KOAREA", "description": "EupType", "max_length": 3},
        {
            "name": "MyeonName_KOAREA",
            "description": "MyeonName",
            "max_length": 15,
        },
        {
            "name": "MyeonType_KOAREA",
            "description": "MyeonType",
            "max_length": 3,
        },
        {
            "name": "DongName_KOAREA",
            "description": "DongName",
            "max_length": 27,
        },
        {"name": "DongType_KOAREA", "description": "DongType", "max_length": 3},
        {"name": "GaName_KOAREA", "description": "GaName", "max_length": 27},
        {"name": "GaType_KOAREA", "description": "GaType", "max_length": 3},
        {"name": "NoName_KOAREA", "description": "NoName", "max_length": 27},
        {"name": "NoType_KOAREA", "description": "NoType", "max_length": 3},
        {"name": "RiName_KOAREA", "description": "RiName", "max_length": 27},
        {"name": "RiType_KOAREA", "description": "RiType", "max_length": 3},
        {
            "name": "DoseoName_KOAREA",
            "description": "DoseoName",
            "max_length": 21,
        },
        {
            "name": "RemainderAValue_KOAREA",
            "description": "RemainderAValue",
            "max_length": 60,
        },
        {
            "name": "DongLawCode_KOAREA",
            "description": "DongLawCode",
            "max_length": 10,
        },
        {
            "name": "DongAdmCode_KOAREA",
            "description": "DongAdmCode",
            "max_length": 10,
        },
        {
            "name": "CountryCode_KOAREA",
            "description": "CountryCode",
            "max_length": 6,
        },
        {
            "name": "UnhandledPattern_KOAREA",
            "description": "UnhandledPattern",
            "max_length": 100,
        },
        {
            "name": "UnhandledData_KOAREA",
            "description": "UnhandledData",
            "max_length": 250,
        },
        {
            "name": "InputPattern_KOAREA",
            "description": "InputPattern",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_KOAREA",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "KONAME": [
        {
            "name": "CompanyType1_KONAME",
            "description": "NameType",
            "max_length": 12,
        },
        {
            "name": "CompanyName_KONAME",
            "description": "CompanyName",
            "max_length": 90,
        },
        {
            "name": "CompanyType2_KONAME",
            "description": "NameType",
            "max_length": 12,
        },
        {
            "name": "Branchname_KONAME",
            "description": "NameType",
            "max_length": 45,
        },
        {
            "name": "UnhandledPattern_KONAME",
            "description": "UnhandledPattern",
            "max_length": 50,
        },
        {
            "name": "UnhandledData_KONAME",
            "description": "UnhandledData",
            "max_length": 90,
        },
        {
            "name": "InputPattern_KONAME",
            "description": "InputPattern",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_KONAME",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "KOPREP": [
        {
            "name": "AreaDomain_KOPREP",
            "description": "AreaDomain",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_KOPREP",
            "description": "AddressDomain",
            "max_length": 200,
        },
        {
            "name": "Field1Pattern_KOPREP",
            "description": "Field1Pattern",
            "max_length": 100,
        },
        {
            "name": "Field2Pattern_KOPREP",
            "description": "Field2Pattern",
            "max_length": 50,
        },
        {
            "name": "Field3Pattern_KOPREP",
            "description": "Field3Pattern",
            "max_length": 50,
        },
        {
            "name": "Field4Pattern_KOPREP",
            "description": "Field4Pattern",
            "max_length": 50,
        },
        {
            "name": "Field5Pattern_KOPREP",
            "description": "Field5Pattern",
            "max_length": 50,
        },
        {
            "name": "Field6Pattern_KOPREP",
            "description": "Field6Pattern",
            "max_length": 50,
        },
        {
            "name": "InputPattern_KOPREP",
            "description": "InputPattern",
            "max_length": 100,
        },
        {
            "name": "OutboundPattern_KOPREP",
            "description": "OutboundPattern",
            "max_length": 100,
        },
        {
            "name": "UserOverrideFlag_KOPREP",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_KOPREP",
            "description": "CustomFlag",
            "max_length": 2,
        },
    ],
    "THADDR": [
        {
            "name": "House_Number_THADDR",
            "description": "House_Number",
            "max_length": 100,
        },
        {"name": "Moo_THADDR", "description": "Moo", "max_length": 100},
        {"name": "Soi_THADDR", "description": "Soi", "max_length": 100},
        {
            "name": "Building_THADDR",
            "description": "Building",
            "max_length": 100,
        },
        {"name": "Floor_THADDR", "description": "Floor", "max_length": 100},
        {"name": "Room_THADDR", "description": "Room", "max_length": 100},
        {"name": "Road_THADDR", "description": "Road", "max_length": 100},
        {"name": "Tambon_THADDR", "description": "Tambon", "max_length": 100},
        {"name": "Amphoe_THADDR", "description": "Amphoe", "max_length": 100},
        {
            "name": "Changwat_THADDR",
            "description": "Changwat",
            "max_length": 100,
        },
        {"name": "Zip_THADDR", "description": "Zip", "max_length": 100},
        {
            "name": "UnhandledPattern_THADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_THADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_THADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_THADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_THADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "THNAME": [
        {
            "name": "CompanyName_THNAME",
            "description": "Thai Company Name",
            "max_length": 100,
        },
        {
            "name": "CompanyType_THNAME",
            "description": "Thai Company Type",
            "max_length": 50,
        },
        {
            "name": "NamePrefix_THNAME",
            "description": "Thai Name Prefix",
            "max_length": 25,
        },
        {
            "name": "GivenName_THNAME",
            "description": "Thai Given Name",
            "max_length": 50,
        },
        {
            "name": "FamilyName_THNAME",
            "description": "Thai Family Name",
            "max_length": 50,
        },
        {
            "name": "UnhandledPattern_THNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_THNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_THNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_THNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_THNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "THPHON": [
        {"name": "PF_THPHON", "description": "PhonePrefix", "max_length": 3},
        {"name": "PN_THPHON", "description": "PhoneNumber", "max_length": 7},
        {"name": "PE_THPHON", "description": "PhoneExtension", "max_length": 7},
        {
            "name": "PP_THPHON",
            "description": "PhoneNumberPeriod",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_THPHON",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_THPHON",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_THPHON",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "InputData_THPHON",
            "description": "Input Data",
            "max_length": 100,
        },
        {"name": "Debug_THPHON", "description": "Debug", "max_length": 100},
        {
            "name": "ExceptionData_THPHON",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_THPHON",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "MXADDR": [
        {
            "name": "TipoDireccion_MXADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "PrefijoTipoCalle_MXADDR",
            "description": "Ordinal number that appears before the street type",
            "max_length": 15,
        },
        {
            "name": "TipoCalle_MXADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 20,
        },
        {
            "name": "Calle_MXADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "Kilometro_MXADDR",
            "description": "Kilometer as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "Exterior_MXADDR",
            "description": "Exterior house number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "SufijoExterior_MXADDR",
            "description": "Direction that appears after the exterior house number, for example North=N, East=E, or Southwest=SW",
            "max_length": 10,
        },
        {
            "name": "Interior_MXADDR",
            "description": "Interior house number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "SufijoInterior_MXADDR",
            "description": "Direction that appears after the interior house number, for example North=N, East=E, or Southwest=SW",
            "max_length": 10,
        },
        {
            "name": "CalleInterseccion1_MXADDR",
            "description": "First part of street intersection",
            "max_length": 50,
        },
        {
            "name": "CalleInterseccion2_MXADDR",
            "description": "Second part of street intersection",
            "max_length": 50,
        },
        {
            "name": "TipoEdificacion_MXADDR",
            "description": "Standardized building descriptor",
            "max_length": 15,
        },
        {
            "name": "ValorEdificacion_MXADDR",
            "description": "Name of the building affiliated with the TipoEdificacion column",
            "max_length": 20,
        },
        {
            "name": "TipoPiso_MXADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 10,
        },
        {
            "name": "ValorPiso_MXADDR",
            "description": "Value affiliated with the TipoPiso column",
            "max_length": 10,
        },
        {
            "name": "TipoUnidad_MXADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 15,
        },
        {
            "name": "ValorUnidad_MXADDR",
            "description": "Value that is affiliated with the TipoUnidad column",
            "max_length": 10,
        },
        {
            "name": "Grupo_MXADDR",
            "description": "Land registry group as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Modulo_MXADDR",
            "description": "Land registry modulo as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Manzana_MXADDR",
            "description": "Land registry block as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Lote_MXADDR",
            "description": "Land registry lot as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Casa_MXADDR",
            "description": "House as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Asentamiento_MXADDR",
            "description": "Name of the neighborhood as determined by the rule set",
            "max_length": 60,
        },
        {
            "name": "TipoApartado_MXADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 15,
        },
        {
            "name": "ApartadoPostal_MXADDR",
            "description": "The value affiliated with the TipoApartado column",
            "max_length": 10,
        },
        {
            "name": "DireccionAdicional_MXADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 60,
        },
        {
            "name": "MatchNombreCalle_MXADDR",
            "description": "Standardized version of the NombreCalle",
            "max_length": 40,
        },
        {
            "name": "MatchNombreCalleHashKey_MXADDR",
            "description": "The first two characters of the first 5 words of MatchNombreCalle",
            "max_length": 10,
        },
        {
            "name": "MatchNombreCallePackKey_MXADDR",
            "description": "MatchNombreCalle value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumdeMatchPalabrasCalle_MXADDR",
            "description": "Number of words in MatchNombreCalle column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPalabraCalle1_MXADDR",
            "description": "First word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle2_MXADDR",
            "description": "Second word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle3_MXADDR",
            "description": "Third word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle4_MXADDR",
            "description": "Fourth word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle5_MXADDR",
            "description": "Fifth word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle1NYSIIS_MXADDR",
            "description": "Phonetic sound of the MatchPalabraCalle1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalabraCalle1RVSNDX_MXADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalabraCalle1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle1SNDX_MXADDR",
            "description": "Phonetic sound of the MatchPalabraCalle1 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle2NYSIIS_MXADDR",
            "description": "Phonetic sound of the MatchPalabraCalle2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalabraCalle2RVSNDX_MXADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalabraCalle2 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle2SNDX_MXADDR",
            "description": "Phonetic sound of the MatchPalabraCalle2 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_MXADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_MXADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_MXADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_MXADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_MXADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "MXAREA": [
        {
            "name": "CodigoPostal_MXAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 5,
        },
        {
            "name": "NombreLocalidad_MXAREA",
            "description": "Name of the locality as determined by the rule set",
            "max_length": 40,
        },
        {
            "name": "NombreEstado_MXAREA",
            "description": "Name of the state as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "CodigoPais_MXAREA",
            "description": "Country name as determined by the AREA rule set",
            "max_length": 30,
        },
        {
            "name": "NombreLocalidadNYSIIS_MXAREA",
            "description": "Phonetic sound of the NombreLocalidad column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "NombreLocalidadRVSNDX_MXAREA",
            "description": "Numerical representation of the reverse phonetic sound of the NombreLocalidad column",
            "max_length": 4,
        },
        {
            "name": "NombreLocalidadSNDX_MXAREA",
            "description": "Phonetic sound of the NombreLocalidad column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "NombreEstadoNYSIIS_MXAREA",
            "description": "Phonetic sound of the NombreEstado column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "NombreEstadoRVSNDX_MXAREA",
            "description": "Numerical representation of the reverse phonetic sound of the NombreEstado column",
            "max_length": 4,
        },
        {
            "name": "NombreEstadoSNDX_MXAREA",
            "description": "Phonetic sound of the NombreEstado column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_MXAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_MXAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_MXAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_MXAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_MXAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "MXNAME": [
        {
            "name": "TipoNombre_MXNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "CodigoGenero_MXNAME",
            "description": "The gender of the individual name that is derived from the PrefijoNombre or PrimerNombre",
            "max_length": 1,
        },
        {
            "name": "PrefijoNombre_MXNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "PrimerNombre_MXNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "SegundoNombre_MXNAME",
            "description": "Middle Name of the Individual",
            "max_length": 70,
        },
        {
            "name": "Apellido_MXNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 70,
        },
        {
            "name": "SufijoNombre_MXNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "Nombre_Adicional_MXNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchPrimerNombre_MXNAME",
            "description": "Standardized version of the PrimerNombre, for example 'WILLIAM' is the MatchPrimerNombre of the PrimerNombre 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchPrimerNombreNYSIIS_MXNAME",
            "description": "Phonetic sound of the MatchPrimerNombre column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimerNombreRVSNDX_MXNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimerNombre column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido_MXNAME",
            "description": "Apellido without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 70,
        },
        {
            "name": "MatchApellidoHashKey_MXNAME",
            "description": "The first two characters of the first 5 words of MatchApellido",
            "max_length": 10,
        },
        {
            "name": "MatchApellidoPackKey_MXNAME",
            "description": "MatchApellido value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchApellido_MXNAME",
            "description": "Number of words in MatchApellido column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchApellido1_MXNAME",
            "description": "First word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido2_MXNAME",
            "description": "Second word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido3_MXNAME",
            "description": "Third word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido4_MXNAME",
            "description": "Fourth word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido5_MXNAME",
            "description": "Fifth word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido1NYSIIS_MXNAME",
            "description": "Phonetic sound of the MatchApellido1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchApellido1RVSNDX_MXNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchApellido1 column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido2NYSIIS_MXNAME",
            "description": "Phonetic sound of the MatchApellido2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchApellido2RVSNDX_MXNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchApellido2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_MXNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_MXNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_MXNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_MXNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_MXNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "MXPREP": [
        {
            "name": "DominioNombre_MXPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "DominioDireccion_MXPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "DominioArea_MXPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_MXPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_MXPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_MXPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_MXPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_MXPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_MXPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_MXPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_MXPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_MXPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_MXPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "RUADDRL": [
        {
            "name": "RegionType_RUADDRL",
            "description": "RegionType",
            "max_length": 20,
        },
        {
            "name": "RegionValue_RUADDRL",
            "description": "RegionValue",
            "max_length": 30,
        },
        {
            "name": "DistrictType_RUADDRL",
            "description": "DistrictType",
            "max_length": 20,
        },
        {
            "name": "DistrictValue_RUADDRL",
            "description": "DistrictValue",
            "max_length": 30,
        },
        {
            "name": "CityType_RUADDRL",
            "description": "CityType",
            "max_length": 20,
        },
        {
            "name": "CityValue_RUADDRL",
            "description": "CityValue",
            "max_length": 30,
        },
        {
            "name": "CityNumericExtension_RUADDRL",
            "description": "CityNumericExtension",
            "max_length": 5,
        },
        {
            "name": "SettlementType_RUADDRL",
            "description": "SettlementType",
            "max_length": 20,
        },
        {
            "name": "SettlementValue_RUADDRL",
            "description": "SettlementValue",
            "max_length": 30,
        },
        {
            "name": "BLockType_RUADDRL",
            "description": "BLockType",
            "max_length": 20,
        },
        {
            "name": "BLockValue_RUADDRL",
            "description": "BLockValue",
            "max_length": 30,
        },
        {
            "name": "StreetPrefixType_RUADDRL",
            "description": "StreetPrefixType",
            "max_length": 20,
        },
        {
            "name": "StreetName_RUADDRL",
            "description": "StreetName",
            "max_length": 30,
        },
        {
            "name": "StreetSuffixType_RUADDRL",
            "description": "StreetSuffixType",
            "max_length": 20,
        },
        {
            "name": "BuildingType_RUADDRL",
            "description": "BuildingType",
            "max_length": 20,
        },
        {
            "name": "BuildingValue_RUADDRL",
            "description": "BuildingValue",
            "max_length": 30,
        },
        {
            "name": "HouseType1_RUADDRL",
            "description": "HouseType1;",
            "max_length": 20,
        },
        {
            "name": "HouseValue1_RUADDRL",
            "description": "HouseValue1",
            "max_length": 20,
        },
        {
            "name": "HouseType2_RUADDRL",
            "description": "HouseType2;",
            "max_length": 20,
        },
        {
            "name": "HouseValue2_RUADDRL",
            "description": "HouseValue2",
            "max_length": 10,
        },
        {
            "name": "FloorType_RUADDRL",
            "description": "FloorType",
            "max_length": 10,
        },
        {
            "name": "FLoorValue_RUADDRL",
            "description": "FLoorValue",
            "max_length": 10,
        },
        {
            "name": "UnitType_RUADDRL",
            "description": "UnitType",
            "max_length": 10,
        },
        {
            "name": "UnitValue_RUADDRL",
            "description": "UnitValue",
            "max_length": 10,
        },
        {
            "name": "PostOfficeBoxType_RUADDRL",
            "description": "PostOfficeBoxType",
            "max_length": 10,
        },
        {
            "name": "PostOfficeBoxValue_RUADDRL",
            "description": "PostOfficeBoxValue",
            "max_length": 10,
        },
        {
            "name": "PostalCode_RUADDRL",
            "description": "PostalCode",
            "max_length": 6,
        },
        {"name": "Country_RUADDRL", "description": "Country", "max_length": 20},
        {"name": "OrgName_RUADDRL", "description": "OrgName", "max_length": 30},
        {
            "name": "DistrictTransliterated_RUADDRL",
            "description": "DistrictTransliterated",
            "max_length": 30,
        },
        {
            "name": "SettlementTransliterated_RUADDRL",
            "description": "SettlementTransliterated",
            "max_length": 30,
        },
        {
            "name": "CityTransliterated_RUADDRL",
            "description": "CityTransliterated",
            "max_length": 30,
        },
        {
            "name": "StreetTransliterated_RUADDRL",
            "description": "StreetTransliterated",
            "max_length": 30,
        },
        {
            "name": "NYSIISDistrict_RUADDRL",
            "description": "NYSIISDistrict",
            "max_length": 8,
        },
        {
            "name": "NYSIISSettlement_RUADDRL",
            "description": "NYSIISSettlement",
            "max_length": 8,
        },
        {
            "name": "NYSIISCity_RUADDRL",
            "description": "NYSIISCity",
            "max_length": 8,
        },
        {
            "name": "NYSIISStreet_RUADDRL",
            "description": "NYSIISStreet",
            "max_length": 8,
        },
        {
            "name": "SoundexStreet_RUADDRL",
            "description": "SoundexStreet",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_RUADDRL",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_RUADDRL",
            "description": "UnhandledData",
            "max_length": 100,
        },
        {
            "name": "InputPattern_RUADDRL",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_RUADDRL",
            "description": "ExceptionData",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_RUADDRL",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
        {
            "name": "Transliterator_RUADDRL",
            "description": "Transliterator",
            "max_length": 35,
        },
    ],
    "RUNAMEL": [
        {
            "name": "NameType_RUNAMEL",
            "description": "NameType",
            "max_length": 1,
        },
        {
            "name": "GenderCode_RUNAMEL",
            "description": "GenderCode",
            "max_length": 1,
        },
        {
            "name": "OrganizationType_RUNAMEL",
            "description": "OrganizationType",
            "max_length": 20,
        },
        {
            "name": "NamePrefixOrganizationSubType_RUNAMEL",
            "description": "NamePrefixOrganizationSubType",
            "max_length": 40,
        },
        {
            "name": "FirstName_RUNAMEL",
            "description": "FirstName",
            "max_length": 25,
        },
        {
            "name": "MiddleName_RUNAMEL",
            "description": "MiddleName",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_RUNAMEL",
            "description": "PrimaryName",
            "max_length": 100,
        },
        {
            "name": "NameGeneration_RUNAMEL",
            "description": "NameGeneration",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_RUNAMEL",
            "description": "NameSuffix",
            "max_length": 20,
        },
        {
            "name": "AdditionalNameInformation_RUNAMEL",
            "description": "AdditionalNameInformation",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_RUNAMEL",
            "description": "MatchFirstName",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameTransliterated_RUNAMEL",
            "description": "MatchFirstNameTransliterated",
            "max_length": 25,
        },
        {
            "name": "NYSIISofMatchFirstName_RUNAMEL",
            "description": "NYSIISofMatchFirstName",
            "max_length": 8,
        },
        {
            "name": "RSoundexofMatchFirstName_RUNAMEL",
            "description": "RSoundexofMatchFirstName",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_RUNAMEL",
            "description": "MatchPrimaryName",
            "max_length": 50,
        },
        {
            "name": "HashKeyofMatchPrimaryName_RUNAMEL",
            "description": "HashKeyofMatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "PackedKeyofMatchPrimaryName_RUNAMEL",
            "description": "PackedKeyofMatchPrimaryName",
            "max_length": 25,
        },
        {
            "name": "NumberofMatchPrimaryWords_RUNAMEL",
            "description": "NumberofMatchPrimaryWords",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_RUNAMEL",
            "description": "MatchPrimaryWord1",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1Transliterated_RUNAMEL",
            "description": "MatchPrimaryWord1Transliterated",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_RUNAMEL",
            "description": "MatchPrimaryWord2",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2Transliterated_RUNAMEL",
            "description": "MatchPrimaryWord2Transliterated",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_RUNAMEL",
            "description": "MatchPrimaryWord3",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_RUNAMEL",
            "description": "MatchPrimaryWord4",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_RUNAMEL",
            "description": "MatchPrimaryWord5",
            "max_length": 15,
        },
        {
            "name": "NYSIISofMatchPrimaryWord1_RUNAMEL",
            "description": "NYSIISofMatchPrimaryWord1",
            "max_length": 8,
        },
        {
            "name": "RSoundexofMatchPrimaryWord1_RUNAMEL",
            "description": "RSoundexofMatchPrimaryWord1",
            "max_length": 4,
        },
        {
            "name": "NYSIISofMatchPrimaryWord2_RUNAMEL",
            "description": "NYSIISofMatchPrimaryWord2",
            "max_length": 8,
        },
        {
            "name": "RSoundexofMatchPrimaryWord2_RUNAMEL",
            "description": "RSoundexofMatchPrimaryWord2",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_RUNAMEL",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_RUNAMEL",
            "description": "UnhandledData",
            "max_length": 100,
        },
        {
            "name": "InputPattern_RUNAMEL",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_RUNAMEL",
            "description": "ExceptionData",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_RUNAMEL",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "CAADDR": [
        {
            "name": "CivicNumber_CAADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "CivicNumberSuffix_CAADDR",
            "description": "Suffix of the house number as determined by the rule set, for example 'A' is the suffix in 123A Main St",
            "max_length": 10,
        },
        {
            "name": "StreetPrefixDirectional_CAADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "StreetPrefixType_CAADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 7,
        },
        {
            "name": "StreetName_CAADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "StreetSuffixType_CAADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 7,
        },
        {
            "name": "StreetSuffixQualifier_CAADDR",
            "description": "An adjective of the street name that appears after the street name, for example 'Old' or 'New'",
            "max_length": 6,
        },
        {
            "name": "StreetSuffixDirectional_CAADDR",
            "description": "Street direction that appears after the street name, for example North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "RuralRouteType_CAADDR",
            "description": "Standardized rural route descriptor, typically 'RR'",
            "max_length": 3,
        },
        {
            "name": "RuralRouteValue_CAADDR",
            "description": "Value affiliated with the RuralRouteType column",
            "max_length": 10,
        },
        {
            "name": "BoxType_CAADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 7,
        },
        {
            "name": "BoxValue_CAADDR",
            "description": "The value affiliated with the BoxType column",
            "max_length": 10,
        },
        {
            "name": "GeneralDelivery_CAADDR",
            "description": "General Delivery as determined by the rule set, typically 'GD'",
            "max_length": 3,
        },
        {
            "name": "DelInstallationType_CAADDR",
            "description": "Standardized delivery installation descriptor",
            "max_length": 5,
        },
        {
            "name": "DelInstallationName_CAADDR",
            "description": "Name affiliated with the DelInstallationType column",
            "max_length": 15,
        },
        {
            "name": "SiteType_CAADDR",
            "description": "Standardized site descriptor, typically 'SITE'",
            "max_length": 5,
        },
        {
            "name": "SiteValue_CAADDR",
            "description": "Value affiliated with the SiteType column",
            "max_length": 10,
        },
        {
            "name": "CompType_CAADDR",
            "description": "Standardized compartment descriptor, typically 'COMP'",
            "max_length": 5,
        },
        {
            "name": "CompValue_CAADDR",
            "description": "Value affiliated with the CompType column",
            "max_length": 10,
        },
        {
            "name": "LotType_CAADDR",
            "description": "Standardized lot descriptor, typically 'LOT'",
            "max_length": 4,
        },
        {
            "name": "LotValue_CAADDR",
            "description": "Value affiliated with the LotType column",
            "max_length": 10,
        },
        {
            "name": "ConcType_CAADDR",
            "description": "Standardized concession descriptor, typically 'CONC'",
            "max_length": 5,
        },
        {
            "name": "ConcValue_CAADDR",
            "description": "Value affiliated with the ConcType column",
            "max_length": 10,
        },
        {
            "name": "FloorType_CAADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 6,
        },
        {
            "name": "FloorValue_CAADDR",
            "description": "Value affiliated with the FloorType column",
            "max_length": 10,
        },
        {
            "name": "UnitType_CAADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 7,
        },
        {
            "name": "UnitValue_CAADDR",
            "description": "Value that is affiliated with the UnitType column",
            "max_length": 10,
        },
        {
            "name": "MultiUnitType_CAADDR",
            "description": "Additional unit descriptor such as Apt, Unit, or Suite populated only if multiple units are found",
            "max_length": 7,
        },
        {
            "name": "MultiUnitValue_CAADDR",
            "description": "Value affiliated with the MultiUnitType column",
            "max_length": 10,
        },
        {
            "name": "BuildingName_CAADDR",
            "description": "Name of the building as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "AdditionalAddress_CAADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 30,
        },
        {
            "name": "AddressType_CAADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "StreetNameNYSIIS_CAADDR",
            "description": "Phonetic sound of the StreetName column",
            "max_length": 8,
        },
        {
            "name": "StreetNameRVSNDX_CAADDR",
            "description": "Numerical representation of the reverse phonetic sound of the StreetName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_CAADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CAADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_CAADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CAADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_CAADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "CAAREA": [
        {
            "name": "MunicipalityName_CAAREA",
            "description": "Name of the municipality as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "ProvinceAbbreviation_CAAREA",
            "description": "Two letter province abbreviation",
            "max_length": 3,
        },
        {
            "name": "PostalCode_CAAREA",
            "description": "Post Code as determined by the rule set",
            "max_length": 7,
        },
        {
            "name": "CountryCode_CAAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 3,
        },
        {
            "name": "MunicipalityNameNYSIIS_CAAREA",
            "description": "Phonetic sound of the MunicipalityName column",
            "max_length": 8,
        },
        {
            "name": "MunicipalityNameRVSNDX_CAAREA",
            "description": "Numerical representation of the reverse phonetic sound of the MunicipalityName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_CAAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CAAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_CAAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CAAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_CAAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "CANAME": [
        {
            "name": "NameType_CANAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_CANAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_CANAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_CANAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_CANAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_CANAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_CANAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_CANAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_CANAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_CANAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_CANAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_CANAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_CANAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_CANAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_CANAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_CANAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_CANAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_CANAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_CANAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_CANAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_CANAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_CANAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_CANAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_CANAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_CANAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_CANAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CANAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_CANAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CANAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_CANAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "CAPREP": [
        {
            "name": "NameDomain_CAPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_CAPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_CAPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_CAPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_CAPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_CAPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_CAPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_CAPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_CAPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_CAPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_CAPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_CAPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_CAPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "USADDR": [
        {
            "name": "HouseNumber_USADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "HouseNumberSuffix_USADDR",
            "description": "Suffix of the house number as determined by the rule set, for example 'A' is the suffix in 123A Main St",
            "max_length": 10,
        },
        {
            "name": "StreetPrefixDirectional_USADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "StreetPrefixType_USADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 20,
        },
        {
            "name": "StreetName_USADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "StreetSuffixType_USADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 5,
        },
        {
            "name": "StreetSuffixQualifier_USADDR",
            "description": "An adjective of the street name that appears after the street name, for example 'Old' or 'New'",
            "max_length": 5,
        },
        {
            "name": "StreetSuffixDirectional_USADDR",
            "description": "Street direction that appears after the street name, for example North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "RuralRouteType_USADDR",
            "description": "Standardized rural route descriptor, typically 'RR'",
            "max_length": 3,
        },
        {
            "name": "RuralRouteValue_USADDR",
            "description": "Value affiliated with the RuralRouteType column",
            "max_length": 10,
        },
        {
            "name": "BoxType_USADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 7,
        },
        {
            "name": "BoxValue_USADDR",
            "description": "The value affiliated with the BoxType column",
            "max_length": 10,
        },
        {
            "name": "FloorType_USADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 5,
        },
        {
            "name": "FloorValue_USADDR",
            "description": "Value affiliated with the FloorType column",
            "max_length": 10,
        },
        {
            "name": "UnitType_USADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 5,
        },
        {
            "name": "UnitValue_USADDR",
            "description": "Value that is affiliated with the UnitType column",
            "max_length": 10,
        },
        {
            "name": "MultiUnitType_USADDR",
            "description": "Additional unit descriptor such as Apt, Unit, or Suite populated only if multiple units are found",
            "max_length": 5,
        },
        {
            "name": "MultiUnitValue_USADDR",
            "description": "Value affiliated with the MultiUnitType column",
            "max_length": 10,
        },
        {
            "name": "BuildingName_USADDR",
            "description": "Name of the building as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "AdditionalAddress_USADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "AddressType_USADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "StreetNameNYSIIS_USADDR",
            "description": "Phonetic sound of the StreetName column",
            "max_length": 8,
        },
        {
            "name": "StreetNameRVSNDX_USADDR",
            "description": "Numerical representation of the reverse phonetic sound of the StreetName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_USADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_USADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_USADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_USADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_USADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "USAREA": [
        {
            "name": "CityName_USAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "StateAbbreviation_USAREA",
            "description": "Two letter state abbreviation",
            "max_length": 3,
        },
        {
            "name": "ZipCode_USAREA",
            "description": "First 5 digits of the US ZIP code",
            "max_length": 5,
        },
        {
            "name": "Zip4AddonCode_USAREA",
            "description": "Optional field that contains the additional ZIP + 4 code for the US ZIP code",
            "max_length": 4,
        },
        {
            "name": "CountryCode_USAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 2,
        },
        {
            "name": "CityNameNYSIIS_USAREA",
            "description": "Phonetic sound of the CityName column",
            "max_length": 8,
        },
        {
            "name": "CityNameRVSNDX_USAREA",
            "description": "Numerical representation of the reverse phonetic sound of the CityName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_USAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_USAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_USAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_USAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_USAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "USNAME": [
        {
            "name": "NameType_USNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_USNAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_USNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_USNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_USNAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_USNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_USNAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_USNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_USNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_USNAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_USNAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_USNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_USNAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_USNAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_USNAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_USNAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_USNAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_USNAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_USNAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_USNAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_USNAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_USNAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_USNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_USNAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_USNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_USNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_USNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_USNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_USNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_USNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "USPREP": [
        {
            "name": "NameDomain_USPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_USPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_USPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_USPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_USPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_USPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_USPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_USPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_USPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_USPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_USPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_USPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_USPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "USTAXID": [
        {
            "name": "ValidFlag_USTAXID",
            "description": "ValidFlag",
            "max_length": 1,
        },
        {"name": "TaxID_USTAXID", "description": "TaxID", "max_length": 10},
        {
            "name": "UnhandledPattern_USTAXID",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_USTAXID",
            "description": "UnhandledData",
            "max_length": 50,
        },
        {
            "name": "InputPattern_USTAXID",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_USTAXID",
            "description": "ExceptionData",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_USTAXID",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "ARADDR": [
        {
            "name": "TipoDireccion_ARADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "TipoCalle_ARADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 20,
        },
        {
            "name": "Calle_ARADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "Kilometro_ARADDR",
            "description": "Kilometer as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Altura_ARADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "SufijoAltura_ARADDR",
            "description": "Street direction that appears after the street name, for example North=N, East=E, or Southwest=SW",
            "max_length": 10,
        },
        {
            "name": "AlturaAdicional_ARADDR",
            "description": "Street components that cannot be parsed into existing columns",
            "max_length": 10,
        },
        {
            "name": "CalleInterseccion1_ARADDR",
            "description": "First part of street intersection",
            "max_length": 50,
        },
        {
            "name": "CalleInterseccion2_ARADDR",
            "description": "Second part of street intersection",
            "max_length": 50,
        },
        {
            "name": "TipoEdificacion_ARADDR",
            "description": "Standardized building descriptor",
            "max_length": 15,
        },
        {
            "name": "ValorEdificacion_ARADDR",
            "description": "Name of the building affiliated with the TipoEdificacion column",
            "max_length": 20,
        },
        {
            "name": "TipoPiso_ARADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 10,
        },
        {
            "name": "ValorPiso_ARADDR",
            "description": "Value affiliated with the TipoPiso column",
            "max_length": 10,
        },
        {
            "name": "TipoUnidad_ARADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 15,
        },
        {
            "name": "ValorUnidad_ARADDR",
            "description": "Value that is affiliated with the TipoUnidad column",
            "max_length": 10,
        },
        {
            "name": "BarrioZona_ARADDR",
            "description": "Name of the neighborhood as determined by the rule set",
            "max_length": 40,
        },
        {
            "name": "Circunscripcion_ARADDR",
            "description": "District or set of sections as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Seccion_ARADDR",
            "description": "Section as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Manzana_ARADDR",
            "description": "Land registry block as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Casa_ARADDR",
            "description": "House as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "LoteParcela_ARADDR",
            "description": "Land registry lot parcel as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Sector_ARADDR",
            "description": "Sector as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "UnidadFuncional_ARADDR",
            "description": "Land registry functional unit as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "TipoCasilla_ARADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 15,
        },
        {
            "name": "CasillaCorreo_ARADDR",
            "description": "The value affiliated with the TipoCasilla column",
            "max_length": 5,
        },
        {
            "name": "SufijoCasillaCorreo_ARADDR",
            "description": "Suffix of the Post Office Box as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "DireccionAdicional_ARADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 60,
        },
        {
            "name": "MatchNombreCalle_ARADDR",
            "description": "Standardized version of the NombreCalle",
            "max_length": 25,
        },
        {
            "name": "MatchNombreCalleHashKey_ARADDR",
            "description": "The first two characters of the first 5 words of MatchNombreCalle",
            "max_length": 10,
        },
        {
            "name": "MatchNombreCallePackKey_ARADDR",
            "description": "MatchNombreCalle value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumdeMatchPalabrasCalle_ARADDR",
            "description": "Number of words in MatchNombreCalle column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPalabraCalle1_ARADDR",
            "description": "First word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle2_ARADDR",
            "description": "Second word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle3_ARADDR",
            "description": "Third word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle4_ARADDR",
            "description": "Fourth word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle5_ARADDR",
            "description": "Fifth word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle1NYSIIS_ARADDR",
            "description": "Phonetic sound of the MatchPalabraCalle1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalabraCalle1RVSNDX_ARADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalabraCalle1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle1SNDX_ARADDR",
            "description": "Phonetic sound of the MatchPalabraCalle1 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle2NYSIIS_ARADDR",
            "description": "Phonetic sound of the MatchPalabraCalle2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalabraCalle2RVSNDX_ARADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalabraCalle2 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle2SNDX_ARADDR",
            "description": "Phonetic sound of the MatchPalabraCalle2 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ARADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ARADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_ARADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ARADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ARADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ARAREA": [
        {
            "name": "CodigoPostal_ARAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 4,
        },
        {
            "name": "CPA_ARAREA",
            "description": "CPA as determined by the rule set",
            "max_length": 8,
        },
        {
            "name": "NombreCiudad_ARAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "NombreProvincia_ARAREA",
            "description": "Name of the province as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "CodigoPais_ARAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 3,
        },
        {
            "name": "NombreCiudadNYSIIS_ARAREA",
            "description": "Phonetic sound of the NombreCiudad column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "NombreCiudadRVSNDX_ARAREA",
            "description": "Numerical representation of the reverse phonetic sound of the NombreCiudad column",
            "max_length": 4,
        },
        {
            "name": "NombreCiudadSNDX_ARAREA",
            "description": "Phonetic sound of the NombreCiudad column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "NombreProvinciaNYSIIS_ARAREA",
            "description": "Phonetic sound of the NombreCiudad column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "NombreProvinciaRVSNDX_ARAREA",
            "description": "Numerical representation of the reverse phonetic sound of the NombreCiudad column",
            "max_length": 4,
        },
        {
            "name": "NombreProvinciaSNDX_ARAREA",
            "description": "Phonetic sound of the NombreCiudad column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ARAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ARAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_ARAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ARAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ARAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ARNAME": [
        {
            "name": "TipoNombre_ARNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "CodigoGenero_ARNAME",
            "description": "The gender of the individual name that is derived from the PrefijoNombre or PrimerNombre",
            "max_length": 1,
        },
        {
            "name": "PrefijoNombre_ARNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "PrimerNombre_ARNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "SegundoNombre_ARNAME",
            "description": "Middle Name of the Individual",
            "max_length": 70,
        },
        {
            "name": "Apellido_ARNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 70,
        },
        {
            "name": "SufijoNombre_ARNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "NombreAdicional_ARNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchPrimerNombre_ARNAME",
            "description": "Standardized version of the PrimerNombre, for example 'WILLIAM' is the MatchPrimerNombre of the PrimerNombre 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchPrimerNombreNYSIIS_ARNAME",
            "description": "Phonetic sound of the MatchPrimerNombre column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimerNombreRVSNDX_ARNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimerNombre column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido_ARNAME",
            "description": "Apellido without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 70,
        },
        {
            "name": "MatchApellidoHashKey_ARNAME",
            "description": "The first two characters of the first 5 words of MatchApellido",
            "max_length": 10,
        },
        {
            "name": "MatchApellidoPackKey_ARNAME",
            "description": "MatchApellido value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchApellido_ARNAME",
            "description": "Number of words in MatchApellido column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchApellido1_ARNAME",
            "description": "First word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido2_ARNAME",
            "description": "Second word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido3_ARNAME",
            "description": "Third word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido4_ARNAME",
            "description": "Fourth word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido5_ARNAME",
            "description": "Fifth word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido1NYSIIS_ARNAME",
            "description": "Phonetic sound of the MatchApellido1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchApellido1RVSNDX_ARNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchApellido1 column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido1SNDX_ARNAME",
            "description": "Phonetic sound of the MatchApellido1 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "MatchApellido2NYSIIS_ARNAME",
            "description": "Phonetic sound of the MatchApellido2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchApellido2RVSNDX_ARNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchApellido2 column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido2SNDX_ARNAME",
            "description": "Phonetic sound of the MatchApellido2 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ARNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ARNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_ARNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ARNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ARNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ARPREP": [
        {
            "name": "DominioNombre_ARPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "DominioDireccion_ARPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "DominioArea_ARPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_ARPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_ARPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_ARPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_ARPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_ARPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_ARPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_ARPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_ARPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_ARPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_ARPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "BRADDR": [
        {
            "name": "TipoLogradouro_BRADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 15,
        },
        {
            "name": "Logradouro_BRADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 100,
        },
        {
            "name": "Numero_BRADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "Complemento_BRADDR",
            "description": "Secondary street name as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "Lotes_BRADDR",
            "description": "Land registry lot as determined by the rule set",
            "max_length": 20,
        },
        {
            "name": "Edificio_BRADDR",
            "description": "Name of the building as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "TipoAndar_BRADDR",
            "description": "Standardized floor descriptor, typically 'ANDAR'",
            "max_length": 10,
        },
        {
            "name": "Andar_BRADDR",
            "description": "Value affiliated with the TipoAndar column",
            "max_length": 10,
        },
        {
            "name": "TipoUnidade_BRADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 10,
        },
        {
            "name": "Unidade_BRADDR",
            "description": "Value that is affiliated with the TipoUnidade column",
            "max_length": 10,
        },
        {
            "name": "TipoCaixaPostal_BRADDR",
            "description": "Standardized Post Office Box descriptor, typically 'CAIXA POSTAL'",
            "max_length": 12,
        },
        {
            "name": "CaixaPostal_BRADDR",
            "description": "The value affiliated with the TipoCaixaPostal column",
            "max_length": 8,
        },
        {
            "name": "Bairro_BRADDR",
            "description": "Name of the neighborhood as determined by the rule set",
            "max_length": 100,
        },
        {
            "name": "AddressType_BRADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "StreetNYSIIS_BRADDR",
            "description": "Phonetic sound of the Logradouro column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "StreetRVSNDX_BRADDR",
            "description": "Numerical representation of the reverse phonetic sound of the Logradouro column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_BRADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_BRADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_BRADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_BRADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_BRADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "BRAREA": [
        {
            "name": "Cidade_BRAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 40,
        },
        {
            "name": "UF_BRAREA",
            "description": "Two letter state abbreviation",
            "max_length": 2,
        },
        {
            "name": "CEP_BRAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 8,
        },
        {
            "name": "Pa\u00eds_BRAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 2,
        },
        {
            "name": "CityNYSIIS_BRAREA",
            "description": "Phonetic sound of the Cidade column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "CityRVSNDX_BRAREA",
            "description": "Numerical representation of the reverse phonetic sound of the Cidade column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_BRAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_BRAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_BRAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_BRAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_BRAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "BRNAME": [
        {
            "name": "TipoNome_BRNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "CodigoGenero_BRNAME",
            "description": "The gender of the individual name that is derived from the PrefixoNome or PrimeiroNome",
            "max_length": 1,
        },
        {
            "name": "PrefixoNome_BRNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "PrimeiroNome_BRNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "NomeDoMeio_BRNAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "NomePrincipal_BRNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 70,
        },
        {
            "name": "NomeDeFamilia_BRNAME",
            "description": "Family name of an individual",
            "max_length": 10,
        },
        {
            "name": "SufixoNome_BRNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "Informa\u00e7\u00f5esAdicionais_BRNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchPrimeiroNome_BRNAME",
            "description": "Standardized version of the PrimeiroNome, for example 'WILLIAM' is the MatchPrimeiroNome of the PrimeiroNome 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchPrimeiroNomeNYSIIS_BRNAME",
            "description": "Phonetic sound of the MatchPrimeiroNome column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimeiroNomeRVSNDX_BRNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimeiroNome column",
            "max_length": 4,
        },
        {
            "name": "MatchNomePrincipal_BRNAME",
            "description": "NomePrincipal without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchNomePrincipalHashKey_BRNAME",
            "description": "The first two characters of the first 5 words of MatchNomePrincipal",
            "max_length": 10,
        },
        {
            "name": "MatchNomePrincipalPackKey_BRNAME",
            "description": "MatchNomePrincipal value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumdeMatchPalavraPrincipal_BRNAME",
            "description": "Number of words in MatchNomePrincipal column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPalavraPrincipal1_BRNAME",
            "description": "First word of MatchNomePrincipal column",
            "max_length": 15,
        },
        {
            "name": "MatchPalavraPrincipal2_BRNAME",
            "description": "Second word of MatchNomePrincipal column",
            "max_length": 15,
        },
        {
            "name": "MatchPalavraPrincipal1NYSIIS_BRNAME",
            "description": "Phonetic sound of the MatchPalavraPrincipal1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalavraPrincipal1RVSNDX_BRNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalavraPrincipal1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalavraPrincipal2NYSIIS_BRNAME",
            "description": "Phonetic sound of the MatchPalavraPrincipal2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalavraPrincipal2RVSNDX_BRNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalavraPrincipal2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_BRNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_BRNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_BRNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_BRNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_BRNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "BRPREP": [
        {
            "name": "Nome_BRPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Endere\u00e7o_BRPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Area_BRPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Teste1_BRPREP",
            "description": "Placeholder for additional information you want to standardize",
            "max_length": 100,
        },
        {
            "name": "Teste2_BRPREP",
            "description": "Placeholder for additional information you want to standardize",
            "max_length": 100,
        },
        {
            "name": "Teste3_BRPREP",
            "description": "Placeholder for additional information you want to standardize",
            "max_length": 100,
        },
        {
            "name": "Teste4_BRPREP",
            "description": "Placeholder for additional information you want to standardize",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_BRPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_BRPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_BRPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_BRPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_BRPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_BRPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_BRPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_BRPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_BRPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_BRPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "CLADDR": [
        {
            "name": "TipoDireccion_CLADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "TipoCalle_CLADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 20,
        },
        {
            "name": "Calle_CLADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "Kilometro_CLADDR",
            "description": "Kilometer as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Altura_CLADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "AlturaAdicional_CLADDR",
            "description": "Street components that cannot be parsed into existing columns",
            "max_length": 10,
        },
        {
            "name": "SufijoAltura_CLADDR",
            "description": "Street direction that appears after the street name, for example North=N, East=E, or Southwest=SW",
            "max_length": 10,
        },
        {
            "name": "CalleInterseccion1_CLADDR",
            "description": "First part of street intersection",
            "max_length": 50,
        },
        {
            "name": "CalleInterseccion2_CLADDR",
            "description": "Second part of street intersection",
            "max_length": 50,
        },
        {
            "name": "TipoEdificacion_CLADDR",
            "description": "Standardized building descriptor",
            "max_length": 15,
        },
        {
            "name": "ValorEdificacion_CLADDR",
            "description": "Name of the building affiliated with the TipoEdificacion column",
            "max_length": 35,
        },
        {
            "name": "TipoPiso_CLADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 10,
        },
        {
            "name": "ValorPiso_CLADDR",
            "description": "Value affiliated with the TipoPiso column",
            "max_length": 10,
        },
        {
            "name": "TipoUnidad_CLADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 15,
        },
        {
            "name": "ValorUnidad_CLADDR",
            "description": "Value that is affiliated with the TipoUnidad column",
            "max_length": 10,
        },
        {
            "name": "Zona_CLADDR",
            "description": "Name of the neighborhood as determined by the rule set",
            "max_length": 40,
        },
        {
            "name": "Manzana_CLADDR",
            "description": "Land registry block as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Casa_CLADDR",
            "description": "House as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "LoteParcela_CLADDR",
            "description": "Land registry lot parcel as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "Sector_CLADDR",
            "description": "Sector as determined by the rule set",
            "max_length": 40,
        },
        {
            "name": "TipoCasilla_CLADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 15,
        },
        {
            "name": "CasillaCorreo_CLADDR",
            "description": "The value affiliated with the TipoCasilla column",
            "max_length": 5,
        },
        {
            "name": "SufijoCasillaCorreo_CLADDR",
            "description": "Suffix of the Post Office Box as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "DireccionAdicional_CLADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 60,
        },
        {
            "name": "MatchNombreCalle_CLADDR",
            "description": "Standardized version of the NombreCalle",
            "max_length": 35,
        },
        {
            "name": "MatchNombreCalleHashKey_CLADDR",
            "description": "The first two characters of the first 5 words of MatchNombreCalle",
            "max_length": 10,
        },
        {
            "name": "MatchNombreCallePackKey_CLADDR",
            "description": "MatchNombreCalle value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumdeMatchPalabrasCalle_CLADDR",
            "description": "Number of words in MatchNombreCalle column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPalabraCalle1_CLADDR",
            "description": "First word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle2_CLADDR",
            "description": "Second word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle3_CLADDR",
            "description": "Third word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle4_CLADDR",
            "description": "Fourth word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle5_CLADDR",
            "description": "Fifth word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle1NYSIIS_CLADDR",
            "description": "Phonetic sound of the MatchPalabraCalle1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalabraCalle1RVSNDX_CLADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalabraCalle1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle1SNDX_CLADDR",
            "description": "Phonetic sound of the MatchPalabraCalle1 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle2NYSIIS_CLADDR",
            "description": "Phonetic sound of the MatchPalabraCalle2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalabraCalle2RVSNDX_CLADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalabraCalle2 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle2SNDX_CLADDR",
            "description": "Phonetic sound of the MatchPalabraCalle2 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_CLADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CLADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_CLADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CLADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_CLADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "CLAREA": [
        {
            "name": "Comuna_CLAREA",
            "description": "Name of the neighborhood as determined by the rule set",
            "max_length": 20,
        },
        {
            "name": "Ciudad_CLAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "Region_CLAREA",
            "description": "Name of the region as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "CodigoPais_CLAREA",
            "description": "Country name as determined by the AREA rule set",
            "max_length": 30,
        },
        {
            "name": "CodigoPostal_CLAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "ComunaNYSIIS_CLAREA",
            "description": "Phonetic sound of the Comuna column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "ComunaRVSNDX_CLAREA",
            "description": "Numerical representation of the reverse phonetic sound of the Comuna column",
            "max_length": 4,
        },
        {
            "name": "ComunaSNDX_CLAREA",
            "description": "Phonetic sound of the Comuna column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "CiudadNYSIIS_CLAREA",
            "description": "Phonetic sound of the Ciudad column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "CiudadRVSNDX_CLAREA",
            "description": "Numerical representation of the reverse phonetic sound of the Ciudad column",
            "max_length": 4,
        },
        {
            "name": "CiudadSNDX_CLAREA",
            "description": "Phonetic sound of the Ciudad column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "RegionNYSIIS_CLAREA",
            "description": "Phonetic sound of the Region column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "RegionRVSNDX_CLAREA",
            "description": "Numerical representation of the reverse phonetic sound of the Region column",
            "max_length": 4,
        },
        {
            "name": "RegionSNDX_CLAREA",
            "description": "Phonetic sound of the Region column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_CLAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CLAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_CLAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CLAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_CLAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "CLNAME": [
        {
            "name": "TipoNombre_CLNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "CodigoGenero_CLNAME",
            "description": "The gender of the individual name that is derived from the PrefijoNombre or PrimerNombre",
            "max_length": 1,
        },
        {
            "name": "PrefijoNombre_CLNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "PrimerNombre_CLNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "SegundoNombre_CLNAME",
            "description": "Middle Name of the Individual",
            "max_length": 70,
        },
        {
            "name": "Apellido_CLNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 70,
        },
        {
            "name": "Nombre_Adicional_CLNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "SufijoNombre_CLNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "MatchPrimerNombre_CLNAME",
            "description": "Standardized version of the PrimerNombre, for example 'WILLIAM' is the MatchPrimerNombre of the PrimerNombre 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchPrimerNombreNYSIIS_CLNAME",
            "description": "Phonetic sound of the MatchPrimerNombre column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimerNombreRVSNDX_CLNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimerNombre column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido_CLNAME",
            "description": "Apellido without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 70,
        },
        {
            "name": "MatchApellidoHashKey_CLNAME",
            "description": "The first two characters of the first 5 words of MatchApellido",
            "max_length": 10,
        },
        {
            "name": "MatchApellidoPackKey_CLNAME",
            "description": "MatchApellido value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchApellido_CLNAME",
            "description": "Number of words in MatchApellido column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchApellido1_CLNAME",
            "description": "First word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido2_CLNAME",
            "description": "Second word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido3_CLNAME",
            "description": "Third word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido4_CLNAME",
            "description": "Fourth word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido5_CLNAME",
            "description": "Fifth word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido1NYSIIS_CLNAME",
            "description": "Phonetic sound of the MatchApellido1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchApellido1RVSNDX_CLNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchApellido1 column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido1SNDX_CLNAME",
            "description": "Phonetic sound of the MatchApellido1 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "MatchApellido2NYSIIS_CLNAME",
            "description": "Phonetic sound of the MatchApellido2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchApellido2RVSNDX_CLNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchApellido2 column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido2SNDX_CLNAME",
            "description": "Phonetic sound of the MatchApellido2 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_CLNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_CLNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_CLNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_CLNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_CLNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "CLPREP": [
        {
            "name": "DominioNombre_CLPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "DominioDireccion_CLPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "DominioArea_CLPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_CLPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_CLPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_CLPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_CLPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_CLPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_CLPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_CLPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_CLPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_CLPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_CLPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "PEADDR": [
        {
            "name": "TipoDireccion_PEADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "TipoCalle_PEADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 20,
        },
        {
            "name": "Calle_PEADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "Numero_PEADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "Kilometro_PEADDR",
            "description": "Kilometer as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "NumeroAdicional_PEADDR",
            "description": "Number that cannot be parsed into existing columns",
            "max_length": 10,
        },
        {
            "name": "Cuadra_PEADDR",
            "description": "Land registry block as determined by the rule set",
            "max_length": 60,
        },
        {
            "name": "Interno_PEADDR",
            "description": "Interno as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "CalleInterseccion1_PEADDR",
            "description": "First part of street intersection",
            "max_length": 50,
        },
        {
            "name": "CalleInterseccion2_PEADDR",
            "description": "Second part of street intersection",
            "max_length": 50,
        },
        {
            "name": "TipoEdificacion_PEADDR",
            "description": "Standardized building descriptor",
            "max_length": 15,
        },
        {
            "name": "ValorEdificacion_PEADDR",
            "description": "Name of the building affiliated with the TipoEdificacion column",
            "max_length": 20,
        },
        {
            "name": "TipoPiso_PEADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 10,
        },
        {
            "name": "ValorPiso_PEADDR",
            "description": "Value affiliated with the TipoPiso column",
            "max_length": 10,
        },
        {
            "name": "TipoUnidad_PEADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 15,
        },
        {
            "name": "ValorUnidad_PEADDR",
            "description": "Value that is affiliated with the TipoUnidad column",
            "max_length": 10,
        },
        {
            "name": "Sector_PEADDR",
            "description": "Sector as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Grupo_PEADDR",
            "description": "Land registry group as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Parcela_PEADDR",
            "description": "Land registry plot as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Manzana_PEADDR",
            "description": "Land registry acre as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Lote_PEADDR",
            "description": "Land registry lot as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "Casa_PEADDR",
            "description": "House as determined by the rule set",
            "max_length": 15,
        },
        {
            "name": "UrbanizacionZona_PEADDR",
            "description": "Name of the neighborhood as determined by the rule set",
            "max_length": 60,
        },
        {
            "name": "DireccionAdicional_PEADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 60,
        },
        {
            "name": "MatchNombreCalle_PEADDR",
            "description": "Standardized version of the NombreCalle",
            "max_length": 40,
        },
        {
            "name": "MatchNombreCalleHashKey_PEADDR",
            "description": "The first two characters of the first 5 words of MatchNombreCalle",
            "max_length": 10,
        },
        {
            "name": "MatchNombreCallePackKey_PEADDR",
            "description": "MatchNombreCalle value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumdeMatchPalabrasCalle_PEADDR",
            "description": "Number of words in MatchNombreCalle column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPalabraCalle1_PEADDR",
            "description": "First word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle2_PEADDR",
            "description": "Second word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle3_PEADDR",
            "description": "Third word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle4_PEADDR",
            "description": "Fourth word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle5_PEADDR",
            "description": "Fifth word of MatchNombreCalle column",
            "max_length": 15,
        },
        {
            "name": "MatchPalabraCalle1NYSIIS_PEADDR",
            "description": "Phonetic sound of the MatchPalabraCalle1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalabraCalle1RVSNDX_PEADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalabraCalle1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle1SNDX_PEADDR",
            "description": "Phonetic sound of the MatchPalabraCalle1 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle2NYSIIS_PEADDR",
            "description": "Phonetic sound of the MatchPalabraCalle2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchPalabraCalle2RVSNDX_PEADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPalabraCalle2 column",
            "max_length": 4,
        },
        {
            "name": "MatchPalabraCalle2SNDX_PEADDR",
            "description": "Phonetic sound of the MatchPalabraCalle2 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_PEADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_PEADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_PEADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_PEADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_PEADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "PEAREA": [
        {
            "name": "Distrito_PEAREA",
            "description": "Name of the district as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "CodigoPostal_PEAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "Provincia_PEAREA",
            "description": "Name of the province as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "Departamento_PEAREA",
            "description": "Name of the department as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "CodigoPais_PEAREA",
            "description": "Country name as determined by the AREA rule set",
            "max_length": 30,
        },
        {
            "name": "DistritoNYSIIS_PEAREA",
            "description": "Phonetic sound of the Distrito column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "DistritoRVSNDX_PEAREA",
            "description": "Numerical representation of the reverse phonetic sound of the Distrito column",
            "max_length": 4,
        },
        {
            "name": "DistritoSNDX_PEAREA",
            "description": "Phonetic sound of the Distrito column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "ProvinciaNYSIIS_PEAREA",
            "description": "Phonetic sound of the Provincia column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "ProvinciaRVSNDX_PEAREA",
            "description": "Numerical representation of the reverse phonetic sound of the Provincia column",
            "max_length": 4,
        },
        {
            "name": "ProvinciaSNDX_PEAREA",
            "description": "Phonetic sound of the Provincia column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "DepartamentoNYSIIS_PEAREA",
            "description": "Phonetic sound of the Departamento column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "DepartamentoRVSNDX_PEAREA",
            "description": "Numerical representation of the reverse phonetic sound of the Departamento column",
            "max_length": 4,
        },
        {
            "name": "DepartamentoSNDX_PEAREA",
            "description": "Phonetic sound of the Departamento column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_PEAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_PEAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_PEAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_PEAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_PEAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "PENAME": [
        {
            "name": "TipoNombre_PENAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "CodigoGenero_PENAME",
            "description": "The gender of the individual name that is derived from the PrefijoNombre or PrimerNombre",
            "max_length": 1,
        },
        {
            "name": "PrefijoNombre_PENAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "PrimerNombre_PENAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "SegundoNombre_PENAME",
            "description": "Middle Name of the Individual",
            "max_length": 70,
        },
        {
            "name": "Apellido_PENAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 70,
        },
        {
            "name": "Nombre_Adicional_PENAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "SufijoNombre_PENAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "MatchPrimerNombre_PENAME",
            "description": "Standardized version of the PrimerNombre, for example 'WILLIAM' is the MatchPrimerNombre of the PrimerNombre 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchPrimerNombreNYSIIS_PENAME",
            "description": "Phonetic sound of the MatchPrimerNombre column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimerNombreRVSNDX_PENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimerNombre column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido_PENAME",
            "description": "Apellido without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 70,
        },
        {
            "name": "MatchApellidoHashKey_PENAME",
            "description": "The first two characters of the first 5 words of MatchApellido",
            "max_length": 10,
        },
        {
            "name": "MatchApellidoPackKey_PENAME",
            "description": "MatchApellido value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchApellido_PENAME",
            "description": "Number of words in MatchApellido column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchApellido1_PENAME",
            "description": "First word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido2_PENAME",
            "description": "Second word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido3_PENAME",
            "description": "Third word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido4_PENAME",
            "description": "Fourth word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido5_PENAME",
            "description": "Fifth word of MatchApellido column",
            "max_length": 15,
        },
        {
            "name": "MatchApellido1NYSIIS_PENAME",
            "description": "Phonetic sound of the MatchApellido1 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchApellido1RVSNDX_PENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchApellido1 column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido1SNDX_PENAME",
            "description": "Phonetic sound of the MatchApellido1 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "MatchApellido2NYSIIS_PENAME",
            "description": "Phonetic sound of the MatchApellido2 column using the NYSIIS algorithm",
            "max_length": 8,
        },
        {
            "name": "MatchApellido2RVSNDX_PENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchApellido2 column",
            "max_length": 4,
        },
        {
            "name": "MatchApellido2SNDX_PENAME",
            "description": "Phonetic sound of the MatchApellido2 column using the Soundex algorithm",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_PENAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_PENAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_PENAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_PENAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_PENAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "PEPREP": [
        {
            "name": "DominioNombre_PEPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "DominioDireccion_PEPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "DominioArea_PEPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_PEPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_PEPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_PEPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_PEPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_PEPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_PEPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_PEPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_PEPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_PEPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_PEPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "FRADDR": [
        {
            "name": "StreetNumber_FRADDR",
            "description": "House number as determined by the rule set",
            "max_length": 5,
        },
        {
            "name": "StreetRepetition_FRADDR",
            "description": "A suffix that appears after the street number, for example 'BIS' or 'TER'",
            "max_length": 5,
        },
        {
            "name": "StreetType_FRADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 20,
        },
        {
            "name": "StreetName_FRADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "BoitePostaleType_FRADDR",
            "description": "Standardized Post Office Box descriptor, typically 'BP'",
            "max_length": 20,
        },
        {
            "name": "BoitePostaleValue_FRADDR",
            "description": "The value affiliated with the BoitePostaleType column",
            "max_length": 5,
        },
        {
            "name": "CenterType_FRADDR",
            "description": "Standardized center descriptor",
            "max_length": 30,
        },
        {
            "name": "CenterName_FRADDR",
            "description": "The name affiliated with the CenterType column",
            "max_length": 30,
        },
        {
            "name": "BuildingType_FRADDR",
            "description": "Standardized building descriptor",
            "max_length": 20,
        },
        {
            "name": "BuildingValue_FRADDR",
            "description": "Name of the building affiliated with the BuildingType column",
            "max_length": 5,
        },
        {
            "name": "EntranceType_FRADDR",
            "description": "Standardized entrance descriptor",
            "max_length": 20,
        },
        {
            "name": "EntranceValue_FRADDR",
            "description": "Value affiliated with the EntranceType column",
            "max_length": 5,
        },
        {
            "name": "FloorType_FRADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 20,
        },
        {
            "name": "FloorValue_FRADDR",
            "description": "Value affiliated with the FloorType column",
            "max_length": 5,
        },
        {
            "name": "UnitType_FRADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 20,
        },
        {
            "name": "UnitValue_FRADDR",
            "description": "Value that is affiliated with the UnitType column",
            "max_length": 5,
        },
        {
            "name": "LieuDitType_FRADDR",
            "description": "Standardized lieu dit descriptor, typically 'LIEU DIT'",
            "max_length": 10,
        },
        {
            "name": "LieuDitValue_FRADDR",
            "description": "Name of the lieu dit affiliated with the LieuDitType column",
            "max_length": 30,
        },
        {
            "name": "AdditionalAddress_FRADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "AddressType_FRADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "MatchStreetName_FRADDR",
            "description": "Standardized version of the StreetName",
            "max_length": 25,
        },
        {
            "name": "MatchStreetNameHashKey_FRADDR",
            "description": "The first two characters of the first 5 words of MatchStreetName",
            "max_length": 10,
        },
        {
            "name": "MatchStreetNamePackKey_FRADDR",
            "description": "MatchStreetName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchStreetWords_FRADDR",
            "description": "Number of words in MatchStreetName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchStreetWord1_FRADDR",
            "description": "First word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord2_FRADDR",
            "description": "Second word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord3_FRADDR",
            "description": "Third word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord4_FRADDR",
            "description": "Fourth word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord5_FRADDR",
            "description": "Fifth word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord1NYSIIS_FRADDR",
            "description": "Phonetic sound of the MatchStreetWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchStreetWord1RVSNDX_FRADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchStreetWord2NYSIIS_FRADDR",
            "description": "Phonetic sound of the MatchStreetWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchStreetWord2RVSNDX_FRADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_FRADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_FRADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_FRADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_FRADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_FRADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "FRAREA": [
        {
            "name": "PostalCode_FRAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 6,
        },
        {
            "name": "CityName_FRAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "CountryCode_FRAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 3,
        },
        {
            "name": "CityNameNYSIIS_FRAREA",
            "description": "Phonetic sound of the CityName column",
            "max_length": 8,
        },
        {
            "name": "CityNameRVSNDX_FRAREA",
            "description": "Numerical representation of the reverse phonetic sound of the CityName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_FRAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_FRAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_FRAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_FRAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_FRAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "FRNAME": [
        {
            "name": "NameType_FRNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_FRNAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_FRNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_FRNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_FRNAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_FRNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_FRNAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_FRNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AttentionName_FRNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_FRNAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_FRNAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_FRNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_FRNAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_FRNAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_FRNAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_FRNAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_FRNAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_FRNAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_FRNAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_FRNAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_FRNAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_FRNAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_FRNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_FRNAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_FRNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_FRNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_FRNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_FRNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_FRNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_FRNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "FRPREP": [
        {
            "name": "NameDomain_FRPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_FRPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_FRPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_FRPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_FRPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_FRPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_FRPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_FRPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_FRPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_FRPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_FRPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_FRPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_FRPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "DEADDR": [
        {
            "name": "AddressType_DEADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "StreetPrefixDirectional_DEADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "StreetPrefixType_DEADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 10,
        },
        {
            "name": "StreetName_DEADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 35,
        },
        {
            "name": "StreetSuffixType_DEADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 10,
        },
        {
            "name": "StreetSuffixDirectional_DEADDR",
            "description": "Street direction that appears after the street name, for example North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "HouseNumber_DEADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "HouseNumberSuffix_DEADDR",
            "description": "Suffix of the house number as determined by the rule set, for example 'A' is the suffix in 123A Main St",
            "max_length": 10,
        },
        {
            "name": "PostBoxType_DEADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 9,
        },
        {
            "name": "PostBoxValue_DEADDR",
            "description": "The value affiliated with the PostBoxType column",
            "max_length": 10,
        },
        {
            "name": "BuildingType_DEADDR",
            "description": "Standardized building descriptor",
            "max_length": 15,
        },
        {
            "name": "BuildingValue_DEADDR",
            "description": "Name of the building affiliated with the BuildingType column",
            "max_length": 20,
        },
        {
            "name": "UnitType_DEADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 15,
        },
        {
            "name": "UnitValue_DEADDR",
            "description": "Value that is affiliated with the UnitType column",
            "max_length": 10,
        },
        {
            "name": "MatchStreetName_DEADDR",
            "description": "Standardized version of the StreetName",
            "max_length": 35,
        },
        {
            "name": "MatchStreetNameHashKey_DEADDR",
            "description": "The first two characters of the first 5 words of MatchStreetName",
            "max_length": 10,
        },
        {
            "name": "MatchStreetNamePackKey_DEADDR",
            "description": "MatchStreetName value without spaces",
            "max_length": 30,
        },
        {
            "name": "NumofMatchStreetWords_DEADDR",
            "description": "Number of words in MatchStreetName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchStreetWord1_DEADDR",
            "description": "First word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord2_DEADDR",
            "description": "Second word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord3_DEADDR",
            "description": "Third word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord4_DEADDR",
            "description": "Fourth word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord5_DEADDR",
            "description": "Fifth word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord1NYSIIS_DEADDR",
            "description": "Phonetic sound of the MatchStreetWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchStreetWord1RVSNDX_DEADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchStreetWord2NYSIIS_DEADDR",
            "description": "Phonetic sound of the MatchStreetWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchStreetWord2RVSNDX_DEADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_DEADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_DEADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_DEADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_DEADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_DEADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "DEAREA": [
        {
            "name": "PostalCode_DEAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 6,
        },
        {
            "name": "CityName_DEAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "CountryCode_DEAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 3,
        },
        {
            "name": "CityNameNYSIIS_DEAREA",
            "description": "Phonetic sound of the CityName column",
            "max_length": 8,
        },
        {
            "name": "CityNameRVSNDX_DEAREA",
            "description": "Numerical representation of the reverse phonetic sound of the CityName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_DEAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_DEAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_DEAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_DEAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_DEAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "DENAME": [
        {
            "name": "NameType_DENAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_DENAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_DENAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_DENAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_DENAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_DENAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_DENAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_DENAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_DENAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_DENAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_DENAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_DENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_DENAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_DENAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_DENAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_DENAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_DENAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_DENAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_DENAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_DENAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_DENAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_DENAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_DENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_DENAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_DENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_DENAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_DENAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_DENAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_DENAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_DENAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "DEPREP": [
        {
            "name": "NameDomain_DEPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_DEPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_DEPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_DEPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_DEPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_DEPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_DEPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_DEPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_DEPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_DEPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_DEPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_DEPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_DEPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "IEADDR": [
        {
            "name": "SubBuildingName_IEADDR",
            "description": "Name of the building affiliated with the SubBuildingDescriptor column",
            "max_length": 30,
        },
        {
            "name": "SubBuildingDescriptor_IEADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 20,
        },
        {
            "name": "SubBuildingNumber_IEADDR",
            "description": "Numeric value that is affiliated with the SubBuildingName column",
            "max_length": 10,
        },
        {
            "name": "SubBuildingNameFormat1_IEADDR",
            "description": "Alphanumeric value that is affiliated with the SubBuildingName column",
            "max_length": 10,
        },
        {
            "name": "BuildingPrefix_IEADDR",
            "description": "Building direction that appears before the building name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "BuildingName_IEADDR",
            "description": "Name of the building affiliated with the BuildingDescriptor column",
            "max_length": 50,
        },
        {
            "name": "BuildingDescriptor_IEADDR",
            "description": "Standardized building descriptor",
            "max_length": 20,
        },
        {
            "name": "BuildingSuffix_IEADDR",
            "description": "Building direction that appears after the building name, for example North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "BuildingNameFormat1_IEADDR",
            "description": "Alphanumeric value that is affiliated with the BuildingName column",
            "max_length": 10,
        },
        {
            "name": "BuildingNumber_IEADDR",
            "description": "Numeric value that is affiliated with the BuildingName column",
            "max_length": 4,
        },
        {
            "name": "DepThfareQualifier_IEADDR",
            "description": "A directive that appears before the street name, for example 'Below' or 'Upper'",
            "max_length": 20,
        },
        {
            "name": "DepThfarePrefix_IEADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "DepThfareName_IEADDR",
            "description": "Secondary street name as determined by the rule set",
            "max_length": 60,
        },
        {
            "name": "DepThfareDescriptor_IEADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 20,
        },
        {
            "name": "DepThfareSuffix_IEADDR",
            "description": "Street direction that appears after the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "ThfareQualifier_IEADDR",
            "description": "An adjective that appears before the street name, for example 'Old' or 'New'",
            "max_length": 20,
        },
        {
            "name": "ThfarePrefix_IEADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "ThfareName_IEADDR",
            "description": "Primary street name as determined by the rule set",
            "max_length": 60,
        },
        {
            "name": "ThfareDescriptor_IEADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 20,
        },
        {
            "name": "ThfareSuffix_IEADDR",
            "description": "Street direction that appears after the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "POBoxDescriptor_IEADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 6,
        },
        {
            "name": "POBoxNumber_IEADDR",
            "description": "The value affiliated with the POBoxDescriptor column",
            "max_length": 6,
        },
        {
            "name": "AddressType_IEADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "ThfareNameNYSIIS_IEADDR",
            "description": "Phonetic sound of the ThfareName column",
            "max_length": 8,
        },
        {
            "name": "ThfareNameRVSNDX_IEADDR",
            "description": "Numerical representation of the reverse phonetic sound of the ThfareName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_IEADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_IEADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_IEADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_IEADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_IEADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "IEAREA": [
        {
            "name": "DoubleDepLocality_IEAREA",
            "description": "Name of the double dependent locality as determined by the rule set",
            "max_length": 35,
        },
        {
            "name": "DepLocality_IEAREA",
            "description": "Name of the dependent locality as determined by the rule set",
            "max_length": 35,
        },
        {
            "name": "PostTown_IEAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "County_IEAREA",
            "description": "Name of the county as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "OutwardPostcode_IEAREA",
            "description": "First part of the United Kingdom post code",
            "max_length": 4,
        },
        {
            "name": "InwardPostcode_IEAREA",
            "description": "Second part of the United Kingdom post code",
            "max_length": 3,
        },
        {
            "name": "CountryCode_IEAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 2,
        },
        {
            "name": "PostTownNYSIIS_IEAREA",
            "description": "Phonetic sound of the PostTown column",
            "max_length": 8,
        },
        {
            "name": "UnhandledPattern_IEAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_IEAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_IEAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_IEAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_IEAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "IENAME": [
        {
            "name": "NameType_IENAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_IENAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_IENAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_IENAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_IENAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_IENAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_IENAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_IENAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_IENAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_IENAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_IENAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_IENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchMiddleName_IENAME",
            "description": "MatchMiddleName",
            "max_length": 25,
        },
        {
            "name": "MatchPrimaryName_IENAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_IENAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_IENAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_IENAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_IENAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_IENAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_IENAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_IENAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_IENAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_IENAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_IENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_IENAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_IENAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_IENAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_IENAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_IENAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_IENAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_IENAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "IEPREP": [
        {
            "name": "NameDomain_IEPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_IEPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_IEPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_IEPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_IEPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_IEPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_IEPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_IEPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_IEPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_IEPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_IEPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_IEPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_IEPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "ITADDR": [
        {
            "name": "AddressType_ITADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "StreetPrefixType_ITADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 20,
        },
        {
            "name": "StreetName_ITADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "StreetDirectional_ITADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "HouseNumber_ITADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "HouseNumberSuffix_ITADDR",
            "description": "Suffix of the house number as determined by the rule set, for example 'A' is the suffix in 123A Main St",
            "max_length": 10,
        },
        {
            "name": "PostBoxType_ITADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 9,
        },
        {
            "name": "PostBoxValue_ITADDR",
            "description": "The value affiliated with the PostBoxType column",
            "max_length": 10,
        },
        {
            "name": "BuildingType_ITADDR",
            "description": "Standardized building descriptor",
            "max_length": 15,
        },
        {
            "name": "BuildingValue_ITADDR",
            "description": "Name of the building affiliated with the BuildingType column",
            "max_length": 20,
        },
        {
            "name": "UnitType_ITADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 15,
        },
        {
            "name": "UnitValue_ITADDR",
            "description": "Value that is affiliated with the UnitType column",
            "max_length": 10,
        },
        {
            "name": "AdditionalAddress_ITADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchStreetName_ITADDR",
            "description": "Standardized version of the StreetName",
            "max_length": 25,
        },
        {
            "name": "MatchStreetNameHashKey_ITADDR",
            "description": "The first two characters of the first 5 words of MatchStreetName",
            "max_length": 10,
        },
        {
            "name": "MatchStreetNamePackKey_ITADDR",
            "description": "MatchStreetName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchStreetWords_ITADDR",
            "description": "Number of words in MatchStreetName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchStreetWord1_ITADDR",
            "description": "First word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord2_ITADDR",
            "description": "Second word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord3_ITADDR",
            "description": "Third word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord4_ITADDR",
            "description": "Fourth word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord5_ITADDR",
            "description": "Fifth word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord1NYSIIS_ITADDR",
            "description": "Phonetic sound of the MatchStreetWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchStreetWord1RVSNDX_ITADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchStreetWord2NYSIIS_ITADDR",
            "description": "Phonetic sound of the MatchStreetWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchStreetWord2RVSNDX_ITADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ITADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ITADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_ITADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ITADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ITADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ITAREA": [
        {
            "name": "PostalCode_ITAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 6,
        },
        {
            "name": "CityName_ITAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "ProvinceAbbreviation_ITAREA",
            "description": "Two letter province abbreviation",
            "max_length": 3,
        },
        {
            "name": "CountryCode_ITAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 3,
        },
        {
            "name": "CityNameNYSIIS_ITAREA",
            "description": "Phonetic sound of the CityName column",
            "max_length": 8,
        },
        {
            "name": "CityNameRVSNDX_ITAREA",
            "description": "Numerical representation of the reverse phonetic sound of the CityName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ITAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ITAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_ITAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ITAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ITAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ITNAME": [
        {
            "name": "NameType_ITNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_ITNAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_ITNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_ITNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_ITNAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_ITNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_ITNAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_ITNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_ITNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_ITNAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_ITNAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_ITNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_ITNAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_ITNAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_ITNAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_ITNAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_ITNAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_ITNAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_ITNAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_ITNAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_ITNAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_ITNAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_ITNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_ITNAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_ITNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ITNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ITNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_ITNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ITNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ITNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ITPREP": [
        {
            "name": "NameDomain_ITPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_ITPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_ITPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_ITPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_ITPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_ITPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_ITPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_ITPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_ITPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_ITPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_ITPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_ITPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_ITPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "NLADDR": [
        {
            "name": "AddressType_NLADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "StreetPrefixDirectional_NLADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "StreetPrefixType_NLADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 10,
        },
        {
            "name": "StreetName_NLADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 35,
        },
        {
            "name": "StreetSuffixType_NLADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 10,
        },
        {
            "name": "StreetSuffixDirectional_NLADDR",
            "description": "Street direction that appears after the street name, for example North=N, East=E, or Southwest=SW",
            "max_length": 3,
        },
        {
            "name": "HouseNumber_NLADDR",
            "description": "House number as determined by the rule set",
            "max_length": 8,
        },
        {
            "name": "HouseNumberSuffix_NLADDR",
            "description": "Suffix of the house number as determined by the rule set, for example 'A' is the suffix in 123A Main St",
            "max_length": 4,
        },
        {
            "name": "HouseNumberRange_NLADDR",
            "description": "Range of house numbers as determined by the rule set",
            "max_length": 8,
        },
        {
            "name": "PostBoxType_NLADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 15,
        },
        {
            "name": "PostBoxValue_NLADDR",
            "description": "The value affiliated with the PostBoxType column",
            "max_length": 10,
        },
        {
            "name": "BuildingType_NLADDR",
            "description": "Standardized building descriptor",
            "max_length": 10,
        },
        {
            "name": "BuildingValue_NLADDR",
            "description": "Name of the building affiliated with the BuildingType column",
            "max_length": 20,
        },
        {
            "name": "FloorType_NLADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 10,
        },
        {
            "name": "FloorValue_NLADDR",
            "description": "Value affiliated with the FloorType column",
            "max_length": 5,
        },
        {
            "name": "RoomType_NLADDR",
            "description": "Standardized room descriptor such as Apt, Unit, or Suite",
            "max_length": 10,
        },
        {
            "name": "RoomValue_NLADDR",
            "description": "Value that is affiliated with the RoomType column",
            "max_length": 5,
        },
        {
            "name": "MatchStreetName_NLADDR",
            "description": "Standardized version of the StreetName",
            "max_length": 25,
        },
        {
            "name": "HashKeyofMatchStreetName_NLADDR",
            "description": "The first two characters of the first 5 words of MatchStreetName",
            "max_length": 10,
        },
        {
            "name": "PackedKeyofMatchStreetName_NLADDR",
            "description": "MatchStreetName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumberofMatchStreetWords_NLADDR",
            "description": "Number of words in MatchStreetName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchStreetWord1_NLADDR",
            "description": "First word of MatchStreetName column",
            "max_length": 20,
        },
        {
            "name": "MatchStreetWord2_NLADDR",
            "description": "Second word of MatchStreetName column",
            "max_length": 20,
        },
        {
            "name": "MatchStreetWord3_NLADDR",
            "description": "Third word of MatchStreetName column",
            "max_length": 20,
        },
        {
            "name": "MatchStreetWord4_NLADDR",
            "description": "Fourth word of MatchStreetName column",
            "max_length": 20,
        },
        {
            "name": "MatchStreetWord5_NLADDR",
            "description": "Fifth word of MatchStreetName column",
            "max_length": 20,
        },
        {
            "name": "NYSIISofMatchStreetWord1_NLADDR",
            "description": "Phonetic sound of the MatchStreetWord1 column",
            "max_length": 8,
        },
        {
            "name": "RSoundexofMatchStreetWord1_NLADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord1 column",
            "max_length": 4,
        },
        {
            "name": "NYSIISofMatchStreetWord2_NLADDR",
            "description": "Phonetic sound of the MatchStreetWord2 column",
            "max_length": 8,
        },
        {
            "name": "RSoundexofMatchStreetWord2_NLADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_NLADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_NLADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_NLADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_NLADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_NLADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "NLAREA": [
        {
            "name": "PostalCode_NLAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 7,
        },
        {
            "name": "CityNamePrefix_NLAREA",
            "description": "Directional and/or common words that appear before city name",
            "max_length": 10,
        },
        {
            "name": "CityName_NLAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "CityNameSuffix_NLAREA",
            "description": "Directional and/or common words that appear after city name",
            "max_length": 10,
        },
        {
            "name": "CountryCode_NLAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 3,
        },
        {
            "name": "NYSIISofCityName_NLAREA",
            "description": "Phonetic sound of the CityName column",
            "max_length": 8,
        },
        {
            "name": "RSoundexofCityName_NLAREA",
            "description": "Numerical representation of the reverse phonetic sound of the CityName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_NLAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_NLAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_NLAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_NLAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_NLAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "NLNAME": [
        {
            "name": "NameType_NLNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_NLNAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_NLNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_NLNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_NLNAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryPrefix_NLNAME",
            "description": "Prefix for an individual last name, for example: Van",
            "max_length": 15,
        },
        {
            "name": "PrimaryName_NLNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_NLNAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_NLNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_NLNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_NLNAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "NYSIISofMatchFirstName_NLNAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "RSoundexofMatchFirstName_NLNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_NLNAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "HashKeyofMatchPrimaryName_NLNAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "PackedKeyofMatchPrimaryName_NLNAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumberofMatchPrimaryWords_NLNAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_NLNAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 20,
        },
        {
            "name": "MatchPrimaryWord2_NLNAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 20,
        },
        {
            "name": "MatchPrimaryWord3_NLNAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 20,
        },
        {
            "name": "MatchPrimaryWord4_NLNAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 20,
        },
        {
            "name": "MatchPrimaryWord5_NLNAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 20,
        },
        {
            "name": "NYSIISofMatchPrimaryWord1_NLNAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "RSoundexofMatchPrimaryWord1_NLNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "NYSIISofMatchPrimaryWord2_NLNAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "RSoundexofMatchPrimaryWord2_NLNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_NLNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_NLNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_NLNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_NLNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_NLNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "NLPREP": [
        {
            "name": "NameDomain_NLPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_NLPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_NLPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_NLPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_NLPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_NLPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_NLPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_NLPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_NLPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_NLPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_NLPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_NLPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_NLPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "ESADDR": [
        {
            "name": "AddressType_ESADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "StreetPrefixType_ESADDR",
            "description": "Street type that appears before the street name, for example: Rue, Calle, or Blvd",
            "max_length": 20,
        },
        {
            "name": "StreetName_ESADDR",
            "description": "Street name as determined by the rule set",
            "max_length": 50,
        },
        {
            "name": "HouseNumber_ESADDR",
            "description": "House number as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "HouseNumberSuffix_ESADDR",
            "description": "Suffix of the house number as determined by the rule set, for example 'A' is the suffix in 123A Main St",
            "max_length": 10,
        },
        {
            "name": "PostBoxType_ESADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 10,
        },
        {
            "name": "PostBoxValue_ESADDR",
            "description": "The value affiliated with the PostBoxType column",
            "max_length": 10,
        },
        {
            "name": "BuildingType_ESADDR",
            "description": "Standardized building descriptor",
            "max_length": 15,
        },
        {
            "name": "BuildingValue_ESADDR",
            "description": "Name of the building affiliated with the BuildingType column",
            "max_length": 20,
        },
        {
            "name": "FloorType_ESADDR",
            "description": "Standardized floor descriptor, typically 'FL'",
            "max_length": 10,
        },
        {
            "name": "FloorValue_ESADDR",
            "description": "Value affiliated with the FloorType column",
            "max_length": 10,
        },
        {
            "name": "UnitType_ESADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 15,
        },
        {
            "name": "UnitValue_ESADDR",
            "description": "Value that is affiliated with the UnitType column",
            "max_length": 10,
        },
        {
            "name": "UnitSuffix_ESADDR",
            "description": "Suffix of the unit value as determined by the rule set",
            "max_length": 10,
        },
        {
            "name": "AdditionalAddress_ESADDR",
            "description": "Address components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchStreetName_ESADDR",
            "description": "Standardized version of the StreetName",
            "max_length": 25,
        },
        {
            "name": "MatchStreetNameHashKey_ESADDR",
            "description": "The first two characters of the first 5 words of MatchStreetName",
            "max_length": 10,
        },
        {
            "name": "MatchStreetNamePackKey_ESADDR",
            "description": "MatchStreetName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchStreetWords_ESADDR",
            "description": "Number of words in MatchStreetName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchStreetWord1_ESADDR",
            "description": "First word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord2_ESADDR",
            "description": "Second word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord3_ESADDR",
            "description": "Third word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord4_ESADDR",
            "description": "Fourth word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord5_ESADDR",
            "description": "Fifth word of MatchStreetName column",
            "max_length": 15,
        },
        {
            "name": "MatchStreetWord1NYSIIS_ESADDR",
            "description": "Phonetic sound of the MatchStreetWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchStreetWord1RVSNDX_ESADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchStreetWord2NYSIIS_ESADDR",
            "description": "Phonetic sound of the MatchStreetWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchStreetWord2RVSNDX_ESADDR",
            "description": "Numerical representation of the reverse phonetic sound of the MatchStreetWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ESADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ESADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_ESADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ESADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ESADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ESAREA": [
        {
            "name": "PostalCode_ESAREA",
            "description": "Post code as determined by the rule set",
            "max_length": 6,
        },
        {
            "name": "CityName_ESAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "ProvinceName_ESAREA",
            "description": "Name of the province as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "CountryCode_ESAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 3,
        },
        {
            "name": "CityNameNYSIIS_ESAREA",
            "description": "Phonetic sound of the CityName column",
            "max_length": 8,
        },
        {
            "name": "CityNameRVSNDX_ESAREA",
            "description": "Numerical representation of the reverse phonetic sound of the CityName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ESAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ESAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_ESAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ESAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ESAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ESNAME": [
        {
            "name": "NameType_ESNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_ESNAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_ESNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_ESNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_ESNAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_ESNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_ESNAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_ESNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_ESNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_ESNAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_ESNAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_ESNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_ESNAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_ESNAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_ESNAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_ESNAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_ESNAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_ESNAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_ESNAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_ESNAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_ESNAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_ESNAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_ESNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_ESNAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_ESNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_ESNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_ESNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_ESNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_ESNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_ESNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "ESPREP": [
        {
            "name": "NameDomain_ESPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_ESPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_ESPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_ESPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_ESPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_ESPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_ESPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_ESPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_ESPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_ESPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_ESPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_ESPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_ESPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "GBADDR": [
        {
            "name": "SubBuildingName_GBADDR",
            "description": "Name of the building affiliated with the SubBuildingDescriptor column",
            "max_length": 30,
        },
        {
            "name": "SubBuildingDescriptor_GBADDR",
            "description": "Standardized unit descriptor such as Apt, Unit, or Suite",
            "max_length": 20,
        },
        {
            "name": "SubBuildingNumber_GBADDR",
            "description": "Numeric value that is affiliated with the SubBuildingName column",
            "max_length": 10,
        },
        {
            "name": "SubBuildingNameFormat1_GBADDR",
            "description": "Alphanumeric value that is affiliated with the SubBuildingName column",
            "max_length": 10,
        },
        {
            "name": "BuildingPrefix_GBADDR",
            "description": "Building direction that appears before the building name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "BuildingName_GBADDR",
            "description": "Name of the building affiliated with the BuildingDescriptor column",
            "max_length": 50,
        },
        {
            "name": "BuildingDescriptor_GBADDR",
            "description": "Standardized building descriptor",
            "max_length": 20,
        },
        {
            "name": "BuildingSuffix_GBADDR",
            "description": "Building direction that appears after the building name, for example North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "BuildingNameFormat1_GBADDR",
            "description": "Alphanumeric value that is affiliated with the BuildingName column",
            "max_length": 10,
        },
        {
            "name": "BuildingNumber_GBADDR",
            "description": "Numeric value that is affiliated with the BuildingName column",
            "max_length": 4,
        },
        {
            "name": "DepThfareQualifier_GBADDR",
            "description": "A directive that appears before the street name, for example 'Below' or 'Upper'",
            "max_length": 20,
        },
        {
            "name": "DepThfarePrefix_GBADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "DepThfareName_GBADDR",
            "description": "Secondary street name as determined by the rule set",
            "max_length": 60,
        },
        {
            "name": "DepThfareDescriptor_GBADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 20,
        },
        {
            "name": "DepThfareSuffix_GBADDR",
            "description": "Street direction that appears after the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "ThfareQualifier_GBADDR",
            "description": "An adjective that appears before the street name, for example 'Old' or 'New'",
            "max_length": 20,
        },
        {
            "name": "ThfarePrefix_GBADDR",
            "description": "Street direction that appears before the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "ThfareName_GBADDR",
            "description": "Primary street name as determined by the rule set",
            "max_length": 60,
        },
        {
            "name": "ThfareDescriptor_GBADDR",
            "description": "Street type that appears after the street name, for example 'Ave', 'St', or 'Rd'",
            "max_length": 20,
        },
        {
            "name": "ThfareSuffix_GBADDR",
            "description": "Street direction that appears after the street name, for example: North=N, East=E, or Southwest=SW",
            "max_length": 5,
        },
        {
            "name": "POBoxDescriptor_GBADDR",
            "description": "Standardized Post Office Box descriptor, typically 'PO Box'",
            "max_length": 6,
        },
        {
            "name": "POBoxNumber_GBADDR",
            "description": "The value affiliated with the POBoxDescriptor column",
            "max_length": 6,
        },
        {
            "name": "AddressType_GBADDR",
            "description": "Single alpha character that indicates the address type, for example street address=S or post office box=B",
            "max_length": 1,
        },
        {
            "name": "ThfareNameNYSIIS_GBADDR",
            "description": "Phonetic sound of the ThfareName column",
            "max_length": 8,
        },
        {
            "name": "ThfareNameRVSNDX_GBADDR",
            "description": "Numerical representation of the reverse phonetic sound of the ThfareName column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_GBADDR",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_GBADDR",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_GBADDR",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_GBADDR",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_GBADDR",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "GBAREA": [
        {
            "name": "DoubleDepLocality_GBAREA",
            "description": "Name of the double dependent locality as determined by the rule set",
            "max_length": 35,
        },
        {
            "name": "DepLocality_GBAREA",
            "description": "Name of the dependent locality as determined by the rule set",
            "max_length": 35,
        },
        {
            "name": "PostTown_GBAREA",
            "description": "Name of the city as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "County_GBAREA",
            "description": "Name of the county as determined by the rule set",
            "max_length": 30,
        },
        {
            "name": "OutwardPostcode_GBAREA",
            "description": "First part of the United Kingdom post code",
            "max_length": 4,
        },
        {
            "name": "InwardPostcode_GBAREA",
            "description": "Second part of the United Kingdom post code",
            "max_length": 3,
        },
        {
            "name": "CountryCode_GBAREA",
            "description": "Two letter ISO country or region code as determined by the AREA rule set",
            "max_length": 2,
        },
        {
            "name": "PostTownNYSIIS_GBAREA",
            "description": "Phonetic sound of the PostTown column",
            "max_length": 8,
        },
        {
            "name": "UnhandledPattern_GBAREA",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_GBAREA",
            "description": "Data that is not processed by the rule set",
            "max_length": 50,
        },
        {
            "name": "InputPattern_GBAREA",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_GBAREA",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_GBAREA",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "GBNAME": [
        {
            "name": "NameType_GBNAME",
            "description": "Single alpha character that indicates the name type, typically 'I' for individual, 'O' for organization",
            "max_length": 1,
        },
        {
            "name": "GenderCode_GBNAME",
            "description": "The gender of the individual name that is derived from the NamePrefix or FirstName",
            "max_length": 1,
        },
        {
            "name": "NamePrefix_GBNAME",
            "description": "Title that appears before the name, for example: Mr, Mrs, or Dr",
            "max_length": 20,
        },
        {
            "name": "FirstName_GBNAME",
            "description": "First name of the individual as determined by the rule set",
            "max_length": 25,
        },
        {
            "name": "MiddleName_GBNAME",
            "description": "Middle Name of the Individual",
            "max_length": 25,
        },
        {
            "name": "PrimaryName_GBNAME",
            "description": "Last name of an individual or name of a business",
            "max_length": 50,
        },
        {
            "name": "NameGeneration_GBNAME",
            "description": "Generation of the Individual, typically 'JR', 'SR', 'III'",
            "max_length": 10,
        },
        {
            "name": "NameSuffix_GBNAME",
            "description": "Title that appears at the end of the name, for example: PHD, MD, LTD",
            "max_length": 20,
        },
        {
            "name": "AdditionalName_GBNAME",
            "description": "Name components that cannot be parsed into existing columns",
            "max_length": 50,
        },
        {
            "name": "MatchFirstName_GBNAME",
            "description": "Standardized version of the FirstName, for example 'WILLIAM' is the MatchFirstname of the FirstName 'BILL'",
            "max_length": 25,
        },
        {
            "name": "MatchFirstNameNYSIIS_GBNAME",
            "description": "Phonetic sound of the MatchFirstName column",
            "max_length": 8,
        },
        {
            "name": "MatchFirstNameRVSNDX_GBNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchFirstName column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryName_GBNAME",
            "description": "PrimaryName without articles and conjuctions such as 'THE', 'AND' 'WITH'",
            "max_length": 50,
        },
        {
            "name": "MatchPrimaryNameHashKey_GBNAME",
            "description": "The first two characters of the first 5 words of MatchPrimaryName",
            "max_length": 10,
        },
        {
            "name": "MatchPrimaryNamePackKey_GBNAME",
            "description": "MatchPrimaryName value without spaces",
            "max_length": 20,
        },
        {
            "name": "NumofMatchPrimaryWords_GBNAME",
            "description": "Number of words in MatchPrimaryName column, counts up to 9 words",
            "max_length": 1,
        },
        {
            "name": "MatchPrimaryWord1_GBNAME",
            "description": "First word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord2_GBNAME",
            "description": "Second word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord3_GBNAME",
            "description": "Third word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord4_GBNAME",
            "description": "Fourth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord5_GBNAME",
            "description": "Fifth word of MatchPrimaryName column",
            "max_length": 15,
        },
        {
            "name": "MatchPrimaryWord1NYSIIS_GBNAME",
            "description": "Phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord1RVSNDX_GBNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord1 column",
            "max_length": 4,
        },
        {
            "name": "MatchPrimaryWord2NYSIIS_GBNAME",
            "description": "Phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 8,
        },
        {
            "name": "MatchPrimaryWord2RVSNDX_GBNAME",
            "description": "Numerical representation of the reverse phonetic sound of the MatchPrimaryWord2 column",
            "max_length": 4,
        },
        {
            "name": "UnhandledPattern_GBNAME",
            "description": "Pattern that is assigned to the unhandled data by the rule set",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_GBNAME",
            "description": "Data that is not processed by the rule set",
            "max_length": 100,
        },
        {
            "name": "InputPattern_GBNAME",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_GBNAME",
            "description": "Components of the data that the rule set identified as inappropriate for the domain",
            "max_length": 25,
        },
        {
            "name": "UserOverrideFlag_GBNAME",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "GBPREP": [
        {
            "name": "NameDomain_GBPREP",
            "description": "Name components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AddressDomain_GBPREP",
            "description": "Address components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "AreaDomain_GBPREP",
            "description": "Area components that have been identified by processing with PREP rule set",
            "max_length": 100,
        },
        {
            "name": "Field1Pattern_GBPREP",
            "description": "Input pattern of Field1 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field2Pattern_GBPREP",
            "description": "Input pattern of Field2 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field3Pattern_GBPREP",
            "description": "Input pattern of Field3 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field4Pattern_GBPREP",
            "description": "Input pattern of Field4 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field5Pattern_GBPREP",
            "description": "Input pattern of Field5 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "Field6Pattern_GBPREP",
            "description": "Input pattern of Field6 as denoted by the delimiters",
            "max_length": 20,
        },
        {
            "name": "InputPattern_GBPREP",
            "description": "Pattern that is assigned to the input data, this pattern reflects changes made in the classification overrides",
            "max_length": 88,
        },
        {
            "name": "OutboundPattern_GBPREP",
            "description": "Pattern that is assigned to the entire string by the PREP rule sets",
            "max_length": 88,
        },
        {
            "name": "UserOverrideFlag_GBPREP",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
        {
            "name": "CustomFlag_GBPREP",
            "description": "Placeholder for a flag that you can define",
            "max_length": 2,
        },
    ],
    "COUNTRY": [
        {
            "name": "ISOCountryCode_COUNTRY",
            "description": "ISO Country Code",
            "max_length": 3,
        },
        {
            "name": "IdentifierFlag_COUNTRY",
            "description": "Identifier Flag",
            "max_length": 2,
        },
        {
            "name": "UserOverrideFlag_COUNTRY",
            "description": "Indicator that an override was applied to the data, but it does not apply to the override classifications; default=NO",
            "max_length": 2,
        },
    ],
    "EXPCOM": [
        {
            "name": "CompanyName_EXPCOM",
            "description": "CompanyName",
            "max_length": 100,
        },
        {
            "name": "NumberOfWords_EXPCOM",
            "description": "NumberOfWords",
            "max_length": 1,
        },
        {
            "name": "AcronymOfKeywords_EXPCOM",
            "description": "AcronymOfKeywords",
            "max_length": 10,
        },
        {
            "name": "MatchKeyWord1_EXPCOM",
            "description": "New",
            "max_length": 15,
        },
        {
            "name": "MatchKeyWord2_EXPCOM",
            "description": "York",
            "max_length": 15,
        },
        {
            "name": "MatchKeyWord3_EXPCOM",
            "description": "Department",
            "max_length": 15,
        },
        {
            "name": "MatchKeyWord4_EXPCOM",
            "description": "Motor",
            "max_length": 15,
        },
        {
            "name": "MatchKeyWord5_EXPCOM",
            "description": "Vehicles",
            "max_length": 15,
        },
        {
            "name": "MatchKeyWord6_EXPCOM",
            "description": "State",
            "max_length": 15,
        },
        {
            "name": "MatchKeyWord7_EXPCOM",
            "description": "Investigation",
            "max_length": 15,
        },
        {
            "name": "MatchKeyWord8_EXPCOM",
            "description": "Div",
            "max_length": 15,
        },
        {
            "name": "MatchKeyWord1NYSIIS_EXPCOM",
            "description": "MatchKeyWord1NYSIIS",
            "max_length": 8,
        },
        {
            "name": "MatchKeyWord2NYSIIS_EXPCOM",
            "description": "MatchKeyWord2NYSIIS",
            "max_length": 8,
        },
        {
            "name": "TradeName_EXPCOM",
            "description": "TradeName",
            "max_length": 30,
        },
        {
            "name": "StateOrgNum_EXPCOM",
            "description": "StateOrgNum",
            "max_length": 15,
        },
        {
            "name": "FranchiseNumber_EXPCOM",
            "description": "FranchiseNumber",
            "max_length": 10,
        },
        {
            "name": "Division_EXPCOM",
            "description": "Division",
            "max_length": 30,
        },
        {
            "name": "AccountInfo_EXPCOM",
            "description": "AccountInfo",
            "max_length": 30,
        },
        {"name": "CorpDate_EXPCOM", "description": "CorpDate", "max_length": 8},
        {
            "name": "UnknownWords_EXPCOM",
            "description": "UnknownWords",
            "max_length": 15,
        },
        {
            "name": "UnhandledPattern_EXPCOM",
            "description": "UnhandledPattern",
            "max_length": 10,
        },
        {
            "name": "UnhandledData_EXPCOM",
            "description": "UnhandledData",
            "max_length": 20,
        },
        {
            "name": "ExceptionData_EXPCOM",
            "description": "ExceptionData",
            "max_length": 10,
        },
        {
            "name": "InputPattern_EXPCOM",
            "description": "InputPattern",
            "max_length": 10,
        },
        {
            "name": "InvalidData_EXPCOM",
            "description": "InvalidData",
            "max_length": 10,
        },
        {
            "name": "InvalidReason_EXPCOM",
            "description": "InvalidReason",
            "max_length": 2,
        },
        {
            "name": "UserOverrideFlag_EXPCOM",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "PHPROD": [
        {
            "name": "Manufacturer_PHPROD",
            "description": "Manufacturer",
            "max_length": 100,
        },
        {
            "name": "DrugDescriptive_PHPROD",
            "description": "DrugDescriptive",
            "max_length": 100,
        },
        {
            "name": "QtyActiveSubs_PHPROD",
            "description": "QtyActiveSubs",
            "max_length": 20,
        },
        {
            "name": "MeasureActiveSubs_PHPROD",
            "description": "MeasureActiveSubs",
            "max_length": 30,
        },
        {
            "name": "DrugType_PHPROD",
            "description": "DrugType",
            "max_length": 50,
        },
        {
            "name": "UnitQty1_PHPROD",
            "description": "UnitQty1",
            "max_length": 20,
        },
        {
            "name": "UnitOfMeasure1_PHPROD",
            "description": "UnitOfMeasure1",
            "max_length": 30,
        },
        {
            "name": "UnitQty2_PHPROD",
            "description": "UnitQty2",
            "max_length": 20,
        },
        {
            "name": "UnitOfMeasure2_PHPROD",
            "description": "UnitOfMeasure2",
            "max_length": 30,
        },
        {
            "name": "UnitQtyFormat_PHPROD",
            "description": "UnitQtyFormat",
            "max_length": 30,
        },
        {"name": "Package_PHPROD", "description": "Package", "max_length": 30},
        {
            "name": "UnhandledPattern_PHPROD",
            "description": "UnhandledPattern",
            "max_length": 30,
        },
        {
            "name": "UnhandledData_PHPROD",
            "description": "UnhandledData",
            "max_length": 50,
        },
        {
            "name": "InputPattern_PHPROD",
            "description": "InputPattern",
            "max_length": 30,
        },
        {
            "name": "ExceptionData_PHPROD",
            "description": "ExceptionData",
            "max_length": 50,
        },
        {
            "name": "UserOverrideFlag_PHPROD",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "VDATE": [
        {
            "name": "ValidFlag_VDATE",
            "description": "ValidFlag",
            "max_length": 1,
        },
        {
            "name": "DateCCYYMMDD_VDATE",
            "description": "DateCCYYMMDD",
            "max_length": 8,
        },
        {
            "name": "UnhandledPattern_VDATE",
            "description": "UnhandledPattern",
            "max_length": 10,
        },
        {
            "name": "UnhandledData_VDATE",
            "description": "UnhandledData",
            "max_length": 20,
        },
        {
            "name": "InputPattern_VDATE",
            "description": "InputPattern",
            "max_length": 10,
        },
        {
            "name": "InvalidData_VDATE",
            "description": "InvalidData",
            "max_length": 10,
        },
        {
            "name": "InvalidReason_VDATE",
            "description": "InvalidReason",
            "max_length": 2,
        },
        {
            "name": "UserOverrideFlag_VDATE",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "VEMAIL": [
        {
            "name": "ValidFlag_VEMAIL",
            "description": "ValidFlag",
            "max_length": 1,
        },
        {
            "name": "EmailUser_VEMAIL",
            "description": "EmailUser",
            "max_length": 40,
        },
        {
            "name": "EmailDomain_VEMAIL",
            "description": "EmailDomain",
            "max_length": 40,
        },
        {
            "name": "EmailTopLevel_VEMAIL",
            "description": "EmailTopLevel",
            "max_length": 15,
        },
        {
            "name": "EmailURL_VEMAIL",
            "description": "EmailURL",
            "max_length": 50,
        },
        {
            "name": "UnhandledPattern_VEMAIL",
            "description": "UnhandledPattern",
            "max_length": 20,
        },
        {
            "name": "UnhandledData_VEMAIL",
            "description": "UnhandledData",
            "max_length": 50,
        },
        {
            "name": "InputPattern_VEMAIL",
            "description": "InputPattern",
            "max_length": 20,
        },
        {
            "name": "InvalidReason_VEMAIL",
            "description": "InvalidReason",
            "max_length": 2,
        },
        {
            "name": "UserOverrideFlag_VEMAIL",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "VPHONE": [
        {
            "name": "ValidFlag_VPHONE",
            "description": "ValidFlag",
            "max_length": 1,
        },
        {
            "name": "PhoneNumber_VPHONE",
            "description": "PhoneNumber",
            "max_length": 10,
        },
        {
            "name": "PhoneExtension_VPHONE",
            "description": "PhoneExtension",
            "max_length": 10,
        },
        {
            "name": "UnhandledPattern_VPHONE",
            "description": "UnhandledPattern",
            "max_length": 10,
        },
        {
            "name": "UnhandledData_VPHONE",
            "description": "UnhandledData",
            "max_length": 20,
        },
        {
            "name": "ExceptionData_VPHONE",
            "description": "ExceptionData",
            "max_length": 10,
        },
        {
            "name": "InputPattern_VPHONE",
            "description": "InputPattern",
            "max_length": 10,
        },
        {
            "name": "InvalidData_VPHONE",
            "description": "InvalidData",
            "max_length": 20,
        },
        {
            "name": "InvalidReason_VPHONE",
            "description": "InvalidReason",
            "max_length": 2,
        },
        {
            "name": "UserOverrideFlag_VPHONE",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
    "VTAXID": [
        {
            "name": "ValidFlag_VTAXID",
            "description": "ValidFlag",
            "max_length": 1,
        },
        {"name": "TaxID_VTAXID", "description": "TaxID", "max_length": 10},
        {
            "name": "UnhandledPattern_VTAXID",
            "description": "UnhandledPattern",
            "max_length": 10,
        },
        {
            "name": "UnhandledData_VTAXID",
            "description": "UnhandledData",
            "max_length": 20,
        },
        {
            "name": "ExceptionData_VTAXID",
            "description": "ExceptionData",
            "max_length": 10,
        },
        {
            "name": "InputPattern_VTAXID",
            "description": "InputPattern",
            "max_length": 10,
        },
        {
            "name": "InvalidData_VTAXID",
            "description": "InvalidData",
            "max_length": 10,
        },
        {
            "name": "InvalidReason_VTAXID",
            "description": "InvalidReason",
            "max_length": 2,
        },
        {
            "name": "UserOverrideFlag_VTAXID",
            "description": "UserOverrideFlag",
            "max_length": 2,
        },
    ],
}
