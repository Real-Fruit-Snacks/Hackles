"""BloodHound CE Neo4j connection and query execution"""
import time
from typing import Optional
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError
from hackles.display.colors import Colors
from hackles.core.cypher import node_type

# Attack edge types for path analysis
ATTACK_EDGES = [
    # Core relationships
    'MemberOf', 'AdminTo', 'HasSession', 'CanRDP', 'CanPSRemote',
    'ExecuteDCOM', 'SQLAdmin',
    # ACL abuse
    'GenericAll', 'GenericWrite', 'WriteDacl', 'WriteOwner',
    'ForceChangePassword', 'AddMember', 'AllExtendedRights',
    'Owns', 'AddSelf', 'WriteSPN', 'WriteAccountRestrictions',
    # DCSync
    'GetChanges', 'GetChangesAll', 'DCSync',
    # Delegation
    'AllowedToAct', 'AllowedToDelegate',
    # Credential access
    'ReadLAPSPassword', 'ReadGMSAPassword', 'AddKeyCredentialLink',
    # ADCS
    'Enroll', 'ManageCA', 'ManageCertificates', 'GoldenCert',
    # SID History and coercion
    'HasSIDHistory', 'CoerceToTGT',
]


class BloodHoundCE:
    """BloodHound CE Neo4j query executor"""

    def __init__(self, uri: str, username: str, password: str, debug: bool = False):
        self.uri = uri
        self.username = username
        self.password = password
        self.debug = debug
        self.driver = None
        self._accumulated_results: list = []  # Accumulated results for structured output

    def connect(self) -> bool:
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Verify connection
            self.driver.verify_connectivity()
            return True
        except AuthError as e:
            print(f"{Colors.FAIL}[!] Authentication failed: {e}{Colors.END}")
        except ServiceUnavailable as e:
            print(f"{Colors.FAIL}[!] Neo4j service unavailable: {e}{Colors.END}")
        except Neo4jError as e:
            print(f"{Colors.FAIL}[!] Neo4j error: {e}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Connection failed: {e}{Colors.END}")

        # Clean up driver on any failure
        if self.driver:
            try:
                self.driver.close()
            except Exception:
                pass
            self.driver = None
        return False

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

    def run_query(self, query: str, params: Optional[dict] = None) -> list:
        """Execute a Cypher query and return results.

        Results are also cached in _last_results for structured output modes.
        """
        if self.debug:
            print(f"{Colors.CYAN}[DEBUG] Query: {query}{Colors.END}")
            if params:
                print(f"{Colors.CYAN}[DEBUG] Params: {params}{Colors.END}")

        start_time = time.time()
        results = []

        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                results = [dict(record) for record in result]
        except Neo4jError as e:
            print(f"{Colors.FAIL}[!] Query error: {e}{Colors.END}")
            raise  # Re-raise for caller to handle
        except Exception as e:
            print(f"{Colors.FAIL}[!] Unexpected error during query: {e}{Colors.END}")
            raise

        elapsed = time.time() - start_time
        if self.debug:
            print(f"{Colors.CYAN}[DEBUG] Query completed in {elapsed:.2f}s{Colors.END}")

        # Accumulate results for structured output modes (JSON/CSV/HTML)
        # This allows queries that run multiple sub-queries to capture all results
        self._accumulated_results.extend(results)
        return results

    @property
    def accumulated_results(self) -> list:
        """Get all accumulated results from queries run since last clear."""
        return self._accumulated_results

    def clear_results_cache(self):
        """Clear the accumulated results cache. Call before each query function."""
        self._accumulated_results = []

    def get_domains(self) -> list:
        """Get all domains in the database"""
        query = """
        MATCH (d:Domain)
        RETURN d.name AS name, d.functionallevel AS level, d.objectid AS objectid
        ORDER BY d.name
        """
        return self.run_query(query)

    def get_domain_sid(self, domain: str) -> Optional[str]:
        """Get the SID for a domain"""
        query = """
        MATCH (d:Domain)
        WHERE toUpper(d.name) = toUpper($domain)
        RETURN d.objectid AS sid
        """
        results = self.run_query(query, {"domain": domain})
        if results:
            return results[0]["sid"]
        return None

    def mark_owned(self, name: str) -> bool:
        """Add Tag_Owned label to a principal"""
        query = """
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        SET n:Tag_Owned
        RETURN n.name AS name
        """
        results = self.run_query(query, {"name": name})
        return len(results) > 0

    def unmark_owned(self, name: str) -> bool:
        """Remove Tag_Owned label from a principal"""
        query = """
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        REMOVE n:Tag_Owned
        RETURN n.name AS name
        """
        results = self.run_query(query, {"name": name})
        return len(results) > 0

    def mark_tier_zero(self, name: str) -> bool:
        """Add Tag_Tier_Zero label to a principal"""
        query = """
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        SET n:Tag_Tier_Zero
        RETURN n.name AS name
        """
        results = self.run_query(query, {"name": name})
        return len(results) > 0

    def unmark_tier_zero(self, name: str) -> bool:
        """Remove Tag_Tier_Zero label from a principal"""
        query = """
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        REMOVE n:Tag_Tier_Zero
        RETURN n.name AS name
        """
        results = self.run_query(query, {"name": name})
        return len(results) > 0

    def clear_all_owned(self) -> int:
        """Remove Tag_Owned label from all principals"""
        query = """
        MATCH (n:Tag_Owned)
        REMOVE n:Tag_Owned
        RETURN count(n) AS removed
        """
        results = self.run_query(query)
        return results[0]["removed"] if results else 0

    def get_node_info(self, name: str) -> Optional[dict]:
        """Get all properties of a node by name"""
        query = """
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        RETURN n, labels(n) AS labels
        LIMIT 1
        """
        results = self.run_query(query, {"name": name})
        if results:
            node_props = dict(results[0]["n"])
            node_props["_labels"] = results[0]["labels"]
            return node_props
        return None

    def search_nodes(self, pattern: str) -> list:
        """Search for nodes matching a pattern (supports * wildcards)"""
        import re
        # Escape special regex characters except *, then replace * with .*
        escaped = re.escape(pattern).replace(r'\*', '.*')
        regex_pattern = escaped
        query = f"""
        MATCH (n)
        WHERE n.name =~ $pattern
        RETURN n.name AS name, {node_type('n')} AS type, n.enabled AS enabled, n.domain AS domain
        ORDER BY n.name
        LIMIT 100
        """
        return self.run_query(query, {"pattern": f"(?i){regex_pattern}"})

    def find_shortest_path(self, source: str, target: str) -> list:
        """Find shortest path between two nodes"""
        query = f"""
        MATCH (source) WHERE toUpper(source.name) = toUpper($source)
        MATCH (target) WHERE toUpper(target.name) = toUpper($target)
        MATCH p = shortestPath((source)-[*1..15]->(target))
        RETURN
            [n IN nodes(p) | n.name] AS nodes,
            [n IN nodes(p) | {node_type('n')}] AS node_types,
            [r IN relationships(p) | type(r)] AS relationships,
            length(p) AS path_length
        LIMIT 5
        """
        return self.run_query(query, {"source": source, "target": target})

    def find_path_to_da(self, principal: str) -> list:
        """Find shortest path from principal to Domain Admins"""
        query = f"""
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        MATCH (g:Group)
        WHERE g.objectid ENDS WITH '-512' OR g.objectid ENDS WITH '-519'
        MATCH p = shortestPath((n)-[*1..15]->(g))
        RETURN
            [node IN nodes(p) | node.name] AS nodes,
            [node IN nodes(p) | {node_type('node')}] AS node_types,
            [r IN relationships(p) | type(r)] AS relationships,
            length(p) AS path_length,
            g.name AS target
        ORDER BY length(p)
        LIMIT 5
        """
        return self.run_query(query, {"name": principal})

    def find_path_to_dc(self, principal: str) -> list:
        """Find shortest path from principal to Domain Controllers"""
        query = f"""
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        MATCH (c:Computer)-[:MemberOf*1..]->(g:Group)
        WHERE g.objectid ENDS WITH '-516'
        MATCH p = shortestPath((n)-[*1..15]->(c))
        RETURN
            [node IN nodes(p) | node.name] AS nodes,
            [node IN nodes(p) | {node_type('node')}] AS node_types,
            [r IN relationships(p) | type(r)] AS relationships,
            length(p) AS path_length,
            c.name AS target
        ORDER BY length(p)
        LIMIT 5
        """
        return self.run_query(query, {"name": principal})

    def get_group_members(self, group_name: str) -> list:
        """Get members of a group (recursive)"""
        query = f"""
        MATCH (g:Group) WHERE toUpper(g.name) = toUpper($name)
        MATCH (m)-[:MemberOf*1..]->(g)
        RETURN DISTINCT m.name AS member, {node_type('m')} AS type, m.enabled AS enabled
        ORDER BY {node_type('m')}, m.name
        LIMIT 500
        """
        return self.run_query(query, {"name": group_name})

    def get_member_of(self, principal: str) -> list:
        """Get groups a principal belongs to"""
        query = f"""
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        MATCH (n)-[:MemberOf*1..]->(g:Group)
        RETURN DISTINCT g.name AS group_name,
               CASE WHEN 'admin_tier_0' IN g.system_tags OR g:Tag_Tier_Zero THEN 'Yes' ELSE 'No' END AS tier_zero,
               g.description AS description
        ORDER BY tier_zero DESC, g.name
        """
        return self.run_query(query, {"name": principal})

    def get_admins_to(self, computer: str) -> list:
        """Get principals with admin rights to a computer"""
        query = f"""
        MATCH (c:Computer) WHERE toUpper(c.name) = toUpper($name)
        MATCH (n)-[:AdminTo|MemberOf*1..3]->(c)
        RETURN DISTINCT n.name AS principal, {node_type('n')} AS type, n.enabled AS enabled
        ORDER BY {node_type('n')}, n.name
        LIMIT 100
        """
        return self.run_query(query, {"name": computer})

    def get_admin_of(self, principal: str) -> list:
        """Get computers a principal can admin"""
        query = f"""
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        MATCH (n)-[:AdminTo|MemberOf*1..3]->(c:Computer)
        RETURN DISTINCT c.name AS computer, c.operatingsystem AS os, c.enabled AS enabled
        ORDER BY c.name
        LIMIT 100
        """
        return self.run_query(query, {"name": principal})

    def get_computer_sessions(self, computer: str) -> list:
        """Get sessions on a computer"""
        query = """
        MATCH (c:Computer) WHERE toUpper(c.name) = toUpper($name)
        MATCH (c)-[:HasSession]->(u:User)
        RETURN u.name AS user, u.admincount AS admin, u.enabled AS enabled
        ORDER BY u.admincount DESC, u.name
        """
        return self.run_query(query, {"name": computer})

    def get_edges_from(self, principal: str) -> list:
        """Get outbound edges from a node"""
        query = f"""
        MATCH (n) WHERE toUpper(n.name) = toUpper($name)
        MATCH (n)-[r]->(m)
        WHERE type(r) IN $edge_types
        RETURN type(r) AS relationship, m.name AS target, {node_type('m')} AS target_type
        ORDER BY type(r), m.name
        LIMIT 100
        """
        return self.run_query(query, {"name": principal, "edge_types": ATTACK_EDGES})

    def get_edges_to(self, principal: str) -> list:
        """Get inbound edges to a node"""
        query = f"""
        MATCH (m) WHERE toUpper(m.name) = toUpper($name)
        MATCH (n)-[r]->(m)
        WHERE type(r) IN $edge_types
        RETURN n.name AS source, {node_type('n')} AS source_type, type(r) AS relationship
        ORDER BY type(r), n.name
        LIMIT 100
        """
        return self.run_query(query, {"name": principal, "edge_types": ATTACK_EDGES})
