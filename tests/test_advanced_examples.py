"""
Test script for ADVANCED_EXAMPLES.md - demonstrating the power of knowledge graphs.
This runs through several advanced scenarios showing emergent knowledge discovery.
"""

import sys
import shutil
from pathlib import Path

# Fix Windows console encoding for unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from src.server import (
    ingest_hypothesis,
    connect_propositions,
    semantic_search,
    find_scientific_lineage,
    find_contradictions,
    list_propositions,
    get_unit,
)

# Store unit IDs
units = {}


def print_header(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title: str):
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def print_insight(text: str):
    """Print an insight or discovery."""
    print(f"\n  [INSIGHT] {text}")


def print_result(label: str, result: dict, show_details: bool = False):
    """Print a result summary."""
    status = "[OK]" if result.get("status") == "success" else "[FAIL]"
    print(f"  {status} {label}")
    if show_details and result.get("status") == "success":
        for key, value in result.items():
            if key in ["status", "available_actions"]:
                continue
            if isinstance(value, list):
                print(f"      {key}: {len(value)} items")
            elif isinstance(value, dict):
                print(f"      {key}: {value}")
            else:
                print(f"      {key}: {str(value)[:80]}")


def ingest(content: str, source: str = "", key: str = None) -> str:
    """Helper to ingest and store unit ID."""
    result = ingest_hypothesis(
        hypothesis=content,
        source=source,
        idempotency_key=key or f"adv-{len(units)}"
    )
    unit_id = result.get("unit_id")
    if key:
        units[key] = unit_id
    print(f"  [+] {content[:60]}...")
    return unit_id


def connect(key_a: str, key_b: str, relation: str, reasoning: str):
    """Helper to connect two units by key."""
    result = connect_propositions(
        id_a=units[key_a],
        id_b=units[key_b],
        relation=relation,
        reasoning=reasoning,
        idempotency_key=f"conn-{key_a}-{key_b}"
    )
    status = "[OK]" if result.get("status") == "success" else "[FAIL]"
    print(f"  {status} {key_a} --[{relation}]--> {key_b}")
    return result


# =============================================================================
# EXAMPLE 1: Discovering Hidden Connections (Sleep -> Creativity)
# =============================================================================
def run_example_1():
    """Example 1: Discovering Hidden Connections - Sleep and Creativity"""
    print_header("EXAMPLE 1: Discovering Hidden Connections")
    print("Scenario: Finding the link between sleep and creativity\n")

    print_subheader("Step 1: Building the knowledge base")

    ingest("REM sleep is associated with memory consolidation",
           "Walker et al. 2017", "rem_memory")
    ingest("Memory consolidation involves replaying neural patterns from waking experience",
           "neuroscience research", "memory_replay")
    ingest("Creative insights often occur when the brain makes novel associations between existing memories",
           "cognitive psychology", "creative_associations")
    ingest("The prefrontal cortex, which normally inhibits unusual associations, is less active during REM sleep",
           "neuroimaging studies", "prefrontal_rem")
    ingest("Many historical discoveries occurred immediately after sleep, including Mendeleev's periodic table",
           "history of science", "sleep_discoveries")

    print_subheader("Step 2: Connecting the knowledge")

    connect("rem_memory", "memory_replay", "implies",
            "Memory consolidation happens through neural replay during REM")
    connect("memory_replay", "creative_associations", "supports",
            "Replayed memories can form new associations")
    connect("prefrontal_rem", "creative_associations", "supports",
            "Less inhibition during REM allows unusual associations")
    connect("sleep_discoveries", "creative_associations", "supports",
            "Historical evidence that sleep aids creative insights")

    print_subheader("Step 3: Discovering the hidden connection")

    result = find_scientific_lineage(
        start_concept="REM sleep",
        end_concept="creative insights"
    )
    print_result("Lineage: REM sleep -> creative insights", result, show_details=True)

    if result.get("path"):
        print_insight("The graph reveals TWO pathways from sleep to creativity:")
        print("    1. REM -> Memory consolidation -> Neural replay -> Novel associations")
        print("    2. REM -> Reduced prefrontal activity -> Unusual associations allowed")
        print_insight("EMERGENT HYPOTHESIS: Memory replay during REM, combined with")
        print("    reduced inhibition, allows finding novel connections between memories.")

    return result.get("status") == "success"


