'''
Filename: test_bod_parser.py
Project: /Users/sofiane/Desktop/APPLICATIONS/code/python-cmpparis-lib/tests
Created Date: Tuesday October 7th 2025
Author: Sofiane (sofiane@klark.app)
-----
Last Modified: Tuesday, 7th October 2025 3:03:02 pm
Modified By: Sofiane (sofiane@klark.app)
-----
Copyright (c) 2025 Klark
'''

"""
Test script for BODParser
"""
from cmpparis import BODParser, PURCHASE_ORDER_CONFIG

# XML exemple fourni par infor
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<SyncPurchaseOrder xmlns="http://schema.infor.com/InforOAGIS/2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schema.infor.com/InforOAGIS/2 http://schema.infor.com/2.14.x/InforOAGIS/BODs/SyncPurchaseOrder.xsd" releaseID="9.2" versionID="2.14.3" systemEnvironmentCode="Production" languageCode="GB">
	<ApplicationArea>
		<Sender>
			<LogicalID schemeVersionID="16.0.0.097">lid://infor.m3.m3</LogicalID>
			<ComponentID schemeVersionID="16.0.0.20250711012901.9">M3BE</ComponentID>
			<ConfirmationCode>OnError</ConfirmationCode>
		</Sender>
		<CreationDateTime>2025-09-24T09:33:09.770Z</CreationDateTime>
		<BODID>0b61d005-7e42-41e8-bf47-13039b8bd10d</BODID>
	</ApplicationArea>
	<DataArea>
		<Sync>
			<AccountingEntityID>300_001</AccountingEntityID>
			<LocationID>FR1</LocationID>
			<ActionCriteria>
				<ActionExpression actionCode="Replace"/>
			</ActionCriteria>
		</Sync>
		<PurchaseOrder>
			<PurchaseOrderHeader>
				<DocumentID>
					<ID accountingEntity="300_001" location="FR1" variationID="1" lid="lid://infor.m3.m3">1000000454</ID>
				</DocumentID>
				<DisplayID>1000000454</DisplayID>
				<LastModificationDateTime>2025-09-24T09:32:39.079Z</LastModificationDateTime>
				<LastModificationPerson>
					<IDs>
						<ID accountingEntity="300_001">EXTAGUEBSI</ID>
					</IDs>
				</LastModificationPerson>
				<DocumentDateTime>2025-09-09T00:00:00.000Z</DocumentDateTime>
				<Status>
					<Code>Open</Code>
				</Status>
				<CustomerParty>
					<BuyerContact>
						<Name>Anis Ben Romdhane</Name>
						<Communication preferredIndicator="false">
							<ChannelCode listID="Communication Channels">EMail</ChannelCode>
							<UseCode listID="Communication Use Codes">Office</UseCode>
							<URI>anis.benromdhane@infor.com</URI>
							<Preference>
								<Indicator>false</Indicator>
							</Preference>
						</Communication>
					</BuyerContact>
				</CustomerParty>
				<SupplierParty>
					<PartyIDs>
						<ID accountingEntity="300_001">CHN0000040</ID>
					</PartyIDs>
					<Name>HANGZHOU LIGHT INDUSTRIAL PRODUCTS</Name>
					<Location>
						<Address type="text">
							<AddressLine sequence="1">ROOM 1205 -61 XIYUAN ROAD WEST</AddressLine>
							<AddressLine sequence="2">LAKE TECHNOLOGY ECONOMIC ZONE</AddressLine>
							<CityName>HANGZHOU</CityName>
							<CountryCode listID="Countries">CN</CountryCode>
						</Address>
					</Location>
				</SupplierParty>
				<ShipToParty>
					<PartyIDs>
						<ID accountingEntity="300_001">FR1</ID>
					</PartyIDs>
					<Name>CMP GROUP</Name>
					<Location>
						<ID>FR1</ID>
						<Name>AMBLAINVILLE</Name>
						<Address type="text">
							<AddressLine sequence="1">ZAC DES VAL AVENUE DE BRUXELLES</AddressLine>
							<AddressLine sequence="3">60110 AMBLAINVILLE</AddressLine>
							<AddressLine sequence="4">France</AddressLine>
							<CityName>AMBLAINVILLE</CityName>
							<CountryCode listID="Countries">FR</CountryCode>
							<PostalCode>60110</PostalCode>
						</Address>
					</Location>
				</ShipToParty>
				<ShipFromParty>
					<PartyIDs>
						<ID accountingEntity="300_001">CHN0000040</ID>
					</PartyIDs>
					<Location>
						<ID accountingEntity="300_001">FR1</ID>
						<Address type="text">
							<AddressLine sequence="1">ZAC DES VAL AVENUE DE BRUXELLES</AddressLine>
							<AddressLine sequence="3">60110 AMBLAINVILLE</AddressLine>
							<AddressLine sequence="4">France</AddressLine>
							<CityName>AMBLAINVILLE</CityName>
							<CountryCode listID="Countries">FR</CountryCode>
							<PostalCode>60110</PostalCode>
						</Address>
					</Location>
					<Location>
						<Address type="text">
							<AddressLine sequence="1">ROOM 1205 -61 XIYUAN ROAD WEST</AddressLine>
							<AddressLine sequence="2">LAKE TECHNOLOGY ECONOMIC ZONE</AddressLine>
							<CityName>HANGZHOU</CityName>
							<CountryCode listID="Countries">CN</CountryCode>
						</Address>
					</Location>
				</ShipFromParty>
				<ExtendedAmount currencyID="USD">4600.00</ExtendedAmount>
				<TransportationTerm>
					<IncotermsCode listID="Incoterms">FOB</IncotermsCode>
					<IncotermsText>Free On Board(... named port of shipment)</IncotermsText>
					<FreightTermCode>CM</FreightTermCode>
				</TransportationTerm>
				<PaymentTerm>
					<PaymentTermCode listID="Payment Term">N60</PaymentTermCode>
					<Term>
						<ID>N60</ID>
						<Description>60 days net</Description>
						<Amount currencyID="USD">4600.00</Amount>
					</Term>
				</PaymentTerm>
				<RequestedShipDateTime>2025-12-09</RequestedShipDateTime>
				<PromisedDeliveryDateTime>2025-12-09</PromisedDeliveryDateTime>
				<OrderDateTime>2025-09-09</OrderDateTime>
			</PurchaseOrderHeader>
			<PurchaseOrderLine>
				<LineNumber>10000</LineNumber>
				<Status>
					<Code>Open</Code>
				</Status>
				<Item>
					<ItemID>
						<ID accountingEntity="300_001">HD1300</ID>
					</ItemID>
					<GTIN>4434567018240</GTIN>
					<ServiceIndicator>false</ServiceIndicator>
					<Description>SCULPTURE DECO BULLDOG NOIR VIDE POCHE 21CM M4</Description>
					<Classification type="Country of Origin">
						<Codes>
							<Code sequence="1" listID="Country of Origin">CN</Code>
						</Codes>
						<Description>China</Description>
					</Classification>
				</Item>
				<Quantity unitCode="EA">100</Quantity>
				<BaseUOMQuantity unitCode="EA">100</BaseUOMQuantity>
				<UnitPrice>
					<Amount currencyID="USD">44.00</Amount>
					<PerQuantity unitCode="EA">1</PerQuantity>
				</UnitPrice>
				<ExtendedAmount currencyID="USD">4312.00</ExtendedAmount>
				<TotalAmount currencyID="USD">4893.53</TotalAmount>
				<RequiredDeliveryDateTime>2025-12-09</RequiredDeliveryDateTime>
			</PurchaseOrderLine>
		</PurchaseOrder>
	</DataArea>
