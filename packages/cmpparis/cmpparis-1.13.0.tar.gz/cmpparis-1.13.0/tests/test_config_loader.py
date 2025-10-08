'''
Filename: test_config_loader.py
Project: /Users/sofiane/Desktop/APPLICATIONS/code/python-cmpparis-lib/tests
Created Date: Tuesday October 7th 2025
Author: Sofiane (sofiane@klark.app)
-----
Last Modified: Tuesday, 7th October 2025 3:13:07 pm
Modified By: Sofiane (sofiane@klark.app)
-----
Copyright (c) 2025 Klark
'''

"""
Test BODConfigLoader
"""
from cmpparis import BODParser, BODConfigLoader

# Ton XML de test
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<SyncPurchaseOrder xmlns="http://schema.infor.com/InforOAGIS/2">
    <DataArea>
        <PurchaseOrder>
            <PurchaseOrderHeader>
                <DocumentID><ID>1000000454</ID></DocumentID>
                <DocumentDateTime>2025-09-09T00:00:00.000Z</DocumentDateTime>
                <SupplierParty>
                    <PartyIDs><ID>CHN0000040</ID></PartyIDs>
                    <Name>HANGZHOU LIGHT INDUSTRIAL PRODUCTS</Name>
                </SupplierParty>
                <ShipToParty>
                    <PartyIDs><ID>FR1</ID></PartyIDs>
                    <Name>CMP GROUP</Name>
                </ShipToParty>
                <ExtendedAmount currencyID="USD">4600.00</ExtendedAmount>
                <TransportationTerm>
                    <IncotermsCode>FOB</IncotermsCode>
                </TransportationTerm>
                <PaymentTerm>
                    <PaymentTermCode>N60</PaymentTermCode>
                </PaymentTerm>
                <RequestedShipDateTime>2025-12-09</RequestedShipDateTime>
                <PromisedDeliveryDateTime>2025-12-09</PromisedDeliveryDateTime>
                <Status><Code>Open</Code></Status>
            </PurchaseOrderHeader>
            <PurchaseOrderLine>
                <LineNumber>10000</LineNumber>
                <Item>
                    <ItemID><ID>HD1300</ID></ItemID>
                    <Description>SCULPTURE DECO BULLDOG</Description>
                    <GTIN>4434567018240</GTIN>
                    <Classification type="Country of Origin">
                        <Codes><Code>CN</Code></Codes>
                    </Classification>
                </Item>
                <Quantity unitCode="EA">100</Quantity>
                <UnitPrice><Amount>44.00</Amount></UnitPrice>
                <ExtendedAmount>4312.00</ExtendedAmount>
                <RequiredDeliveryDateTime>2025-12-09</RequiredDeliveryDateTime>
                <Status><Code>Open</Code></Status>
            </PurchaseOrderLine>
        </PurchaseOrder>
    </DataArea>
</SyncPurchaseOrder>"""

def test_from_yaml():
    """Test: Load from YAML file"""
    print("=" * 80)
    print("TEST: Charger config depuis YAML")
    print("=" * 80)
    
    # Charger config depuis YAML
    config = BODConfigLoader.from_yaml("configs/purchase_order.yaml")
    
    # Parser XML
    parser = BODParser()
    csv_output = parser.parse_and_convert(xml_content, config)
    
    print(csv_output)
    print("\n✅ Config YAML chargée et utilisée avec succès !\n")

def test_from_json():
    """Test: Load from JSON file"""
    print("=" * 80)
    print("TEST: Charger config depuis JSON")
    print("=" * 80)
    
    # D'abord sauvegarder en JSON pour tester
    import json
    import yaml
    
    with open("configs/purchase_order.yaml", 'r') as f:
        config_dict = yaml.safe_load(f)
    
    with open("configs/purchase_order.json", 'w') as f:
        json.dump(config_dict, f, indent=2)
    
    print("📄 Fichier JSON créé depuis YAML\n")
    
    # Charger depuis JSON
    config = BODConfigLoader.from_json("configs/purchase_order.json")
    
    parser = BODParser()
    csv_output = parser.parse_and_convert(xml_content, config)
    
    print(csv_output)  # ← Cette ligne manquait !
    print("\n✅ Config JSON chargée et utilisée avec succès !\n")

if __name__ == "__main__":
    print("\n🚀 Test du BODConfigLoader\n")
    
    try:
        test_from_yaml()
        test_from_json()
        
        print("=" * 80)
        print("✅ TOUS LES TESTS SONT RÉUSSIS !")
        print("=" * 80)
        print("\n💡 Maintenant tu peux :")
        print("   - Modifier configs/purchase_order.yaml sans toucher au code")
        print("   - Créer de nouvelles configs pour d'autres BODs")
        print("   - Stocker les configs sur S3 pour un accès centralisé")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()