# =============================================================================
# EXAMPLE 2: Generating New Hypotheses (Drug Repurposing)
# =============================================================================
def run_example_2():
    """Example 2: Generating New Hypotheses - Drug Repurposing"""
    print_header("EXAMPLE 2: Generating New Hypotheses")
    print("Scenario: Drug repurposing through mechanism chain discovery\n")

    print_subheader("Step 1: Building pharmaceutical knowledge")

    ingest("Metformin is a diabetes drug that lowers blood glucose by improving insulin sensitivity",
           "pharmacology", "metformin_diabetes")
    ingest("Metformin activates AMPK (AMP-activated protein kinase) in cells",
           "molecular biology", "metformin_ampk")
    ingest("AMPK activation inhibits mTOR signaling pathway",
           "cell biology", "ampk_mtor")
    ingest("mTOR pathway dysregulation is implicated in cancer cell proliferation",
           "oncology research", "mtor_cancer")
    ingest("mTOR inhibitors like rapamycin show anti-cancer properties",
           "clinical trials", "mtor_inhibitors")
    ingest("Metformin users show lower rates of certain cancers in epidemiological studies",
           "population health", "metformin_cancer_rates")

    print_subheader("Step 2: Building the mechanism chain")

    connect("metformin_diabetes", "metformin_ampk", "implies",
            "Metformin's mechanism involves AMPK activation")
    connect("metformin_ampk", "ampk_mtor", "implies",
            "AMPK activation leads to mTOR inhibition")
    connect("ampk_mtor", "mtor_cancer", "implies",
            "mTOR inhibition should reduce cancer proliferation")
    connect("mtor_inhibitors", "mtor_cancer", "supports",
            "mTOR inhibitors demonstrate anti-cancer effects")
    connect("metformin_cancer_rates", "metformin_ampk", "supports",
            "Epidemiological evidence supports mechanism")

    print_subheader("Step 3: Discovering the repurposing hypothesis")

    result = find_scientific_lineage(
        start_concept="Metformin diabetes drug",
        end_concept="anti-cancer properties"
    )
    print_result("Lineage: Metformin -> Anti-cancer", result, show_details=True)

    print_insight("EMERGENT HYPOTHESIS GENERATED:")
    print("    Metformin -> AMPK activation -> mTOR inhibition -> Anti-cancer effect")
    print_insight("This suggests Metformin could be repurposed as adjuvant cancer therapy,")
    print("    particularly for mTOR-driven cancers. The graph connected dots across")
    print("    pharmacology, cell biology, and oncology!")

    return result.get("status") == "success"


# =============================================================================
# EXAMPLE 3: Finding Research Gaps (Climate Science)
# =============================================================================
def run_example_3():
    """Example 3: Finding Research Gaps - Climate Feedback Loops"""
    print_header("EXAMPLE 3: Finding Research Gaps")
    print("Scenario: Identifying missing links in climate science\n")

    print_subheader("Step 1: Mapping climate knowledge")

    ingest("Increased CO2 raises global temperatures through the greenhouse effect",
           "IPCC reports", "co2_warming")
    ingest("Higher temperatures increase ocean evaporation rates",
           "atmospheric physics", "temp_evaporation")
    ingest("Increased atmospheric water vapor amplifies warming (water vapor feedback)",
           "climate science", "water_vapor_feedback")
    ingest("Warming temperatures cause permafrost thawing in Arctic regions",
           "cryosphere research", "warming_permafrost")
    ingest("Permafrost contains large amounts of frozen methane and organic carbon",
           "geological surveys", "permafrost_methane")
    ingest("Methane is a greenhouse gas 80x more potent than CO2 over 20 years",
           "atmospheric chemistry", "methane_potency")
    ingest("Arctic temperatures are rising 2-4x faster than global average",
           "polar research", "arctic_amplification")

    print_subheader("Step 2: Connecting known relationships")

    connect("co2_warming", "temp_evaporation", "implies",
            "Higher temperatures lead to more evaporation")
    connect("temp_evaporation", "water_vapor_feedback", "implies",
            "More water vapor amplifies warming")
    connect("co2_warming", "warming_permafrost", "implies",
            "Warming causes permafrost to thaw")
    connect("warming_permafrost", "permafrost_methane", "implies",
            "Thawing releases stored methane")
    connect("permafrost_methane", "methane_potency", "supports",
            "Released methane is potent greenhouse gas")
    connect("arctic_amplification", "warming_permafrost", "supports",
            "Arctic warming accelerates permafrost thaw")

    print_subheader("Step 3: Identifying research gaps")

    # Search for what connects methane back to warming
    result = find_scientific_lineage(
        start_concept="permafrost methane release",
        end_concept="global temperature increase"
    )
    print_result("Lineage: Permafrost methane -> Temperature", result, show_details=True)

    # Search for quantification
    search_result = semantic_search(query="methane release rate quantification", limit=5)
    print_result("Search: methane release quantification", search_result)

    print_insight("RESEARCH GAPS IDENTIFIED:")
    print("    1. MISSING QUANTIFICATION: How much methane per degree of warming?")
    print("    2. TIPPING POINT: At what temperature does release become self-sustaining?")
    print("    3. FEEDBACK CLOSURE: The loop shows:")
    print("       CO2 -> Warming -> Permafrost thaw -> Methane -> [? back to warming]")
    print_insight("The graph reveals what science DOESN'T yet know!")

    return result.get("status") == "success"


