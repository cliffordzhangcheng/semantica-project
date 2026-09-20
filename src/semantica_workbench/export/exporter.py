#!/usr/bin/env python3
"""Export module for canonical graphs"""
from pathlib import Path


class GraphExporter:
    """Export canonical graph to various formats"""
    
    SUPPORTED_FORMATS = {"json", "graphml", "ttl"}
    
    def export(self, graph: dict, output_path: Path, fmt: str) -> bool:
        """Export graph to specified format"""
        if fmt not in self.SUPPORTED_FORMATS:
            return False
        
        try:
            if fmt == "json":
                return self._export_json(graph, output_path)
            elif fmt == "graphml":
                return self._export_graphml(graph, output_path)
            elif fmt == "ttl":
                return self._export_ttl(graph, output_path)
        except Exception:
            return False
        return False
    
    def _export_json(self, graph: dict, output_path: Path) -> bool:
        """Export as JSON"""
        import json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        return True
    
    def _export_graphml(self, graph: dict, output_path: Path) -> bool:
        """Export as GraphML"""
        import xml.etree.ElementTree as ET
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create GraphML structure
        graphml = ET.Element("graphml")
        graph_elem = ET.SubElement(graphml, "graph", edgedefault="undirected")
        
        # Add nodes
        for entity in graph.get("entities", []):
            node = ET.SubElement(graph_elem, "node", id=entity["id"])
            ET.SubElement(node, "data", key="label").text = entity.get("type", "")
            ET.SubElement(node, "data", key="text").text = entity.get("text_basis", "")
        
        # Add edges
        for rel in graph.get("relationships", []):
            edge = ET.SubElement(graph_elem, "edge", 
                               source=rel.get("source_id", ""),
                               target=rel.get("target_id", ""))
            ET.SubElement(edge, "data", key="type").text = rel.get("type", "")
        
        tree = ET.ElementTree(graphml)
        tree.write(str(output_path), encoding="utf-8", xml_declaration=True)
        return True
    
    def _export_ttl(self, graph: dict, output_path: Path) -> bool:
        """Export as Turtle RDF"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = ["@prefix ex: <http://example.org/> .", ""]
        
        for entity in graph.get("entities", []):
            eid = entity["id"]
            etype = entity.get("type", "Unknown")
            lines.append(f"ex:{eid} a ex:{etype} ;")
            if "text_basis" in entity:
                lines.append(f"    ex:text \"{entity['text_basis']}\" ;")
            lines.append(f"    .")
        
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return True
