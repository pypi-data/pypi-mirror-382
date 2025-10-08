"""
This script adds more ontology alignments to ../authors/authors.ttl, ../works/works.ttl, ../relations/relations.ttl or ../merge/all.ttl 
and adds new identifiers from DBpedia, GeoNames etc.

"""

from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL
from rdflib.collection import Collection
import sys
import re
import time
from typing import Dict, Any, Iterable, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import argparse
from pathlib import Path

# Namespaces 
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
ECRM = Namespace("http://erlangen-crm.org/current/")
FRBROO = Namespace("http://iflastandards.info/ns/fr/frbr/frbroo/")
EFRBROO = Namespace("http://erlangen-crm.org/efrbroo/")
LRMOO = Namespace("http://iflastandards.info/ns/lrm/lrmoo/")
INTRO = Namespace("https://w3id.org/lso/intro/currentbeta#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SAPPHO   = Namespace("https://sappho-digital.com/")
SAPPHO_PROP   = Namespace("https://sappho-digital.com/property/")

BIBO = Namespace("http://purl.org/ontology/bibo/")
CITO = Namespace("http://purl.org/spar/cito/")
DC = Namespace("http://purl.org/dc/terms/")
DOCO = Namespace("http://purl.org/spar/doco/")
FABIO = Namespace("http://purl.org/spar/fabio/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
GOLEM = Namespace("https://ontology.golemlab.eu/")
DRACOR = Namespace("http://dracor.org/ontology#")
INTERTEXT_AB = Namespace("https://intertextuality.org/abstract#")
INTERTEXT_TX = Namespace("https://intertextuality.org/extensions/text#")
INTERTEXT_AF = Namespace("https://intertextuality.org/extensions/artifacts#")
INTERTEXT_MT = Namespace("https://intertextuality.org/extensions/motifs#")
MIMOTEXT = Namespace("http://data.mimotext.uni-trier.de/entity/")
ONTOPOETRY_CORE = Namespace("http://postdata.linhd.uned.es/ontology/postdata-core#")
ONTOPOETRY_ANALYSIS = Namespace("http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#")
SCHEMA = Namespace("https://schema.org/")

# HTTP helpers
SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "SapphoMapAndAlignBot/1.0 (laura.untner@fu-berlin.de)"
HTTP_TIMEOUT = 120
MAX_RETRIES = 5

def _parse_retry_after(header_val: str) -> Optional[float]:
    if not header_val:
        return None
    header_val = header_val.strip()
    if header_val.isdigit():
        return float(header_val)
    try:
        dt = parsedate_to_datetime(header_val)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
    except Exception:
        return None

def _make_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update({"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT})
    retry = Retry(total=0, respect_retry_after_header=True, backoff_factor=0,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(["GET"]), raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    sess.mount("https://", adapter); sess.mount("http://", adapter)
    return sess

_SESSION = _make_session()

def _sparql_query(query: str, *, max_retries: int = MAX_RETRIES) -> Dict[str, Any]:
    tries = 0
    while True:
        tries += 1
        resp = _SESSION.get(SPARQL_URL, params={"query": query}, timeout=HTTP_TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            ra = _parse_retry_after(resp.headers.get("Retry-After", "")) or 5.0
            print(f"429 Too Many Requests – waiting {ra:.1f}s (try {tries}/{max_retries})")
            if tries >= max_retries:
                resp.raise_for_status()
            time.sleep(ra); continue
        if 500 <= resp.status_code < 600:
            ra = _parse_retry_after(resp.headers.get("Retry-After", "")) or min(10.0, 1.5 ** (tries - 1))
            print(f"{resp.status_code} Server error – waiting {ra:.1f}s (try {tries}/{max_retries})")
            if tries >= max_retries:
                resp.raise_for_status()
            time.sleep(ra); continue
        resp.raise_for_status()

# Mapping

def normalize_uri(raw, prefix_map):
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if ":" in raw:
        prefix, local = raw.split(":", 1)
        base = prefix_map.get(prefix)
        if base:
            return base + local
    return raw

def query_wikidata_batch(qids): 
    prefix_map = {
        "schema":  "https://schema.org/",
        "dbpedia": "https://dbpedia.org/"
    }

    values = " ".join(f"wd:{qid}" for qid in qids)
    query = f"""
    PREFIX wd:  <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?item ?schemaOrg ?dbpedia ?gnd ?viaf ?geonames ?grWork WHERE {{
      VALUES ?item {{ {values} }}
      OPTIONAL {{
        ?item wdt:P2888 | wdt:P1709 ?link1 .
        FILTER(STRSTARTS(STR(?link1),"https://schema.org/"))
        BIND(STR(?link1) AS ?schemaOrg)
      }}
      OPTIONAL {{
        ?item wdt:P2888 | wdt:P1709 ?link2 .
        FILTER(STRSTARTS(STR(?link2),"https://dbpedia.org/"))
        BIND(STR(?link2) AS ?dbpedia)
      }}
      OPTIONAL {{ ?item wdt:P227  ?gnd      }}
      OPTIONAL {{ ?item wdt:P214  ?viaf     }}
      OPTIONAL {{ ?item wdt:P1566 ?geonames }}
      OPTIONAL {{ ?item wdt:P8383 ?grWork   }}
    }}
    """
    results = _sparql_query(query)

    batch_ids = {
        qid: { 'schema':[], 'dbpedia':[], 'gnd':[], 'viaf':[], 'geonames':[], 'goodreads':[] }
        for qid in qids
    }

    for row in results['results']['bindings']:
        uri_item = row['item']['value']
        qid = uri_item.rsplit("/", 1)[1]

        if 'schemaOrg' in row:
            raw = row['schemaOrg']['value']
            batch_ids[qid]['schema'].append(normalize_uri(raw, prefix_map))

        if 'dbpedia' in row:
            raw = row['dbpedia']['value']
            batch_ids[qid]['dbpedia'].append(normalize_uri(raw, prefix_map))

        if 'gnd' in row:
            batch_ids[qid]['gnd'].append(f"http://d-nb.info/gnd/{row['gnd']['value']}")
        
        if 'viaf' in row:
            batch_ids[qid]['viaf'].append(f"http://viaf.org/viaf/{row['viaf']['value']}")
        
        if 'geonames' in row:
            batch_ids[qid]['geonames'].append(f"http://sws.geonames.org/{row['geonames']['value']}/")
        
        if 'grWork' in row:
            batch_ids[qid]['goodreads'].append(f"https://www.goodreads.com/work/{row['grWork']['value']}")

    return batch_ids

# Get creation year
def extract_year(label_lit):
    return int(str(label_lit))

def get_creation_year(g, expr):
    # Expression_Creation
    for ec in g.objects(expr, LRMOO.R17i_was_created_by):
        for ts in g.objects(ec, ECRM["P4_has_time-span"]):
            return extract_year(g.value(ts, RDFS.label))
    # Manifestation_Creation fallback
    for manif in g.objects(expr, LRMOO.R4i_is_embodied_in):
        for mc in g.subjects(LRMOO.R24_created, manif):
            for ts in g.objects(mc, ECRM["P4_has_time-span"]):
                return extract_year(g.value(ts, RDFS.label))
    return None

# Arguments
def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Add ontology alignments and external identifiers (DBpedia, GeoNames, …) to a TTL file."
    )
    p.add_argument("--input",  type=Path, help="Input TTL (e.g. examples/outputs/all.ttl)")
    p.add_argument("--output", type=Path, help="Output TTL (default: <input>_mapped-and-aligned.ttl)")
    p.add_argument("--log-level", default="INFO", help="Logging level (default: INFO)")
    return p.parse_args(argv)

# Run script
def main(argv=None):
    args = parse_args(argv)

    import logging
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format="%(levelname)s:%(name)s:%(message)s")

    if args.input is None:
        candidates = [
            Path("examples/outputs/all.ttl"),
            Path("examples/outputs/authors.ttl"),
            Path("examples/outputs/works.ttl"),
            Path("examples/outputs/relations.ttl"),
        ]
        for c in candidates:
            if c.exists():
                args.input = c
                break
        if args.input is None:
            raise SystemExit("--input is required (no default TTL found in examples/outputs)")

    if args.output is None:
        args.output = args.input.with_name(args.input.stem + "_mapped-and-aligned.ttl")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    g = Graph()
    g.parse(str(args.input), format="turtle")
    print(f"✅ Loaded {args.input}.")

    # Mapping
    
    prefix_map = {
        "schema":  "https://schema.org/",
        "dbpedia": "https://dbpedia.org/"
    }

    wikidata_pattern = re.compile(r"^http://www\.wikidata\.org/entity/(Q\d+)$")
    subjects_by_qid = {}
    for subj, _, obj in g.triples((None, OWL.sameAs, None)):
        m = wikidata_pattern.match(str(obj))
        if m:
            subjects_by_qid.setdefault(m.group(1), []).append(subj)

    qids = list(subjects_by_qid.keys())
    batch_results = query_wikidata_batch(qids) if qids else {}

    for qid, subjects in subjects_by_qid.items():
        for uri_list in batch_results.get(qid, {}).values():
            for raw in uri_list:
                uri = normalize_uri(raw, prefix_map)
                if uri.startswith("http://") or uri.startswith("https://"):
                    new_obj = URIRef(uri)
                    for subj in subjects:
                        if (subj, OWL.sameAs, new_obj) not in g:
                            g.add((subj, OWL.sameAs, new_obj))
    
    # Alignment

    g.bind("sappho_prop", SAPPHO_PROP)
    g.bind("ecrm", ECRM)
    g.bind("crm", CRM)
    g.bind("frbroo", FRBROO)
    g.bind("efrbroo", EFRBROO)
    g.bind("lrmoo", LRMOO)
    g.bind("intro", INTRO)
    g.bind("skos", SKOS)
    
    g.bind("bibo", BIBO)
    g.bind("cito", CITO)
    g.bind("dc", DC)
    g.bind("doco", DOCO)
    g.bind("dracor", DRACOR)
    g.bind("fabio", FABIO)
    g.bind("foaf", FOAF)
    g.bind("golem", GOLEM)
    g.bind("intertext_ab", INTERTEXT_AB)
    g.bind("intertext_tx", INTERTEXT_TX)
    g.bind("intertext_af", INTERTEXT_AF)
    g.bind("intertext_mt", INTERTEXT_MT)
    g.bind("mimotext", MIMOTEXT)
    g.bind("ontopoetry_core", ONTOPOETRY_CORE)
    g.bind("ontopoetry_analysis", ONTOPOETRY_ANALYSIS)
    g.bind("schema", SCHEMA)

    ## Classes ##
    
    # ecrm:E21_Person
    if any(g.triples((None, RDF.type, ECRM.E21_Person))):
        g.add((DRACOR.author, SKOS.broadMatch, ECRM.E21_Person))
        g.add((ECRM.E21_Person, SKOS.broadMatch, FOAF.Agent))
        g.add((MIMOTEXT.Q11, SKOS.broadMatch, ECRM.E21_Person)) # author
        g.add((MIMOTEXT.Q10, SKOS.closeMatch, ECRM.E21_Person)) # person
        g.add((ONTOPOETRY_CORE.Person, SKOS.closeMatch, ECRM.E21_Person)) 
    
    # ecrm:E35_Title
    if any(g.triples((None, RDF.type, ECRM.E35_Title))):
        g.add((DOCO.Title, SKOS.closeMatch, ECRM.E35_Title))
    
    # ecrm:E38_Image
    if any(g.triples((None, RDF.type, ECRM.E38_Image))):
        g.add((BIBO.Image, SKOS.closeMatch, ECRM.E38_Image))
        g.add((FOAF.Image, SKOS.closeMatch, ECRM.E38_Image))
    
    # ecrm:E40_Legal_Body
    if any(g.triples((None, RDF.type, ECRM.E40_Legal_Body))):
        g.add((ECRM.E40_Legal_Body, SKOS.broadMatch, FOAF.Agent))
        g.add((ONTOPOETRY_CORE.Organisation, SKOS.broadMatch, ECRM.E40_Legal_Body))
    
    # ecrm:E52_Time-Span
    if any(g.triples((None, RDF.type, ECRM["E52_Time-Span"]))):
        g.add((DC.PeriodOfTime, SKOS.closeMatch, ECRM["E52_Time-Span"]))
        g.add((ONTOPOETRY_CORE.TimeSpan, SKOS.closeMatch, ECRM["E52_Time-Span"]))

    # ecrm:E53_Place
    if any(g.triples((None, RDF.type, ECRM.E53_Place))):
        g.add((DC.Location, SKOS.closeMatch, ECRM.E53_Place))
        g.add((MIMOTEXT.Q26, SKOS.closeMatch, ECRM.E53_Place)) # spatial concept
        g.add((ONTOPOETRY_CORE.Place, SKOS.closeMatch, ECRM.E53_Place))
        
    # ecrm:E55_Type
    if any(g.triples((None, RDF.type, ECRM.E55_Type))):
        g.add((DRACOR.genre, SKOS.broadMatch, ECRM.E55_Type))
        g.add((INTERTEXT_TX.TextGenre, SKOS.broadMatch, ECRM.E55_Type))
        g.add((MIMOTEXT.Q33, SKOS.broadMatch, ECRM.E55_Type)) # genre

    # ecrm:E67_Birth
    if any(g.triples((None, RDF.type, ECRM.E67_Birth))):
        g.add((ONTOPOETRY_CORE.Birth, SKOS.closeMatch, ECRM.E67_Birth))
    
    # ecrm:E69_Death
    if any(g.triples((None, RDF.type, ECRM.E69_Death))):
        g.add((ONTOPOETRY_CORE.Death, SKOS.closeMatch, ECRM.E69_Death))
        
    # ecrm:E73_Information_Object
    if any(g.triples((None, RDF.type, ECRM.E73_Information_Object))):
        g.add((FABIO.DigitalItem, SKOS.broadMatch, ECRM.E73_Information_Object))  
    
    # lrmoo:F1_Work
    if any(g.triples((None, RDF.type, LRMOO.F1_Work))):
        g.add((FABIO.Work, SKOS.broadMatch, LRMOO.F1_Work))
        g.add((FABIO.LiteraryArtisticWork, SKOS.broadMatch, LRMOO.F1_Work))
        g.add((ONTOPOETRY_CORE.Work, SKOS.closeMatch, LRMOO.F1_Work))
        g.add((ONTOPOETRY_CORE.PoeticWork, SKOS.broadMatch, LRMOO.F1_Work))
    
    # lrmoo:F2_Expression
    if any(g.triples((None, RDF.type, LRMOO.F2_Expression))):
        g.add((LRMOO.F2_Expression, SKOS.broadMatch, FOAF.Document))
        g.add((BIBO.Manuscript, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((DRACOR.play, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((FABIO.Expression, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((INTERTEXT_TX.Text, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((INTERTEXT_TX.SingleText, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((INTERTEXT_AF.Work, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((INTERTEXT_AB.Reference, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((MIMOTEXT.Q2, SKOS.broadMatch, LRMOO.F2_Expression)) # literary work
        g.add((ONTOPOETRY_CORE.Expression, SKOS.closeMatch, LRMOO.F2_Expression))
        g.add((ONTOPOETRY_ANALYSIS.Intertextuality, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((ONTOPOETRY_ANALYSIS.Source, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((ONTOPOETRY_ANALYSIS.Redaction, SKOS.broadMatch, LRMOO.F2_Expression))
        g.add((ONTOPOETRY_ANALYSIS.Excerpt, SKOS.broadMatch, LRMOO.F2_Expression))
    
    # lrmoo:F3_Manifestation
    if any(g.triples((None, RDF.type, LRMOO.F3_Manifestation))):
        g.add((BIBO.Book, SKOS.broadMatch, LRMOO.F3_Manifestation))
        g.add((DC.BibliographicResource, SKOS.broadMatch, LRMOO.F3_Manifestation))
        g.add((FABIO.Manifestation, SKOS.broadMatch, LRMOO.F3_Manifestation))
        g.add((LRMOO.F3_Manifestation, SKOS.broadMatch, FOAF.Document))
    
    # lrmoo:F5_Item
    if any(g.triples((None, RDF.type, LRMOO.F5_Item))):
        g.add((FABIO.Item, SKOS.broadMatch, LRMOO.F5_Item))     
        g.add((LRMOO.F5_Item, SKOS.broadMatch, FOAF.Document)) 
    
    # lrmoo:F27_Work_Creation
    if any(g.triples((None, RDF.type, LRMOO.F27_Work_Creation))):
        g.add((ONTOPOETRY_CORE.WorkConception, SKOS.closeMatch, LRMOO.F27_Work_Creation))

    # lrmoo:F28_Expression_Creation
    if any(g.triples((None, RDF.type, LRMOO.F28_Expression_Creation))):
        g.add((ONTOPOETRY_CORE.ExpressionCreation, SKOS.closeMatch, LRMOO.F28_Expression_Creation))
    
    # intro:INT1_Segment
    if any(g.triples((None, RDF.type, INTRO.INT1_Segment))):
        g.add((INTERTEXT_AF.Segment, SKOS.broadMatch, INTRO.INT1_Segment))
    
    # intro:INT2_ActualizationOfFeature
    if any(g.triples((None, RDF.type, INTRO.INT2_ActualizationOfFeature))):
        g.add((FRBROO.F38_Character, SKOS.broadMatch, INTRO.INT2_ActualizationOfFeature))
        g.add((EFRBROO.F38_Character, SKOS.broadMatch, INTRO.INT2_ActualizationOfFeature))
        g.add((DRACOR.character, SKOS.broadMatch, INTRO.INT2_ActualizationOfFeature))
        g.add((GOLEM.G1_Character, SKOS.broadMatch, INTRO.INT2_ActualizationOfFeature))
        g.add((GOLEM.G7_Narrative_Sequence, SKOS.broadMatch, INTRO.INT2_ActualizationOfFeature))
        g.add((ONTOPOETRY_CORE.Character, SKOS.broadMatch, INTRO.INT2_ActualizationOfFeature))
    
    # intro:INT4_Feature
    if any(g.triples((None, RDF.type, INTRO.INT4_Feature))):
        g.add((INTRO.INT4_Feature, SKOS.broadMatch, INTERTEXT_AB.Mediator))
        g.add((GOLEM.G9_Narrative_Unit, SKOS.broadMatch, INTRO.INT4_Feature))
    
    # intro:INT6_Architext
    if any(g.triples((None, RDF.type, INTRO.INT6_Architext))):
        g.add((INTERTEXT_AF.System, SKOS.broadMatch, INTRO.INT6_Architext))
    
    # intro:INT11_TypeOfInterrelation
    if any(g.triples((None, RDF.type, INTRO.INT11_TypeOfInterrelation))):
        g.add((INTERTEXT_AB.IntertexualSpecification, SKOS.closeMatch, INTRO.INT11_TypeOfInterrelation))
    
    # intro:INT21_TextPassage
    if any(g.triples((None, RDF.type, INTRO.INT21_TextPassage))):
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.Part))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.BackMatter))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.BodyMatter))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.CaptionedBox))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.Chapter))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.ComplexRunInQuotation))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.Footnote))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.Formula))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.FormulaBox))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.FrontMatter))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.List))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.Section))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, DOCO.Table))
        g.add((INTRO.INT21_TextPassage, SKOS.broadMatch, INTERTEXT_AB.Mediator))
        g.add((BIBO.Quote, SKOS.broadMatch, INTRO.INT21_TextPassage))
        g.add((FABIO.Quotation, SKOS.broadMatch, INTRO.INT21_TextPassage))
        g.add((INTERTEXT_TX.TextSegment, SKOS.closeMatch, INTRO.INT21_TextPassage))
    
    # intro:INT31_IntertextualRelation
    if any(g.triples((None, RDF.type, INTRO.INT31_IntertextualRelation))):
        g.add((INTERTEXT_AB.IntertexualRelation, SKOS.closeMatch, INTRO.INT31_IntertextualRelation))
    
    # intro:INT_Character
    if any(g.triples((None, RDF.type, INTRO.INT_Character))):
        g.add((GOLEM["G0_Character-Stoff"], SKOS.closeMatch, INTRO.INT_Character))
        g.add((FRBROO.F38_Character, SKOS.broadMatch, INTRO.INT_Character))
        g.add((EFRBROO.F38_Character, SKOS.broadMatch, INTRO.INT_Character))
        g.add((DRACOR.character, SKOS.broadMatch, INTRO.INT_Character))
        g.add((ONTOPOETRY_CORE.Character, SKOS.broadMatch, INTRO.INT_Character))
    
    # intro:INT_Plot
    if any(g.triples((None, RDF.type, INTRO.INT_Plot))):
        g.add((GOLEM.G14_Narrative_Stoff, SKOS.closeMatch, INTRO.INT_Plot))
    
    # intro:INT_Motif
    if any(g.triples((None, RDF.type, INTRO.INT_Motif))):
        g.add((INTRO.INT_Motif, SKOS.broadMatch, INTERTEXT_MT.Motive))
    
    # intro:INT_Topic
    if any(g.triples((None, RDF.type, INTRO.INT_Topic))):
        g.add((MIMOTEXT.Q20, SKOS.closeMatch, INTRO.INT_Topic)) # thematic concept
    
    ## Properties ##
    
    # ecrm:P1_is_identified_by
    if any(g.triples((None, ECRM.P1_is_identified_by, None))):
        g.add((DC.identifier, SKOS.broadMatch, ECRM.P1_is_identified_by))
    
    # ecrm:P2_has_type
    if any(g.triples((None, ECRM.P2_has_type, None))):
        g.add((DC.type, SKOS.broadMatch, ECRM.P2_has_type))
        g.add((DRACOR.has_genre, SKOS.broadMatch, ECRM.P2_has_type))
        g.add((FOAF.gender, SKOS.broadMatch, ECRM.P2_has_type))
        g.add((MIMOTEXT.P12, SKOS.broadMatch, ECRM.P2_has_type)) # genre
        g.add((ONTOPOETRY_CORE.gender, SKOS.broadMatch, ECRM.P2_has_type))
        g.add((ONTOPOETRY_CORE.genre, SKOS.broadMatch, ECRM.P2_has_type))
        g.add((SCHEMA.genre, SKOS.broadMatch, ECRM.P2_has_type))
    
    # ecrm:P4_has_time-span
    if any(g.triples((None, ECRM["P4_has_time-span"], None))):
        g.add((DC.date, SKOS.broadMatch, ECRM["P4_has_time-span"]))
        g.add((DC.created, SKOS.broadMatch, ECRM["P4_has_time-span"]))
        g.add((DC.dateCopyrighted, SKOS.broadMatch, ECRM["P4_has_time-span"]))
        g.add((DRACOR.printYear, SKOS.broadMatch, ECRM["P4_has_time-span"]))
        g.add((DRACOR.writtenYear, SKOS.broadMatch, ECRM["P4_has_time-span"]))
        g.add((MIMOTEXT.P9, SKOS.broadMatch, ECRM["P4_has_time-span"])) # publication date
        g.add((ONTOPOETRY_CORE.hasTimeSpan, SKOS.closeMatch, ECRM["P4_has_time-span"]))
        g.add((SCHEMA.dateCreated, SKOS.broadMatch, ECRM["P4_has_time-span"]))
        g.add((SCHEMA.datePublished, SKOS.broadMatch, ECRM["P4_has_time-span"]))
    
    # ecrm:P4i_is_time-span_of
    if any(g.triples((None, ECRM["P4i_is_time-span_of"], None))):
        g.add((ONTOPOETRY_CORE.isTimeSpanOf, SKOS.closeMatch, ECRM["P4i_is_time-span_of"]))
    
    # ecrm:P7_took_place_at
    if any(g.triples((None, ECRM.P7_took_place_at, None))):
        g.add((FABIO.hasPlaceOfPublication, SKOS.broadMatch, ECRM.P7_took_place_at))
        g.add((MIMOTEXT.P10, SKOS.broadMatch, ECRM.P7_took_place_at)) # publication place
        g.add((ONTOPOETRY_CORE.tookPlaceAt, SKOS.closeMatch, ECRM.P7_took_place_at))
        g.add((SCHEMA.locationCreated, SKOS.broadMatch, ECRM.P7_took_place_at))
    
    # ecrm:P7i_witnessed
    if any(g.triples((None, ECRM.P7i_witnessed, None))):
        g.add((ONTOPOETRY_CORE.witnessed, SKOS.closeMatch, ECRM.P7i_witnessed))
    
    # ecrm:P14_carried_out_by
    if any(g.triples((None, ECRM.P14_carried_out_by, None))):
        g.add((BIBO.editor, SKOS.broadMatch, ECRM.P14_carried_out_by))
        g.add((DRACOR.has_author, SKOS.broadMatch, ECRM.P14_carried_out_by))
        g.add((FOAF.maker, SKOS.broadMatch, ECRM.P14_carried_out_by))
        g.add((MIMOTEXT.P5, SKOS.broadMatch, ECRM.P14_carried_out_by)) # has author
        g.add((SCHEMA.author, SKOS.broadMatch, ECRM.P14_carried_out_by))
        g.add((SCHEMA.creator, SKOS.broadMatch, ECRM.P14_carried_out_by))
    
    # ecrm:P14i_performed
    if any(g.triples((None, ECRM.P14i_performed, None))):
        g.add((DC.creator, SKOS.broadMatch, ECRM.P14i_performed))
        g.add((DC.publisher, SKOS.broadMatch, ECRM.P14i_performed))
        g.add((FOAF.made, SKOS.broadMatch, ECRM.P14i_performed))
        g.add((MIMOTEXT.P7, SKOS.broadMatch, ECRM.P14i_performed)) # author of
    
    # ecrm:P98i_was_born
    if any(g.triples((None, ECRM.P98i_was_born, None))):
        g.add((ONTOPOETRY_CORE.wasBorn, SKOS.closeMatch, ECRM.P98i_was_born))
    
    # ecrm:P98_brought_into_life
    if any(g.triples((None, ECRM.P98_brought_into_life, None))):
        g.add((ONTOPOETRY_CORE.broughtIntoLife, SKOS.closeMatch, ECRM.P98_brought_into_life))
    
    # ecrm:P100_was_death_of
    if any(g.triples((None, ECRM.P100_was_death_of, None))):
        g.add((ONTOPOETRY_CORE.wasDeathOf, SKOS.closeMatch, ECRM.P100_was_death_of))
    
    # ecrm:P100i_died_in
    if any(g.triples((None, ECRM.P100i_died_in, None))):
        g.add((ONTOPOETRY_CORE.diedIn, SKOS.closeMatch, ECRM.P100i_died_in))
        
    # ecrm:P102_has_title
    if any(g.triples((None, ECRM.P102_has_title, None))):
        g.add((DC.title, SKOS.broadMatch, ECRM.P102_has_title))
        g.add((MIMOTEXT.P4, SKOS.broadMatch, ECRM.P102_has_title)) # title
    
    # ecrm:P131_is_identified_by
    if any(g.triples((None, ECRM.P131_is_identified_by, None))):
        g.add((FOAF.name, SKOS.broadMatch, ECRM.P131_is_identified_by))
        g.add((MIMOTEXT.P8, SKOS.broadMatch, ECRM.P131_is_identified_by)) # name
    
    # ecrm:P138i_has_representation
    if any(g.triples((None, ECRM.P138i_has_representation, None))):
        g.add((FOAF.img, SKOS.broadMatch, ECRM.P138i_has_representation))
        g.add((MIMOTEXT.P21, SKOS.broadMatch, ECRM.P138i_has_representation)) # full work available at URL
    
    # lrmoo:R3_is_realised_in
    if any(g.triples((None, LRMOO.R3_is_realised_in, None))):
        g.add((FABIO.realization, SKOS.closeMatch, LRMOO.R3_is_realised_in))
    
    # lrmoo:R4i_is_embodied_in
    if any(g.triples((None, LRMOO.R4i_is_embodied_in, None))):
        g.add((FABIO.embodiment, SKOS.closeMatch, LRMOO.R4i_is_embodied_in))
    
    # lrmoo:R7i_is_exemplified_by
    if any(g.triples((None, LRMOO.R7i_is_exemplified_by, None))):
        g.add((FABIO.exemplar, SKOS.closeMatch, LRMOO.R7i_is_exemplified_by))
    
    # lrmoo:R16_created
    if any(g.triples((None, LRMOO.R16_created, None))):
        g.add((ONTOPOETRY_CORE.initiated, SKOS.closeMatch, LRMOO.R16_created))
    
    # lrmoo:R16i_was_created_by
    if any(g.triples((None, LRMOO.R16i_was_created_by, None))):
        g.add((ONTOPOETRY_CORE.wasInitiatedBy, SKOS.closeMatch, LRMOO.R16i_was_created_by))
    
    # lrmoo:R17_created
    if any(g.triples((None, LRMOO.R17_created, None))):
        g.add((ONTOPOETRY_CORE.createdExpressionFromExpressionCreation, SKOS.closeMatch, LRMOO.R17_created))
    
    # lrmoo:R17i_was_created_by
    if any(g.triples((None, LRMOO.R17i_was_created_by, None))):
        g.add((ONTOPOETRY_CORE.wasCreatedByExpressionCreationForExpression, SKOS.closeMatch, LRMOO.R17i_was_created_by))
    
    # lrmoo:R19_created_a_realisation_of
    if any(g.triples((None, LRMOO.R19_created_a_realisation_of, None))):
        g.add((ONTOPOETRY_CORE.createdWorkByExpressionCreation, SKOS.closeMatch, LRMOO.R19_created_a_realisation_of))
    
    # lrmoo:R19i_was_realised_through
    if any(g.triples((None, LRMOO.R19i_was_realised_through, None))):
        g.add((ONTOPOETRY_CORE.realisedThroughExpressionCreation, SKOS.closeMatch, LRMOO.R19i_was_realised_through))
    
    # intro:R12i_isReferredToEntity
    if any(g.triples((None, INTRO.R12i_isReferredToEntity, None))):
        g.add((INTRO.R12i_isReferredToEntity, SKOS.closeMatch, INTERTEXT_AB.there))
    
    # intro:R13i_isReferringEntity
    if any(g.triples((None, INTRO.R13i_isReferringEntity, None))):
        g.add((INTRO.R13i_isReferringEntity, SKOS.closeMatch, INTERTEXT_AB.here))
    
    # intro:R18_showsActualization
    if any(g.triples((None, INTRO.R18_showsActualization, None))):
        g.add((ONTOPOETRY_ANALYSIS.presentsIntertextuality, SKOS.broadMatch, INTRO.R18_showsActualization))
    
    # intro:R18i_actualizationFoundOn
    if any(g.triples((None, INTRO.R18i_actualizationFoundOn, None))):
        g.add((ONTOPOETRY_ANALYSIS.isIntertextualityPresentAt, SKOS.broadMatch, INTRO.R18i_actualizationFoundOn))

    # intro:R19i_isTypeOf
    if any(g.triples((None, INTRO.R19i_isTypeOf, None))):
        g.add((INTERTEXT_AB.specifiedBy, SKOS.broadMatch, INTRO.R19i_isTypeOf))
        g.add((ONTOPOETRY_ANALYSIS.typeOfIntertextuality, SKOS.broadMatch, INTRO.R19i_isTypeOf))
    
    # intro:R22i_relationIsBasedOnSimilarity
    if any(g.triples((None, INTRO.R22i_relationIsBasedOnSimilarity, None))):
        g.add((INTRO.R22i_relationIsBasedOnSimilarity, SKOS.broadMatch, INTERTEXT_AB.mediatedBy))
    
    # intro:R24_hasRelatedEntity
    if any(g.triples((None, INTRO.R24_hasRelatedEntity, None))):
        g.add((INTRO.R24_hasRelatedEntity, SKOS.broadMatch, INTERTEXT_AB.mediatedBy))
    
    # intro:R30_hasTextPassage
    if any(g.triples((None, INTRO.R30_hasTextPassage, None))):
        g.add((INTRO.R30_hasTextPassage, SKOS.broadMatch, DC.hasPart))
        g.add((ONTOPOETRY_ANALYSIS.presentsIntertextuality, SKOS.broadMatch, INTRO.R30_hasTextPassage))
    
    # intro:R30i_isTextPassageOf
    if any(g.triples((None, INTRO.R30i_isTextPassageOf, None))):
        g.add((ONTOPOETRY_ANALYSIS.isIntertextualityPresentAt, SKOS.broadMatch, INTRO.R30i_isTextPassageOf))
    
    # prov:wasDerivedFrom
    if any(g.triples((None, PROV.wasDerivedFrom, None))):
        g.add((DC.source, SKOS.closeMatch, PROV.wasDerivedFrom))
        g.add((MIMOTEXT.P17, SKOS.broadMatch, PROV.wasDerivedFrom)) # reference URL

    ## Complex Properties ##    

    # new properties for F1->F3 (hasManifestation), F1->F5 (hasPortrayal) and F2->F5 (hasRepresentation)
    if (
        any(g.triples((None, RDF.type, LRMOO.F1_Work))) and
        any(g.triples((None, RDF.type, LRMOO.F3_Manifestation)))
    ):
        g.add((SAPPHO_PROP.has_manifestation, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.has_manifestation, RDFS.label, 
            Literal("has manifestation", lang="en")))
        g.add((SAPPHO_PROP.has_manifestation, SKOS.closeMatch, FABIO.hasManifestation))
        g.add((SAPPHO_PROP.has_manifestation, RDFS.domain, LRMOO.F1_Work))
        g.add((SAPPHO_PROP.has_manifestation, RDFS.range,  LRMOO.F3_Manifestation))

        bnode = BNode()
        Collection(g, bnode, [
            LRMOO.R3_is_realised_in,
            LRMOO.R4i_is_embodied_in
        ])
        g.add((SAPPHO_PROP.has_manifestation, OWL.propertyChainAxiom, bnode))
        
        for work in g.subjects(RDF.type, LRMOO.F1_Work):
            for expr in g.objects(work, LRMOO.R3_is_realised_in):
                for mani in g.objects(expr, LRMOO.R4i_is_embodied_in):
                    g.add((work, SAPPHO_PROP.has_manifestation, mani))
  
    if (
        any(g.triples((None, RDF.type, LRMOO.F1_Work))) and
        any(g.triples((None, RDF.type, LRMOO.F5_Item)))
    ):
        g.add((SAPPHO_PROP.has_portrayal, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.has_portrayal, RDFS.label, 
            Literal("has portrayal", lang="en")))
        g.add((SAPPHO_PROP.has_portrayal, SKOS.closeMatch, FABIO.hasPortrayal))
        g.add((SAPPHO_PROP.has_portrayal, RDFS.domain, LRMOO.F1_Work))
        g.add((SAPPHO_PROP.has_portrayal, RDFS.range,  LRMOO.F5_Item))

        bnode = BNode()
        Collection(g, bnode, [
            LRMOO.R3_is_realised_in,
            LRMOO.R4i_is_embodied_in,
            LRMOO.R7i_is_exemplified_by
        ])
        g.add((SAPPHO_PROP.has_portrayal, OWL.propertyChainAxiom, bnode))
        
        for work in g.subjects(RDF.type, LRMOO.F1_Work):
            for expr in g.objects(work, LRMOO.R3_is_realised_in):
                for mani in g.objects(expr, LRMOO.R4i_is_embodied_in):
                    for item in g.objects(mani, LRMOO.R7i_is_exemplified_by):
                        g.add((work, SAPPHO_PROP.has_portrayal, item))

    if (
        any(g.triples((None, RDF.type, LRMOO.F2_Expression))) and
        any(g.triples((None, RDF.type, LRMOO.F5_Item)))
    ):
        g.add((SAPPHO_PROP.has_representation, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.has_representation, RDFS.label, 
            Literal("has representation", lang="en")))
        g.add((SAPPHO_PROP.has_representation, SKOS.closeMatch, FABIO.hasRepresentation))
        g.add((SAPPHO_PROP.has_representation, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.has_representation, RDFS.range,  LRMOO.F5_Item))

        bnode = BNode()
        Collection(g, bnode, [
            LRMOO.R4i_is_embodied_in,
            LRMOO.R7i_is_exemplified_by
        ])
        g.add((SAPPHO_PROP.has_representation, OWL.propertyChainAxiom, bnode))
        
        for expr in g.subjects(RDF.type, LRMOO.F2_Expression):
                for mani in g.objects(expr, LRMOO.R4i_is_embodied_in):
                    for item in g.objects(mani, LRMOO.R7i_is_exemplified_by):
                        g.add((expr, SAPPHO_PROP.has_representation, item))
    
    # sappho_prop:about: expressions that actualize a intro:INT_Topic will be also linked to the topic
    
    # Gather directions (younger/older) first, needed later as well
    directions = []
    
    for rel in g.subjects(RDF.type, INTRO.INT31_IntertextualRelation):
        tp_expr = []
        for tp in g.objects(rel, INTRO.R24_hasRelatedEntity):
            expr = g.value(tp, INTRO.R30i_isTextPassageOf)
            if expr:
                tp_expr.append((tp, expr))

        if len(tp_expr) != 2:
            continue  
        
        exprs = {e for tp, e in tp_expr}
        if len(exprs) != 2:
                continue
                
        (tp1, expr1), (tp2, expr2) = tp_expr[:2]
            
        y1 = get_creation_year(g, expr1)
        y2 = get_creation_year(g, expr2)
        
        if y1 is None or y2 is None:
            continue
        
        if y1 < y2:
            older_expr, younger_expr = expr1, expr2
            older_tp,    younger_tp    = tp1,    tp2
        else:
            older_expr, younger_expr = expr2, expr1
            older_tp,    younger_tp    = tp2,    tp1

        directions.append((younger_expr, older_expr, younger_tp, older_tp))

    if any(g.triples((None, RDF.type, INTRO.INT_Topic))):
        g.add((SAPPHO_PROP.about, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.about, RDFS.label,
            Literal("Link from expression to topic", lang="en")))
        b_about = BNode()
        Collection(g, b_about, [
            INTRO.R18_showsActualization,
            INTRO.R17_actualizesFeature
        ])
        g.add((SAPPHO_PROP.about, OWL.propertyChainAxiom, b_about))
        g.add((SAPPHO_PROP.about, SKOS.closeMatch, DC.subject))
        g.add((SAPPHO_PROP.about, SKOS.closeMatch, FOAF.topic))
        g.add((SAPPHO_PROP.about, SKOS.closeMatch, MIMOTEXT.P36)) # about
        g.add((SAPPHO_PROP.about, SKOS.closeMatch, SCHEMA.about))
        g.add((SAPPHO_PROP.about, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.about, RDFS.range, INTRO.INT_Topic))

        for expr in g.subjects(RDF.type, LRMOO.F2_Expression):
            for act in g.objects(expr, INTRO.R18_showsActualization):
                topic = g.value(act, INTRO.R17_actualizesFeature)
                if topic and (topic, RDF.type, INTRO.INT_Topic) in g:
                    g.add((expr, SAPPHO_PROP.about, topic))

    # sappho_prop:expr_relation: expressions that are linked via intro:INT31 will be linked via this property
    if any(g.triples((None, RDF.type, INTRO.INT31_IntertextualRelation))):
        g.add((SAPPHO_PROP.expr_relation, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.expr_relation, RDFS.label,
            Literal("Relation between two expressions", lang="en")))

        first_elem = BNode()
        g.add((first_elem, OWL.inverseOf, INTRO.R18i_actualizationFoundOn))
        chain_list = [
            first_elem,
            INTRO.R24i_isRelatedEntity,
            INTRO.R24_hasRelatedEntity,
            INTRO.R18i_actualizationFoundOn
        ]
        chain_bnode = BNode()
        Collection(g, chain_bnode, chain_list)
        g.add((SAPPHO_PROP.expr_relation, OWL.propertyChainAxiom, chain_bnode))
        g.add((SAPPHO_PROP.expr_relation, RDF.type, OWL.SymmetricProperty))
        g.add((SAPPHO_PROP.expr_relation, SKOS.closeMatch, DC.relation))
        g.add((SAPPHO_PROP.expr_relation, SKOS.closeMatch, MIMOTEXT.P34))  # relation
        g.add((SAPPHO_PROP.expr_relation, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.expr_relation, RDFS.range,  LRMOO.F2_Expression))
        
        # add directions to intro:INT31_IntertextualRelation
        for rel in g.subjects(RDF.type, INTRO.INT31_IntertextualRelation):
            acts = list(g.objects(rel, INTRO.R24_hasRelatedEntity))
            exprs = {
                expr
                for act in acts
                for expr in g.subjects(INTRO.R18_showsActualization, act)
            }
            for e1 in exprs:
                for e2 in exprs:
                    if e1 != e2:
                        g.add((e1, SAPPHO_PROP.expr_relation, e2))
                        g.add((e2, SAPPHO_PROP.expr_relation, e1))

        # Also materialize younger/older hints if computed
        for younger_expr, older_expr, younger_tp, older_tp in directions:
            g.add((URIRef(str(rel)), INTRO.R13_hasReferringEntity, younger_expr))
            g.add((younger_expr, INTRO.R13i_isReferringEntity, URIRef(str(rel))))
            g.add((URIRef(str(rel)), INTRO.R12_hasReferredToEntity, older_expr))
            g.add((older_expr, INTRO.R12i_isReferredToEntity, URIRef(str(rel))))

    # sappho_prop:expr_possibly_cites / sappho_prop:expr_possibly_cited_by
    # if two expressions have intro:INT21_TextPassages that are part of their intro:INT31, 
    # it is possible (but not necessary) that the younger text cites the older text. 
    # To find out which one is which, the time-spans of the expression or manifestation creations are compared.

    if any(g.triples((None, INTRO.R30i_isTextPassageOf, None))):

        g.add((SAPPHO_PROP.expr_possibly_cites, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.expr_possibly_cites, RDFS.label,
            Literal("Younger expression possibly cites older expression", lang="en")))
        g.add((SAPPHO_PROP.expr_possibly_cites, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.expr_possibly_cites, RDFS.range, LRMOO.F2_Expression))

        inv_rel = BNode(); g.add((inv_rel, OWL.inverseOf, INTRO.R24_hasRelatedEntity))
        inv_tp  = BNode()
        g.add((inv_tp, OWL.inverseOf, INTRO.R30i_isTextPassageOf))

        chain_nodes = [
            INTRO.R30_hasTextPassage, 
            inv_rel,                 
            INTRO.R24_hasRelatedEntity,
            inv_tp                 
    ]
        chain_bnode = BNode(); Collection(g, chain_bnode, chain_nodes)
        
        g.add((SAPPHO_PROP.expr_possibly_cites, OWL.propertyChainAxiom, chain_bnode))

        g.add((SAPPHO_PROP.expr_possibly_cited_by, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.expr_possibly_cites, RDFS.label,
            Literal("Older expression possibly cited by younger expression", lang="en")))
        g.add((SAPPHO_PROP.expr_possibly_cited_by, OWL.inverseOf,
            SAPPHO_PROP.expr_possibly_cites))
        g.add((SAPPHO_PROP.expr_possibly_cited_by, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.expr_possibly_cited_by, RDFS.range, LRMOO.F2_Expression))

        # ecrm alignment
        g.add((SAPPHO_PROP.expr_possibly_cites, RDFS.subPropertyOf, ECRM.P148_has_component))
        g.add((SAPPHO_PROP.expr_possibly_cited_by, RDFS.subPropertyOf, ECRM.P148i_is_component_of))   
                
        g.add((SAPPHO_PROP.expr_possibly_cites, RDFS.subPropertyOf, ECRM.P130_shows_features_of))
        g.add((SAPPHO_PROP.expr_possibly_cited_by, RDFS.subPropertyOf, ECRM.P130i_features_are_also_found_on))   
        
        # lrmoo alignment
        g.add((LRMOO.R76_is_derivative_of, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cites))
        g.add((LRMOO.R76i_has_derivative, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cited_by))

        # other ontologies
        g.add((BIBO.cites, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cites))
        g.add((BIBO.citedBy, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cited_by))
        
        g.add((CITO.cites, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cites))
        g.add((CITO.isCitedBy, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cited_by))
        
        g.add((ONTOPOETRY_ANALYSIS.usedAsRedaction, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cites)) # young to old
        g.add((ONTOPOETRY_ANALYSIS.usedAsSource, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cites)) # young to old
        g.add((ONTOPOETRY_ANALYSIS.showsInfluencesOf, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cites)) # young to old
        g.add((ONTOPOETRY_ANALYSIS.isDerivativeOf, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cites)) # young to old
        g.add((ONTOPOETRY_ANALYSIS.isUsedRedactionIn, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cited_by)) # old to young
        g.add((ONTOPOETRY_ANALYSIS.isUsedSourceIn, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cited_by)) # old to young
        g.add((ONTOPOETRY_ANALYSIS.influencesAreFoundOn, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cited_by)) # old to young
        g.add((ONTOPOETRY_ANALYSIS.hasDerivative, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cited_by)) # old to young
        
        g.add((SCHEMA.citation, SKOS.broadMatch, SAPPHO_PROP.expr_possibly_cites))
        
        # sappho_prop:tp_possibly_cites / sappho_prop:tp_possibly_cited_by
        # if two expressions have intro:INT21_TextPassages that are part of their intro:INT31, 
        # it is also possible (but not necessary) that the younger text cites the text passage of the older text. 
                            
        g.add((SAPPHO_PROP.tp_possibly_cites, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.tp_possibly_cites, RDFS.label,
            Literal("The younger text possibly cites the text passage of the older text", lang="en")))
        g.add((SAPPHO_PROP.tp_possibly_cites, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.tp_possibly_cites, RDFS.range, INTRO.INT21_TextPassage))
        
        g.add((SAPPHO_PROP.tp_possibly_cited_by, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.tp_possibly_cited_by, RDFS.label,
            Literal("The older text is possibly cited by the younger text passage", lang="en")))
        g.add((SAPPHO_PROP.tp_possibly_cited_by, RDFS.domain, INTRO.INT21_TextPassage))
        g.add((SAPPHO_PROP.tp_possibly_cited_by, RDFS.range, LRMOO.F2_Expression))
        
        g.add((SAPPHO_PROP.tp_possibly_cited_by, OWL.inverseOf, SAPPHO_PROP.tp_possibly_cites))
        
        g.add((LRMOO.R75_incorporates,  SKOS.broadMatch, SAPPHO_PROP.tp_possibly_cites))
        g.add((LRMOO.R75i_is_incorporated_in, SKOS.broadMatch, SAPPHO_PROP.tp_possibly_cites))
        
        g.add((SAPPHO_PROP.tp_possibly_cites, RDFS.subPropertyOf, ECRM.P148_has_component))
        g.add((SAPPHO_PROP.tp_possibly_cited_by, RDFS.subPropertyOf, ECRM.P148i_is_component_of))   
        
        g.add((SAPPHO_PROP.tp_possibly_cites, RDFS.subPropertyOf, ECRM.P130_shows_features_of))
        g.add((SAPPHO_PROP.tp_possibly_cited_by, RDFS.subPropertyOf, ECRM.P130i_features_are_also_found_on)) 
        
        chain21 = [INTRO.R30_hasTextPassage]
        b21     = BNode()
        Collection(g, b21, chain21)
        g.add((SAPPHO_PROP.tp_possibly_cites, OWL.propertyChainAxiom, b21))

        for younger_expr, older_expr, younger_tp, older_tp in directions:
            
            g.add((younger_expr, SAPPHO_PROP.expr_possibly_cites, older_expr))
            g.add((older_expr,   SAPPHO_PROP.expr_possibly_cited_by, younger_expr))
            
            g.add((younger_expr, SAPPHO_PROP.tp_possibly_cites, older_tp))
            g.add((older_tp,   SAPPHO_PROP.tp_possibly_cited_by, younger_expr))

        g.add((CITO.hasCitedEntity,  SKOS.broadMatch, SAPPHO_PROP.tp_possibly_cites))
        g.add((CITO.hasCitingEntity, SKOS.broadMatch, SAPPHO_PROP.tp_possibly_cited_by))
    
    # sappho_prop:expr_references / sappho_prop:referenced_by_expr: expressions that actualize a intro:INT18_Reference will be also linked to the referred entity
    if any(g.triples((None, ECRM.P67_refers_to, None))):
        g.add((SAPPHO_PROP.expr_references, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.expr_references, RDFS.label,
            Literal("Reference from expression to person, place or expression", lang="en")))
        chain_bnode = BNode()
        Collection(g, chain_bnode, [
            INTRO.R18_showsActualization,
            ECRM.P67_refers_to
        ])
        g.add((SAPPHO_PROP.expr_references, OWL.propertyChainAxiom, chain_bnode))
        
        g.add((SAPPHO_PROP.expr_references, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.expr_references, RDFS.range, ECRM.E21_Person))
        g.add((SAPPHO_PROP.expr_references, RDFS.range, ECRM.E53_Place))
        g.add((SAPPHO_PROP.expr_references, RDFS.range, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.expr_references, RDFS.subPropertyOf, ECRM.P67_refers_to))
        
        g.add((SAPPHO_PROP.referenced_by_expr, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.referenced_by_expr, RDFS.label,
            Literal("Person, place or expression referenced by expression", lang="en")))
        g.add((SAPPHO_PROP.referenced_by_expr, OWL.inverseOf, SAPPHO_PROP.expr_references))
        g.add((SAPPHO_PROP.referenced_by_expr, RDFS.domain, ECRM.E21_Person))
        g.add((SAPPHO_PROP.referenced_by_expr, RDFS.domain, ECRM.E53_Place))
        g.add((SAPPHO_PROP.referenced_by_expr, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.referenced_by_expr, RDFS.range,  LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.referenced_by_expr, RDFS.subPropertyOf, ECRM.P67i_is_referred_to_by))
        
        for expr in g.subjects(RDF.type, LRMOO.F2_Expression):
            for act in g.objects(expr, INTRO.R18_showsActualization):
                for target in g.objects(act, ECRM.P67_refers_to):
                    g.add((expr, SAPPHO_PROP.expr_references, target))
                    if (target, RDF.type, ECRM.E21_Person) in g:
                        g.add((expr, SAPPHO_PROP.references_person, target))
                    elif (target, RDF.type, ECRM.E53_Place) in g:
                        g.add((expr, SAPPHO_PROP.references_place, target))
                    elif (target, RDF.type, LRMOO.F2_Expression) in g:
                        pass
        
        g.add((SAPPHO_PROP.expr_references, SKOS.closeMatch, DC.references))
        g.add((DC.isReferencedBy, OWL.inverseOf, DC.references))
        
        g.add((SAPPHO_PROP.expr_references, SKOS.narrowMatch, MIMOTEXT.P50)) # mentions
        g.add((MIMOTEXT.P51, OWL.inverseOf, MIMOTEXT.P50))

        g.add((ONTOPOETRY_CORE.mentions, SKOS.broadMatch, SAPPHO_PROP.expr_references))
        g.add((ONTOPOETRY_CORE.isMentionedIn, OWL.inverseOf, ONTOPOETRY_CORE.mentions))
        
        g.add((SCHEMA.mentions, SKOS.broadMatch, SAPPHO_PROP.expr_references))
        
    # sappho_prop:references_person / sappho_prop:person_referenced_by
    
    if any(g.triples((None, ECRM.P67_refers_to, ECRM.E21_Person))):
        g.add((SAPPHO_PROP.references_person, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.references_person, RDFS.label,
            Literal("Reference to person", lang="en")))
        chain_bnode = BNode()
        Collection(g, chain_bnode, [
            INTRO.R18_showsActualization,
            ECRM.P67_refers_to
        ])
        g.add((SAPPHO_PROP.references_person, OWL.propertyChainAxiom, chain_bnode))
        
        g.add((SAPPHO_PROP.references_person, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.references_person, RDFS.range, ECRM.E21_Person))
        g.add((SAPPHO_PROP.references_person, RDFS.subPropertyOf, ECRM.P67_refers_to))

        g.add((SAPPHO_PROP.person_referenced_by, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.person_referenced_by, RDFS.label,
            Literal("Person referenced by expression", lang="en")))
        g.add((SAPPHO_PROP.person_referenced_by, OWL.inverseOf, SAPPHO_PROP.references_person))
        g.add((SAPPHO_PROP.person_referenced_by, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.person_referenced_by, RDFS.range,  ECRM.E21_Person))
        g.add((SAPPHO_PROP.person_referenced_by, RDFS.subPropertyOf, ECRM.P67i_is_referred_to_by))
            
        g.add((ONTOPOETRY_CORE.mentionsAgent, SKOS.broadMatch, SAPPHO_PROP.references_person))
        g.add((ONTOPOETRY_CORE.isAgentMentionedIn, OWL.inverseOf, ONTOPOETRY_CORE.mentionsAgent))
    
    # sappho_prop:references_place / sappho_prop:place_referenced_by
    
    if any(g.triples((None, ECRM.P67_refers_to, ECRM.E53_Place))):
        g.add((SAPPHO_PROP.references_place, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.references_place, RDFS.label,
            Literal("Reference to place", lang="en")))
        chain_bnode = BNode()
        Collection(g, chain_bnode, [
            INTRO.R18_showsActualization,
            ECRM.P67_refers_to
        ])
        g.add((SAPPHO_PROP.references_place, OWL.propertyChainAxiom, chain_bnode))
        
        g.add((SAPPHO_PROP.references_place, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.references_place, RDFS.range, ECRM.E53_Place))
        g.add((SAPPHO_PROP.references_place, RDFS.subPropertyOf, ECRM.P67_refers_to))
        
        g.add((SAPPHO_PROP.place_referenced_by, RDF.type, OWL.ObjectProperty))
        g.add((SAPPHO_PROP.place_referenced_by, RDFS.label,
            Literal("Place referenced by expression", lang="en")))
        g.add((SAPPHO_PROP.place_referenced_by, OWL.inverseOf, SAPPHO_PROP.references_place))
        g.add((SAPPHO_PROP.place_referenced_by, RDFS.domain, LRMOO.F2_Expression))
        g.add((SAPPHO_PROP.place_referenced_by, RDFS.range,  ECRM.E53_Place))
        g.add((SAPPHO_PROP.place_referenced_by, RDFS.subPropertyOf, ECRM.P67i_is_referred_to_by))
        
        g.add((ONTOPOETRY_CORE.mentionsPlace, SKOS.broadMatch, SAPPHO_PROP.references_place))
        g.add((ONTOPOETRY_CORE.isPlaceMentionedIn, OWL.inverseOf, ONTOPOETRY_CORE.mentionsPlace))

    # sappho_prop:has_character / sappho_prop:is_character_in: link character and expression
    if any(g.triples((None, RDF.type, INTRO.INT_Character))):
        properties = [
            ("has_character",    GOLEM.GP1i_has_character),
            ("is_character_in",  GOLEM.GP1i_is_character_in),
        ]

        for local_name, golem_prop in properties:
            prop = SAPPHO_PROP[local_name]
            g.add((prop, RDF.type, OWL.ObjectProperty))
            g.add((prop, RDFS.label, Literal(local_name, lang="en")))
            g.add((prop, SKOS.closeMatch, golem_prop))

            if local_name == "has_character":
                g.add((prop, RDFS.domain, LRMOO.F2_Expression))
                g.add((prop, RDFS.range,  INTRO.INT2_ActualizationOfFeature))
                g.add((prop, RDFS.subPropertyOf, ECRM.P148_has_component))
            else:
                g.add((prop, RDFS.domain, INTRO.INT2_ActualizationOfFeature))
                g.add((prop, RDFS.range,  LRMOO.F2_Expression))
                g.add((prop, RDFS.subPropertyOf, ECRM.P148i_is_component_of))

        for expr in g.subjects(RDF.type, LRMOO.F2_Expression):
            for act in g.objects(expr, INTRO.R18_showsActualization):
                feat = g.value(act, INTRO.R17_actualizesFeature)
                if feat and (feat, RDF.type, INTRO.INT_Character) in g:
                    g.add((expr, SAPPHO_PROP.has_character,    act))
                    g.add((act,  SAPPHO_PROP.is_character_in, expr))
        
        g.add((ONTOPOETRY_CORE.characterIn, SKOS.closeMatch, SAPPHO_PROP.is_character_in))
        g.add((ONTOPOETRY_CORE.hasCharacter, SKOS.closeMatch, SAPPHO_PROP.has_character))
        g.add((SCHEMA.character, SKOS.closeMatch, SAPPHO_PROP.has_character))
    
    # Serialize
    g.serialize(destination=str(args.output), format="turtle")

    # Remove DBpedia prefixes in-place
    ttl_path = Path(args.output)
    text = ttl_path.read_text(encoding="utf-8")

    text = re.sub(r'^@prefix\s+dbpedia:\s*<[^>]+>\s*\.\s*\n', '', text, flags=re.MULTILINE)

    text = re.sub(r'\bdbpedia:([A-Za-z0-9_/]+)\b', r'<https://dbpedia.org/\1>', text)

    ttl_path.write_text(text, encoding="utf-8")
    print(f"✅ File saved as {args.output}")

if __name__ == "__main__":
    main()