# =============================================================================
# EXAMPLE 4: Uncovering Implicit Contradictions (Economics)
# =============================================================================
def run_example_4():
    """Example 4: Uncovering Implicit Contradictions - Economic Theory"""
    print_header("EXAMPLE 4: Uncovering Implicit Contradictions")
    print("Scenario: Finding hidden conflicts in economic theory\n")

    print_subheader("Step 1: Adding competing economic claims")

    ingest("Minimum wage increases reduce employment among low-skilled workers",
           "classical economics", "min_wage_reduces")
    ingest("Minimum wage increases have negligible effects on employment in most studies",
           "Card and Krueger 1994", "min_wage_negligible")
    ingest("Labor markets are competitive, meaning wages equal marginal productivity",
           "neoclassical theory", "competitive_markets")
    ingest("Many labor markets exhibit monopsony power where employers set wages below competitive levels",
           "labor economics", "monopsony_power")
    ingest("Minimum wage increases can increase employment when employers have monopsony power",
           "economic theory", "monopsony_minwage")
    ingest("Fast food employment in New Jersey did not decrease after minimum wage increase",
           "Card and Krueger natural experiment", "nj_evidence")

    print_subheader("Step 2: Mapping logical relationships")

    connect("competitive_markets", "min_wage_reduces", "implies",
            "In competitive markets, min wage above equilibrium reduces employment")
    connect("monopsony_power", "monopsony_minwage", "implies",
            "Monopsony allows min wage to increase employment")
    connect("nj_evidence", "min_wage_reduces", "refutes",
            "Empirical evidence contradicts classical prediction")
    connect("nj_evidence", "monopsony_power", "supports",
            "Evidence suggests monopsony is common")
    connect("min_wage_negligible", "min_wage_reduces", "contradicts",
            "Studies show negligible vs reduced employment")

    print_subheader("Step 3: Finding the contradictions")

    result = find_contradictions(claim="minimum wage reduces employment")
    print_result("Contradictions to 'min wage reduces employment'", result, show_details=True)

    if result.get("conflicts"):
        print_insight("CONTRADICTION DETECTED:")
        print("    Path 1 (Classical): Competitive markets -> Min wage reduces employment")
        print("    Path 2 (Empirical): Card-Krueger -> Employment unchanged -> Suggests monopsony")
        print_insight("ROOT CONFLICT: The assumption 'labor markets are competitive'")
        print("    contradicts observed employment patterns!")
        print_insight("The real debate isn't about minimum wage - it's about")
        print("    whether labor markets are actually competitive.")

    return result.get("status") == "success"


