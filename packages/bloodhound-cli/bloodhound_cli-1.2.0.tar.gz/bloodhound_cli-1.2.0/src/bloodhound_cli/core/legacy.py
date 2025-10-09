"""
Legacy BloodHound implementation using Neo4j
"""
from typing import List, Dict, Optional
from neo4j import GraphDatabase
from .base import BloodHoundClient


class BloodHoundLegacyClient(BloodHoundClient):
    """Legacy BloodHound client using Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str, debug: bool = False, verbose: bool = False):
        super().__init__(debug, verbose)
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def execute_query(self, query: str, **params) -> List[Dict]:
        """Execute a Cypher query"""
        # Show query in debug mode
        if self.debug:
            try:
                from rich.console import Console
                from rich.syntax import Syntax
                console = Console()
                console.print("\n[bold cyan]Debug: Cypher Query[/bold cyan]")
                syntax = Syntax(query, "cypher", theme="monokai", line_numbers=False)
                console.print(syntax)
                if params:
                    console.print(f"[bold cyan]Debug: Query Parameters[/bold cyan]: {params}\n")
            except ImportError:
                # Fallback if rich is not available
                print("\n" + "="*80)
                print("Debug: Cypher Query")
                print("="*80)
                print(query)
                if params:
                    print(f"Debug: Query Parameters: {params}")
                print("="*80 + "\n")
        
        with self.driver.session() as session:
            result = session.run(query, **params).data()
            
            if self.debug:
                print(f"Debug: Query returned {len(result)} records")
            
            return result
    
    def get_users(self, domain: str) -> List[str]:
        query = """
        MATCH (u:User)
        WHERE u.enabled = true AND toLower(u.domain) = toLower($domain)
        RETURN u.samaccountname AS samaccountname
        """
        results = self.execute_query(query, domain=domain)
        return [record["samaccountname"] for record in results]
    
    def get_computers(self, domain: str, laps: Optional[bool] = None) -> List[str]:
        if laps is None:
            query = """
            MATCH (c:Computer)
            WHERE toLower(c.domain) = toLower($domain) AND c.enabled = true
            RETURN toLower(c.name) AS name
            """
            params = {"domain": domain}
        else:
            query = """
            MATCH (c:Computer)
            WHERE toLower(c.domain) = toLower($domain)
              AND c.haslaps = $laps AND c.enabled = true
            RETURN toLower(c.name) AS name
            """
            params = {"domain": domain, "laps": laps}
        results = self.execute_query(query, **params)
        return [record["name"] for record in results]
    
    def get_admin_users(self, domain: str) -> List[str]:
        """Get admin users - includes both direct admincount and through group membership"""
        query = """
        MATCH p=(u:User)-[:MemberOf*1..]->(g:Group)
        WHERE g.admincount = true
          AND u.admincount = false
          AND u.enabled = true
          AND toLower(u.domain) = toLower($domain)
        RETURN u.samaccountname AS samaccountname
        UNION
        MATCH (u:User {admincount:true})
        WHERE u.enabled = true
          AND toLower(u.domain) = toLower($domain)
        RETURN u.samaccountname AS samaccountname
        """
        results = self.execute_query(query, domain=domain)
        return [record["samaccountname"] for record in results]
    
    def get_highvalue_users(self, domain: str) -> List[str]:
        """Get high-value users - includes both direct highvalue and through group membership"""
        query = """
        MATCH (u:User {highvalue: true})
        WHERE u.enabled = true AND toLower(u.domain) = toLower($domain)
        RETURN u.samaccountname AS samaccountname
        UNION
        MATCH p=(u:User)-[:MemberOf*1..]->(g:Group {highvalue: true})-[r1]->(m)
        WHERE u.enabled = true AND toLower(u.domain) = toLower($domain)
        RETURN u.samaccountname AS samaccountname
        """
        results = self.execute_query(query, domain=domain)
        return [record["samaccountname"] for record in results]
    
    def get_password_not_required_users(self, domain: str) -> List[str]:
        query = """
        MATCH (u:User)
        WHERE u.enabled = true AND toLower(u.domain) = toLower($domain)
          AND u.passwordnotreqd = true
        RETURN u.samaccountname AS samaccountname
        """
        results = self.execute_query(query, domain=domain)
        return [record["samaccountname"] for record in results]
    
    def get_password_never_expires_users(self, domain: str) -> List[str]:
        query = """
        MATCH (u:User)
        WHERE u.enabled = true AND toLower(u.domain) = toLower($domain)
          AND u.pwdneverexpires = true
        RETURN u.samaccountname AS samaccountname
        """
        results = self.execute_query(query, domain=domain)
        return [record["samaccountname"] for record in results]
    
    def get_sessions(self, domain: str, da: bool = False) -> List[Dict]:
        """
        Get sessions in a domain.
        If da=True: returns computers with sessions from domain admin users (excluding DCs),
        along with the domain admin username.
        If da=False: returns computers with high-value user sessions.
        """
        if da:
            # Domain admin sessions - exclude DCs and return DA users on non-DC computers
            query = """
            MATCH (dc:Computer)-[r1:MemberOf*0..]->(g1:Group)
            WHERE g1.objectid =~ "S-1-5-.*-516" AND toLower(dc.domain) = toLower($domain)
            WITH COLLECT(dc) AS exclude
            MATCH (c:Computer)-[n:HasSession]->(u:User {enabled:true})
            WHERE NOT c IN exclude AND toLower(c.domain) = toLower($domain)
            AND ((u.highvalue = true OR EXISTS((u)-[:MemberOf*1..]->(:Group {highvalue:true}))))
            RETURN DISTINCT toLower(c.name) AS computer, toLower(u.samaccountname) AS domain_admin
            """
        else:
            # High-value user sessions
            query = """
            MATCH (c:Computer)-[n:HasSession]->(u:User {enabled:true})
            WHERE toLower(c.domain) = toLower($domain)
            AND ((u.highvalue = true OR EXISTS((u)-[:MemberOf*1..]->(:Group {highvalue:true}))))
            RETURN DISTINCT toLower(c.name) AS computer
            """
        return self.execute_query(query, domain=domain)
    
    def get_password_last_change(self, domain: str, user: Optional[str] = None) -> List[Dict]:
        if user:
            query = """
            MATCH (u:User)
            WHERE u.enabled = true AND toLower(u.domain) = toLower($domain)
              AND u.samaccountname = $user
            RETURN u.samaccountname AS samaccountname, u.pwdlastset AS pwdlastset, u.whencreated AS whencreated
            """
            params = {"domain": domain, "user": user}
        else:
            query = """
            MATCH (u:User)
            WHERE u.enabled = true AND toLower(u.domain) = toLower($domain)
            RETURN u.samaccountname AS samaccountname, u.pwdlastset AS pwdlastset, u.whencreated AS whencreated
            """
            params = {"domain": domain}
        return self.execute_query(query, **params)
    
    def get_critical_aces(self, source_domain: str, high_value: bool = False, 
                         username: str = "all", target_domain: str = "all", 
                         relation: str = "all") -> List[Dict]:
        """
        Queries ACLs for a specific user (source) with optional filtering on
        source and target domains. If high_value is True, only ACLs for high-value targets are returned.
        """
        # Build domain filters if not "all"
        username_filter = ""
        username_enabled = ""
        relation_filter = "[r1]"
        if relation.lower() != "all":
            relation_filter = "[r1:" + relation + "]"
        if username.lower() != "all":
            username_filter = " toLower(n.samaccountname) = toLower($samaccountname) AND "
        else:
            username_enabled = " {enabled: true}"
        target_filter = ""
        if target_domain.lower() != "all":
            target_filter = " AND toLower(m.domain) = toLower($target_domain) "

        query = """
        MATCH p=(n """ + username_enabled + """)-""" + relation_filter + """->(m)
        WHERE """ + username_filter + """
          r1.isacl = true
          """ + ("""AND ((m.highvalue = true OR EXISTS((m)-[:MemberOf*1..]->(:Group {highvalue:true}))))""" if high_value else "") + """
          AND toLower(n.domain) = toLower($source_domain)
          """ + ("""AND NOT ((n.highvalue = true OR EXISTS((n)-[:MemberOf*1..]->(:Group {highvalue:true}))))""" if username.lower() == "all" else "") + """
          """ + target_filter + """
        WITH n, m, r1,
             CASE 
                 WHEN 'User' IN labels(n) THEN 'User'
                 WHEN 'Group' IN labels(n) THEN 'Group'
                 WHEN 'Computer' IN labels(n) THEN 'Computer'
                 WHEN 'OU' IN labels(n) THEN 'OU'
                 WHEN 'GPO' IN labels(n) THEN 'GPO'
                 WHEN 'Domain' IN labels(n) THEN 'Domain'
                 ELSE 'Other'
             END AS sourceType,
             CASE 
                 WHEN 'User' IN labels(n) THEN n.samaccountname
                 WHEN 'Group' IN labels(n) THEN n.samaccountname
                 WHEN 'Computer' IN labels(n) THEN n.samaccountname
                 WHEN 'OU' IN labels(n) THEN n.distinguishedname
                 ELSE n.name
             END AS source,
             CASE 
                 WHEN 'User' IN labels(m) THEN 'User'
                 WHEN 'Group' IN labels(m) THEN 'Group'
                 WHEN 'Computer' IN labels(m) THEN 'Computer'
                 WHEN 'OU' IN labels(m) THEN 'OU'
                 WHEN 'GPO' IN labels(m) THEN 'GPO'
                 WHEN 'Domain' IN labels(m) THEN 'Domain'
                 ELSE 'Other'
             END AS targetType,
             CASE 
                 WHEN 'User' IN labels(m) THEN m.samaccountname
                 WHEN 'Group' IN labels(m) THEN m.samaccountname
                 WHEN 'Computer' IN labels(m) THEN m.samaccountname
                 WHEN 'OU' IN labels(m) THEN m.distinguishedname
                 ELSE m.name
             END AS target,
             CASE
                 WHEN n.domain IS NOT NULL THEN toLower(n.domain)
                 ELSE 'N/A'
             END AS sourceDomain,
             CASE
                 WHEN m.domain IS NOT NULL THEN toLower(m.domain)
                 ELSE 'N/A'
             END AS targetDomain
        RETURN DISTINCT {
            source: source,
            sourceType: sourceType,
            target: target,
            targetType: targetType,
            type: type(r1),
            sourceDomain: sourceDomain,
            targetDomain: targetDomain,
            targetEnabled: m.enabled
        } AS result
        UNION
        MATCH p=(n """ + username_enabled + """)-[:MemberOf*1..]->(g:Group)-""" + relation_filter + """->(m)
        WHERE """ + username_filter + """
          r1.isacl = true
          """ + ("""AND ((m.highvalue = true OR EXISTS((m)-[:MemberOf*1..]->(:Group {highvalue:true}))))""" if high_value else "") + """
          AND toLower(n.domain) = toLower($source_domain)
          """ + ("""AND NOT ((n.highvalue = true OR EXISTS((n)-[:MemberOf*1..]->(:Group {highvalue:true}))))""" if username.lower() == "all" else "") + """
          """ + target_filter + """
        WITH n, m, r1,
             CASE 
                 WHEN 'User' IN labels(n) THEN 'User'
                 WHEN 'Group' IN labels(n) THEN 'Group'
                 WHEN 'Computer' IN labels(n) THEN 'Computer'
                 WHEN 'OU' IN labels(n) THEN 'OU'
                 WHEN 'GPO' IN labels(n) THEN 'GPO'
                 WHEN 'Domain' IN labels(n) THEN 'Domain'
                 ELSE 'Other'
             END AS sourceType,
             CASE 
                 WHEN 'User' IN labels(n) THEN n.samaccountname
                 WHEN 'Group' IN labels(n) THEN n.samaccountname
                 WHEN 'Computer' IN labels(n) THEN n.samaccountname
                 WHEN 'OU' IN labels(n) THEN n.distinguishedname
                 ELSE n.name
             END AS source,
             CASE 
                 WHEN 'User' IN labels(m) THEN 'User'
                 WHEN 'Group' IN labels(m) THEN 'Group'
                 WHEN 'Computer' IN labels(m) THEN 'Computer'
                 WHEN 'OU' IN labels(m) THEN 'OU'
                 WHEN 'GPO' IN labels(m) THEN 'GPO'
                 WHEN 'Domain' IN labels(m) THEN 'Domain'
                 ELSE 'Other'
             END AS targetType,
             CASE 
                 WHEN 'User' IN labels(m) THEN m.samaccountname
                 WHEN 'Group' IN labels(m) THEN m.samaccountname
                 WHEN 'Computer' IN labels(m) THEN m.samaccountname
                 WHEN 'OU' IN labels(m) THEN m.distinguishedname
                 ELSE m.name
             END AS target,
             CASE
                 WHEN n.domain IS NOT NULL THEN toLower(n.domain)
                 ELSE 'N/A'
             END AS sourceDomain,
             CASE
                 WHEN m.domain IS NOT NULL THEN toLower(m.domain)
                 ELSE 'N/A'
             END AS targetDomain
        RETURN DISTINCT {
            source: source,
            sourceType: sourceType,
            target: target,
            targetType: targetType,
            type: type(r1),
            sourceDomain: sourceDomain,
            targetDomain: targetDomain,
            targetEnabled: m.enabled
        } AS result
        """
        return [r["result"] for r in self.execute_query(query,
                                                         samaccountname=username,
                                                         source_domain=source_domain,
                                                         target_domain=target_domain,
                                                         relation=relation)]
    
    def get_access_paths(self, source: str, connection: str, target: str, domain: str) -> List[Dict]:
        """
        Constructs and executes a dynamic query based on the following cases:
        1. If source is not "all" and target is "all":
            - Filters the start node by samaccountname and domain (both case-insensitively).
        2. If source is "all" and target is "all":
            - Returns all start nodes from the specified domain with enabled:true and no admincount.
        3. If source is not "all" and target is "dcs":
            - Filters the start node by samaccountname and domain (case-insensitively) and adds additional filtering for DCs.
        The relationship type in the query is set based on the provided 'connection' parameter.
        """
        # Determine if we use the generic relationship with type IN (...) or a specific one.
        if connection.lower() == "all":
            rel_condition = "AND type(r) IN ['AdminTo','CanRDP','CanPSRemote']"
            rel_pattern = "[r]->"  # Generic relationship without type-template
        else:
            rel_condition = ""
            rel_pattern = f"[r:{connection}]->"
            
        if source.lower() != "all" and target.lower() == "all":
            # Specific source, all targets
            query = f"""
            MATCH p = (n)-{rel_pattern}(m)
            WHERE toLower(n.samaccountname) = toLower($source)
            AND toLower(n.domain) = toLower($domain)
            AND m.enabled = true
            {rel_condition}
            RETURN {{source: n.samaccountname, target: m.samaccountname, type: type(r)}} AS result
            """
            params = {"source": source, "domain": domain}
        elif source.lower() == "all" and target.lower() == "all":
            # All sources, all targets
            query = f"""
            MATCH p = (n)-{rel_pattern}(m)
            WHERE n.enabled = true
            AND toLower(n.domain) = toLower($domain)
            AND NOT ((n.highvalue = true OR EXISTS((n)-[:MemberOf*1..]->(:Group {{highvalue:true}}))))
            AND m.enabled = true
            {rel_condition}
            RETURN {{source: n.samaccountname, target: m.samaccountname, type: type(r)}} AS result
            """
            params = {"domain": domain}
        elif source.lower() == "all" and target.lower() == "dcs":
            # All sources, DC targets
            query = f"""
            MATCH p = (n)-{rel_pattern}(m)
            WHERE n.enabled = true
            AND toLower(n.domain) = toLower($domain)
            AND m.enabled = true
            {rel_condition}
            AND (n.admincount IS NULL OR n.admincount = false)
            AND EXISTS {{
                MATCH (m)-[:MemberOf]->(dc:Group)
                WHERE dc.objectid =~ '(?i)S-1-5-.*-516'
            }}
            RETURN {{source: n.samaccountname, target: m.samaccountname, type: type(r)}} AS result
            """
            params = {"domain": domain}
        else:
            return []
        return self.execute_query(query, **params)
    
    def get_critical_aces_by_domain(self, domain: str, blacklist: List[str], 
                                   high_value: bool = False) -> List[Dict]:
        """Get critical ACEs by domain with optional blacklist and high-value filtering"""
        query = """
        MATCH p=(n)-[r1]->(m)
        WHERE r1.isacl = true
          AND toUpper(n.domain) = toUpper($domain)
          AND toUpper(n.domain) <> toUpper(m.domain)
          AND (size($blacklist) = 0 OR NOT toUpper(m.domain) IN $blacklist)
          """ + ("""AND m.highvalue = true""" if high_value else "") + """
        WITH n, m, r1,
             CASE 
                 WHEN 'User' IN labels(n) THEN 'User'
                 WHEN 'Group' IN labels(n) THEN 'Group'
                 WHEN 'Computer' IN labels(n) THEN 'Computer'
                 WHEN 'OU' IN labels(n) THEN 'OU'
                 WHEN 'GPO' IN labels(n) THEN 'GPO'
                 WHEN 'Domain' IN labels(n) THEN 'Domain'
                 ELSE 'Other'
             END AS sourceType,
             CASE 
                 WHEN 'User' IN labels(n) THEN n.samaccountname
                 WHEN 'Group' IN labels(n) THEN n.samaccountname
                 WHEN 'Computer' IN labels(n) THEN n.samaccountname
                 WHEN 'OU' IN labels(n) THEN n.distinguishedname
                 ELSE n.name
             END AS source,
             CASE 
                 WHEN 'User' IN labels(m) THEN 'User'
                 WHEN 'Group' IN labels(m) THEN 'Group'
                 WHEN 'Computer' IN labels(m) THEN 'Computer'
                 WHEN 'OU' IN labels(m) THEN 'OU'
                 WHEN 'GPO' IN labels(m) THEN 'GPO'
                 WHEN 'Domain' IN labels(m) THEN 'Domain'
                 ELSE 'Other'
             END AS targetType,
             CASE 
                 WHEN 'User' IN labels(m) THEN m.samaccountname
                 WHEN 'Group' IN labels(m) THEN m.samaccountname
                 WHEN 'Computer' IN labels(m) THEN m.samaccountname
                 WHEN 'OU' IN labels(m) THEN m.distinguishedname
                 ELSE m.name
             END AS target,
             CASE
                 WHEN n.domain IS NOT NULL THEN toLower(n.domain)
                 ELSE 'N/A'
             END AS sourceDomain,
             CASE
                 WHEN m.domain IS NOT NULL THEN toLower(m.domain)
                 ELSE 'N/A'
             END AS targetDomain
        RETURN DISTINCT {
            source: source,
            sourceType: sourceType,
            target: target,
            targetType: targetType,
            type: type(r1),
            sourceDomain: sourceDomain,
            targetDomain: targetDomain,
            targetEnabled: m.enabled
        } AS result
        UNION
        MATCH p=(n)-[:MemberOf*1..]->(g:Group)-[r1]->(m)
        WHERE r1.isacl = true
          AND toUpper(n.domain) = toUpper($domain)
          AND toUpper(n.domain) <> toUpper(m.domain)
          AND (size($blacklist) = 0 OR NOT toUpper(m.domain) IN $blacklist)
          """ + ("""AND m.highvalue = true""" if high_value else "") + """
        WITH n, m, r1,
             CASE 
                 WHEN 'User' IN labels(n) THEN 'User'
                 WHEN 'Group' IN labels(n) THEN 'Group'
                 WHEN 'Computer' IN labels(n) THEN 'Computer'
                 WHEN 'OU' IN labels(n) THEN 'OU'
                 WHEN 'GPO' IN labels(n) THEN 'GPO'
                 WHEN 'Domain' IN labels(n) THEN 'Domain'
                 ELSE 'Other'
             END AS sourceType,
             CASE 
                 WHEN 'User' IN labels(n) THEN n.samaccountname
                 WHEN 'Group' IN labels(n) THEN n.samaccountname
                 WHEN 'Computer' IN labels(n) THEN n.samaccountname
                 WHEN 'OU' IN labels(n) THEN n.distinguishedname
                 ELSE n.name
             END AS source,
             CASE 
                 WHEN 'User' IN labels(m) THEN 'User'
                 WHEN 'Group' IN labels(m) THEN 'Group'
                 WHEN 'Computer' IN labels(m) THEN 'Computer'
                 WHEN 'OU' IN labels(m) THEN 'OU'
                 WHEN 'GPO' IN labels(m) THEN 'GPO'
                 WHEN 'Domain' IN labels(m) THEN 'Domain'
                 ELSE 'Other'
             END AS targetType,
             CASE 
                 WHEN 'User' IN labels(m) THEN m.samaccountname
                 WHEN 'Group' IN labels(m) THEN m.samaccountname
                 WHEN 'Computer' IN labels(m) THEN m.samaccountname
                 WHEN 'OU' IN labels(m) THEN m.distinguishedname
                 ELSE m.name
             END AS target,
             CASE
                 WHEN n.domain IS NOT NULL THEN toLower(n.domain)
                 ELSE 'N/A'
             END AS sourceDomain,
             CASE
                 WHEN m.domain IS NOT NULL THEN toLower(m.domain)
                 ELSE 'N/A'
             END AS targetDomain
        RETURN DISTINCT {
            source: source,
            sourceType: sourceType,
            target: target,
            targetType: targetType,
            type: type(r1),
            sourceDomain: sourceDomain,
            targetDomain: targetDomain,
            targetEnabled: m.enabled
        } AS result
        """
        results = self.execute_query(query, domain=domain.upper(), blacklist=[d.upper() for d in blacklist])
        return [r["result"] for r in results]
    
    def close(self):
        """Close the Neo4j driver"""
        if hasattr(self, 'driver'):
            self.driver.close()