</SyncPurchaseOrder>"""

def test_basic_parsing():
    """Test 1: Parsing basique"""
    print("=" * 80)
    print("TEST 1: Parsing XML vers CSV")
    print("=" * 80)
    
    parser = BODParser()
    csv_output = parser.parse_and_convert(
        xml_content=xml_content,
        config=PURCHASE_ORDER_CONFIG
    )
    
    print(csv_output)
    print("\n✅ Test 1 réussi !\n")

def test_save_to_file():
    """Test 2: Sauvegarder en fichier"""
    print("=" * 80)
    print("TEST 2: Sauvegarde dans un fichier CSV")
    print("=" * 80)
    
    parser = BODParser()
    csv_output = parser.parse_and_convert(
        xml_content=xml_content,
        config=PURCHASE_ORDER_CONFIG,
        output_csv_path="output_test.csv"
    )
    
    print("✅ Fichier 'output_test.csv' créé avec succès !")
    print(f"📄 Aperçu des premières lignes :\n")
    print("\n".join(csv_output.split("\n")[:3]))
    print("\n✅ Test 2 réussi !\n")

def test_custom_config():
    """Test 3: Configuration personnalisée"""
    print("=" * 80)
    print("TEST 3: Configuration personnalisée (Header seulement)")
    print("=" * 80)
    
    from cmpparis import BODConfig
    
    # Config pour extraire uniquement le header
    custom_config = BODConfig(
        header_xpath=".//ns:PurchaseOrderHeader",
        lines_xpath=".//ns:PurchaseOrderLine",
        header_mapping={
            "order_number": ".//ns:DocumentID/ns:ID",
            "supplier_name": ".//ns:SupplierParty/ns:Name",
            "total_amount": ".//ns:ExtendedAmount",
        },
        line_mapping={},
        flatten_mode="header_only"
    )
    
    parser = BODParser()
    csv_output = parser.parse_and_convert(
        xml_content=xml_content,
        config=custom_config
    )
    
    print(csv_output)
    print("\n✅ Test 3 réussi !\n")

if __name__ == "__main__":
    print("\n🚀 Démarrage des tests BODParser\n")
    
    try:
        test_basic_parsing()
        test_save_to_file()
        test_custom_config()
        
        print("=" * 80)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()