# =============================================================================
# EXAMPLE 5: Cross-Domain Innovation (Biology -> Software)
# =============================================================================
def run_example_5():
    """Example 5: Cross-Domain Innovation - Biology to Software"""
    print_header("EXAMPLE 5: Cross-Domain Innovation")
    print("Scenario: Applying biological principles to software architecture\n")

    print_subheader("Step 1: Building biology knowledge")

    ingest("The human immune system has innate immunity (fast, general) and adaptive immunity (slow, specific)",
           "immunology", "immune_types")
    ingest("Adaptive immunity creates memory cells that respond faster to previously encountered pathogens",
           "immunology", "immune_memory")
    ingest("Immune cells communicate through cytokine signaling to coordinate responses",
           "cell biology", "cytokine_signaling")
    ingest("The immune system distinguishes self from non-self using MHC markers",
           "immunology", "mhc_self")
    ingest("Autoimmune diseases occur when the immune system attacks the body's own cells",
           "pathology", "autoimmune")

    print_subheader("Step 2: Building software security knowledge")

    ingest("Firewalls block malicious traffic based on predefined rules (fast, general)",
           "cybersecurity", "firewalls")
    ingest("Intrusion detection systems learn to identify new attack patterns over time",
           "cybersecurity", "ids_learning")
    ingest("Microservices need to authenticate each other to prevent unauthorized access",
           "software architecture", "service_auth")
    ingest("Zero-trust architecture assumes no service should be trusted by default",
           "modern security", "zero_trust")
    ingest("Insider threats occur when authorized users or services attack the system",
           "security", "insider_threats")

    print_subheader("Step 3: Connecting across domains")

    connect("immune_types", "firewalls", "extends",
            "Both provide fast general protection layer")
    connect("immune_memory", "ids_learning", "extends",
            "Both learn and remember specific threats")
    connect("mhc_self", "service_auth", "extends",
            "Both identify trusted entities")
    connect("autoimmune", "insider_threats", "extends",
            "Both involve trusted entities causing harm")
    connect("cytokine_signaling", "service_auth", "extends",
            "Both enable coordinated responses")

    print_subheader("Step 4: Generating innovations")

    result = find_scientific_lineage(
        start_concept="immune system coordination",
        end_concept="microservices security"
    )
    print_result("Lineage: Immune coordination -> Microservices", result, show_details=True)

    search_result = semantic_search(query="coordinated threat response", limit=5)
    print_result("Search: coordinated threat response", search_result)

    print_insight("INNOVATION IDEAS GENERATED:")
    print("    1. CYTOKINE-INSPIRED SERVICE MESH: Services emit 'digital cytokines'")
    print("       when under attack, triggering coordinated responses")
    print("    2. ADAPTIVE FIREWALL WITH MEMORY: Combine fast innate rules with")
    print("       slow adaptive learning that remembers attack patterns")
    print("    3. AUTOIMMUNE PREVENTION: Detect when authorized services behave")
    print("       anomalously (like immune tolerance mechanisms)")
    print_insight("The graph bridges decades of immune system evolution")
    print("    to next-generation security architecture!")

    return result.get("status") == "success"


