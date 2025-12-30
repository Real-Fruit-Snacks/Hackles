# Find ALL users and show their owned-related properties
MATCH (u:User)
RETURN u.name AS name,
       u.system_tags AS system_tags,
       u.owned AS owned,
       labels(u) AS labels
ORDER BY u.name
LIMIT 50
