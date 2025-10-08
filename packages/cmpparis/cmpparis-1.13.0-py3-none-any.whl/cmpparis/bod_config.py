"""
Module de configuration BOD

Définit les configurations de mapping pour différents types de BOD, incluant
les chemins XPath, les correspondances de champs et les transformateurs
éventuels pour la conversion en CSV.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class BODConfig:
    """Configuration pour l'analyse BOD et la conversion CSV.

    Attributs:
        header_xpath (str): XPath vers l'en-tête.
        lines_xpath (str): XPath vers les lignes.
        header_mapping (Dict[str, Any]): Mapping des champs d'en-tête CSV → XPath/attribut.
        line_mapping (Dict[str, Any]): Mapping des champs de ligne CSV → XPath/attribut.
        header_transformers (Optional[Dict[str, Callable]]): Transformateurs pour l'en-tête.
        line_transformers (Optional[Dict[str, Callable]]): Transformateurs pour les lignes.
        csv_fieldnames (Optional[List[str]]): Liste des colonnes CSV (ordre).
        flatten_mode (str): Mode d'aplatissement (``duplicate_header``, ``header_only``, ``lines_only``).
    """
    # XPath configurations
    header_xpath: str
    lines_xpath: str
    
    # Field mappings
    header_mapping: Dict[str, Any]
    line_mapping: Dict[str, Any]
    
    # Optional transformers
    header_transformers: Optional[Dict[str, Callable]] = None
    line_transformers: Optional[Dict[str, Callable]] = None
    
    # CSV configuration
    csv_fieldnames: Optional[List[str]] = None
    flatten_mode: str = "duplicate_header"  # duplicate_header, header_only, lines_only
    
    def __post_init__(self):
        """Génère automatiquement les entêtes CSV si non fournies.

        Si ``csv_fieldnames`` est ``None``, concatène les clés de
        ``header_mapping`` et ``line_mapping`` pour déterminer l'ordre des
        colonnes.
        """
        if self.csv_fieldnames is None:
            self.csv_fieldnames = list(self.header_mapping.keys()) + list(self.line_mapping.keys())


# Exemple: Configuration pour Purchase Order
PURCHASE_ORDER_CONFIG = BODConfig(
    header_xpath=".//ns:PurchaseOrderHeader",
    lines_xpath=".//ns:PurchaseOrderLine",
    
    header_mapping={
        "order_number": ".//ns:DocumentID/ns:ID",
        "order_date": ".//ns:DocumentDateTime",
        "supplier_id": ".//ns:SupplierParty/ns:PartyIDs/ns:ID",
        "supplier_name": ".//ns:SupplierParty/ns:Name",
        "ship_to_id": ".//ns:ShipToParty/ns:PartyIDs/ns:ID",
        "ship_to_name": ".//ns:ShipToParty/ns:Name",
        "currency": {"xpath": ".//ns:ExtendedAmount", "attribute": "currencyID"},
        "total_amount": ".//ns:ExtendedAmount",
        "incoterm": ".//ns:TransportationTerm/ns:IncotermsCode",
        "payment_term": ".//ns:PaymentTerm/ns:PaymentTermCode",
        "requested_ship_date": ".//ns:RequestedShipDateTime",
        "promised_delivery_date": ".//ns:PromisedDeliveryDateTime",
        "status": ".//ns:Status/ns:Code",
    },
    
    line_mapping={
        "line_number": ".//ns:LineNumber",
        "item_id": ".//ns:Item/ns:ItemID/ns:ID",
        "item_description": ".//ns:Item/ns:Description",
        "gtin": ".//ns:Item/ns:GTIN",
        "quantity": ".//ns:Quantity",
        "unit": {"xpath": ".//ns:Quantity", "attribute": "unitCode"},
        "unit_price": ".//ns:UnitPrice/ns:Amount",
        "line_total": ".//ns:ExtendedAmount",
        "required_delivery_date": ".//ns:RequiredDeliveryDateTime",
        "line_status": ".//ns:Status/ns:Code",
        "country_of_origin": ".//ns:Item/ns:Classification[@type='Country of Origin']/ns:Codes/ns:Code",
    },
    
    header_transformers={
        "order_date": lambda x: x.split('T')[0] if x else "",  # Format date
        "requested_ship_date": lambda x: x.split('T')[0] if 'T' in x else x,
        "promised_delivery_date": lambda x: x.split('T')[0] if 'T' in x else x,
    },
    
    line_transformers={
        "required_delivery_date": lambda x: x.split('T')[0] if 'T' in x else x,
    }
)