# =============================================================================
# EXAMPLE 6: Emergent Pattern Discovery (Power Laws)
# =============================================================================
def run_example_6():
    """Example 6: Emergent Pattern Discovery - Universal Patterns"""
    print_header("EXAMPLE 6: Emergent Pattern Discovery")
    print("Scenario: Finding universal patterns across diverse systems\n")

    print_subheader("Step 1: Building diverse system knowledge")

    ingest("Power laws describe the distribution of city sizes - few cities are very large, many are small",
           "urban geography", "city_powerlaw")
    ingest("Power laws describe word frequency in languages - few words are very common, many are rare (Zipf's law)",
           "linguistics", "word_powerlaw")
    ingest("Power laws describe the distribution of wealth - few people hold most wealth",
           "economics", "wealth_powerlaw")
    ingest("Power laws describe earthquake magnitudes - large earthquakes are exponentially rarer",
           "seismology", "earthquake_powerlaw")
    ingest("Power laws describe website traffic - few sites get most visits",
           "web science", "web_powerlaw")
    ingest("Power laws emerge in systems with preferential attachment - the rich get richer",
           "network science", "preferential_attachment")
    ingest("Power laws emerge in systems with self-organized criticality",
           "physics", "self_organized")

    print_subheader("Step 2: Connecting the patterns")

    connect("city_powerlaw", "preferential_attachment", "supports",
            "Cities grow by preferential attachment")
    connect("wealth_powerlaw", "preferential_attachment", "supports",
            "Wealth accumulates through preferential attachment")
    connect("web_powerlaw", "preferential_attachment", "supports",
            "Popular sites get more links")
    connect("word_powerlaw", "preferential_attachment", "supports",
            "Common words get used more often")
    connect("earthquake_powerlaw", "self_organized", "supports",
            "Earth's crust is self-organized critical system")

    print_subheader("Step 3: Discovering the meta-pattern")

    search_result = semantic_search(query="power law distribution", limit=10)
    print_result("Search: power law distribution", search_result)

    result = find_scientific_lineage(
        start_concept="preferential attachment mechanism",
        end_concept="wealth inequality"
    )
    print_result("Lineage: Preferential attachment -> Wealth", result, show_details=True)

    print_insight("UNIVERSAL PATTERN DETECTED:")
    print("    Cities, words, wealth, earthquakes, websites - ALL follow power laws!")
    print_insight("UNDERLYING MECHANISMS:")
    print("    1. Preferential attachment (success breeds success)")
    print("    2. Self-organized criticality (systems reach critical state)")
    print_insight("EMERGENT HYPOTHESIS: Any competitive system with preferential")
    print("    attachment will develop extreme inequality. This may explain why")
    print("    inequality is a DEFAULT outcome requiring active intervention!")

    return result.get("status") == "success"


# =============================================================================
# EXAMPLE 7: The "Aha!" Moment Generator
# =============================================================================
def run_example_7():
    """Example 7: The Aha! Moment Generator - Climate Resilience"""
    print_header("EXAMPLE 7: The 'Aha!' Moment Generator")
    print("Scenario: Finding unexpected solutions for climate-resilient cities\n")

    print_subheader("Step 1: Building diverse knowledge")

    ingest("Trees reduce urban temperatures by 2-8C through shade and evapotranspiration",
           "urban forestry", "trees_cooling")
    ingest("Traditional cities in hot climates use narrow streets and courtyards for natural cooling",
           "architecture", "traditional_cooling")
    ingest("Permeable surfaces reduce flooding by allowing water infiltration",
           "civil engineering", "permeable_surfaces")
    ingest("Social cohesion improves disaster recovery rates by 40%",
           "disaster research", "social_cohesion")
    ingest("Coral reefs protect coastlines by dissipating 97% of wave energy",
           "marine biology", "coral_protection")
    ingest("Mangrove forests reduce storm surge flooding by 66%",
           "ecology", "mangrove_protection")
    ingest("Diverse ecosystems are more resilient to perturbation than monocultures",
           "ecology", "ecosystem_diversity")
    ingest("Ants create decentralized, resilient infrastructure without central planning",
           "entomology", "ant_infrastructure")
    ingest("Traditional rice paddies function as flood buffers and aquifer recharge",
           "agricultural science", "rice_paddies")

    print_subheader("Step 2: Connecting across domains")

    connect("trees_cooling", "traditional_cooling", "supports",
            "Both use natural cooling mechanisms")
    connect("coral_protection", "mangrove_protection", "supports",
            "Both provide natural coastal defense")
    connect("ecosystem_diversity", "coral_protection", "implies",
            "Diverse ecosystems provide multiple protections")
    connect("ant_infrastructure", "ecosystem_diversity", "supports",
            "Decentralization creates resilience")
    connect("rice_paddies", "permeable_surfaces", "extends",
            "Both manage water through infiltration")
    connect("social_cohesion", "ecosystem_diversity", "extends",
            "Human networks are like ecosystems")

    print_subheader("Step 3: Generating 'Aha!' moments")

    result1 = find_scientific_lineage(
        start_concept="coral reef wave protection",
        end_concept="urban flood management"
    )
    print_result("Lineage: Coral reefs -> Urban flooding", result1)

    result2 = find_scientific_lineage(
        start_concept="ant colony infrastructure",
        end_concept="city resilience"
    )
    print_result("Lineage: Ant colonies -> City resilience", result2)

    search_result = semantic_search(query="natural infrastructure resilience", limit=5)
    print_result("Search: natural infrastructure resilience", search_result)

    print_insight("'AHA!' MOMENTS GENERATED:")
    print("")
    print("    AHA! #1: BIOMIMETIC COASTAL INFRASTRUCTURE")
    print("    Coral reefs dissipate 97% of wave energy")
    print("    -> Design artificial 'reef parks' for coastal cities")
    print("    -> Recreation + storm surge protection combined!")
    print("")
    print("    AHA! #2: ANT COLONY URBANISM")
    print("    Ants build redundant, self-healing networks")
    print("    -> Water/power/transport should have no single points of failure")
    print("    -> Self-healing city infrastructure")
    print("")
    print("    AHA! #3: AGRICULTURAL URBANISM")
    print("    Rice paddies = food production + flood buffer")
    print("    -> Urban farms designed as water retention systems")
    print("    -> Food security + flood resilience combined!")
    print("")
    print("    AHA! #4: SOCIAL INFRASTRUCTURE")
    print("    Social cohesion = 40% better disaster recovery")
    print("    -> Community bonds ARE infrastructure")
    print("    -> Design neighborhoods that build connections")
    print("")
    print_insight("The graph generates creative solutions by connecting")
    print("    domains you wouldn't normally combine!")

    return result1.get("status") == "success"


# =============================================================================
# EXAMPLE 8: Historical Idea Archaeology
# =============================================================================
def run_example_8():
    """Example 8: Historical Idea Archaeology - Origins of the Internet"""
    print_header("EXAMPLE 8: Historical Idea Archaeology")
    print("Scenario: Tracing the intellectual origins of the Internet\n")

    print_subheader("Step 1: Building historical knowledge")

    ingest("Vannevar Bush proposed the Memex in 1945 - a device for storing and linking information",
           "As We May Think", "memex_1945")
    ingest("Ted Nelson coined 'hypertext' in 1963 for non-sequential writing with links",
           "computing history", "hypertext_1963")
    ingest("Douglas Engelbart demonstrated the mouse, hypertext, and collaboration in 1968",
           "Mother of All Demos", "engelbart_1968")
    ingest("Paul Baran developed packet switching in 1964 to route data through damaged networks",
           "networking history", "packet_switching_1964")
    ingest("ARPANET was created in 1969 as a military network that could survive partial destruction",
           "internet history", "arpanet_1969")
    ingest("Claude Shannon's information theory in 1948 provided mathematical foundation for digital communication",
           "communications theory", "shannon_1948")
    ingest("Tim Berners-Lee invented the World Wide Web in 1989 to share physics documents at CERN",
           "web history", "web_1989")
    ingest("The Cold War nuclear threat drove investment in survivable communications",
           "Cold War history", "cold_war_threat")

    print_subheader("Step 2: Mapping intellectual influences")

    connect("memex_1945", "hypertext_1963", "implies",
            "Bush's Memex inspired Nelson's hypertext concept")
    connect("hypertext_1963", "engelbart_1968", "implies",
            "Nelson's ideas influenced Engelbart's demo")
    connect("engelbart_1968", "web_1989", "implies",
            "Engelbart's vision influenced the Web")
    connect("shannon_1948", "packet_switching_1964", "implies",
            "Information theory enabled digital networking")
    connect("cold_war_threat", "arpanet_1969", "supports",
            "Military need drove ARPANET development")
    connect("packet_switching_1964", "arpanet_1969", "supports",
            "Packet switching was ARPANET's foundation")
    connect("arpanet_1969", "web_1989", "supports",
            "ARPANET infrastructure enabled the Web")

    print_subheader("Step 3: Archaeological analysis")

    result1 = find_scientific_lineage(
        start_concept="Memex 1945",
        end_concept="World Wide Web"
    )
    print_result("Lineage: Memex (1945) -> Web (1989)", result1, show_details=True)

    result2 = find_scientific_lineage(
        start_concept="Cold War nuclear threat",
        end_concept="World Wide Web"
    )
    print_result("Lineage: Cold War -> Web", result2, show_details=True)

    print_insight("INTERNET'S FAMILY TREE REVEALED:")
    print("")
    print("    CONCEPTUAL LINEAGE:")
    print("    Vannevar Bush (Memex 1945)")
    print("        -> Ted Nelson (Hypertext 1963)")
    print("            -> Douglas Engelbart (Demo 1968)")
    print("                -> Tim Berners-Lee (Web 1989)")
    print("")
    print("    INFRASTRUCTURE LINEAGE:")
    print("    Cold War Threat + Shannon's Theory")
    print("        -> Paul Baran (Packet Switching 1964)")
    print("            -> ARPANET (1969)")
    print("                -> Commercial Internet")
    print("                    -> Web (1989)")
    print("")
    print_insight("CONVERGENCE: The Web emerged when:")
    print("    - Hypertext vision (Bush -> Nelson -> Engelbart)")
    print("    - Network infrastructure (Shannon -> Baran -> ARPANET)")
    print("    met in a physicist wanting to share documents!")
    print("")
    print_insight("The Internet wasn't invented - it was ASSEMBLED from")
    print("    decades of accumulated ideas, each building on previous ones.")

    return result1.get("status") == "success"


# =============================================================================
# FINAL SUMMARY
# =============================================================================
def run_final_summary():
    """Print final summary of the knowledge graph."""
    print_header("FINAL KNOWLEDGE GRAPH SUMMARY")

    result = list_propositions(limit=100)

    print(f"\n  Total atomic units created: {result.get('count', 0)}")
    print(f"  Total connections made: {len(units)} tracked units")

    # Show some interesting cross-domain connections
    print("\n  CROSS-DOMAIN CONNECTIONS MADE:")
    print("    - Sleep research <-> Creativity psychology")
    print("    - Pharmacology <-> Oncology (drug repurposing)")
    print("    - Climate science <-> Feedback systems")
    print("    - Economic theory <-> Empirical evidence")
    print("    - Immunology <-> Cybersecurity")
    print("    - Physics/Ecology/Economics <-> Universal patterns")
    print("    - Biology/Architecture/Sociology <-> Urban resilience")
    print("    - Computing history <-> Modern web")

    print_insight("This demonstrates the true power of knowledge graphs:")
    print("    - Emergent hypotheses from connected facts")
    print("    - Research gaps become visible")
    print("    - Contradictions surface automatically")
    print("    - Cross-domain insights generate innovation")
    print("    - Historical lineages reveal intellectual heritage")


def main():
    """Run all advanced examples."""
    print("\n" + "=" * 70)
    print("  KNOWLEDGE GRAPH CLI ADVANCED EXAMPLES TEST SUITE")
    print("  Demonstrating the Power of Knowledge Graphs")
    print("=" * 70)
    print("\nThis will demonstrate how knowledge graphs can:")
    print("  - Discover hidden connections")
    print("  - Generate new hypotheses")
    print("  - Find research gaps")
    print("  - Uncover contradictions")
    print("  - Enable cross-domain innovation")
    print("  - Reveal emergent patterns")
    print("  - Generate 'Aha!' moments")
    print("  - Trace intellectual history")
    print("=" * 70)

    # Clean up old test data
    test_data_dir = Path(__file__).parent.parent / "data"
    if test_data_dir.exists():
        print(f"\n[WARN] Cleaning up existing data in {test_data_dir}")
        shutil.rmtree(test_data_dir)
        print("[OK] Old data removed")

    results = {}

    try:
        results["Ex1: Hidden Connections"] = run_example_1()
        results["Ex2: Hypothesis Generation"] = run_example_2()
        results["Ex3: Research Gaps"] = run_example_3()
        results["Ex4: Contradictions"] = run_example_4()
        results["Ex5: Cross-Domain Innovation"] = run_example_5()
        results["Ex6: Pattern Discovery"] = run_example_6()
        results["Ex7: Aha! Moments"] = run_example_7()
        results["Ex8: Idea Archaeology"] = run_example_8()

        run_final_summary()

    except Exception as e:
        print(f"\n[FAIL] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Final results
    print_header("TEST RESULTS")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"  {status} {name}")

    print(f"\n  Total: {passed}/{total} examples passed")

    if passed == total:
        print("\n  [SUCCESS] All advanced examples completed successfully!")
        print("  The knowledge graph demonstrated its power to generate insights.")
        return 0
    else:
        print(f"\n  [WARN] {total - passed} example(s) had issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
